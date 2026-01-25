"""
Upload router - handles statement file uploads and processing.

POST /api/upload - Upload and process a statement file

Since processing is synchronous for now, this endpoint:
1. Receives the file
2. Parses it (auto-detecting format)
3. Stores transactions in the database
4. Returns immediately with the statement ID

Later phases will add LLM categorization and analysis here.
"""

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.database import Statement, Transaction, get_db
from app.models.schemas import UploadResponse
from app.services.parser import parse_statement


router = APIRouter(prefix="/api", tags=["upload"])

# Directory for storing uploaded files (optional, for debugging)
UPLOAD_DIR = Path("uploads")


@router.post("/upload", response_model=UploadResponse)
def upload_statement(
    file: UploadFile = File(..., description="CSV statement file"),
    db: Session = Depends(get_db)
) -> UploadResponse:
    """
    Upload a bank/credit card statement for analysis.

    Accepts CSV files from supported banks (Bank of America, Discover).
    The format is auto-detected from the column headers.

    Returns:
        UploadResponse with statement_id for subsequent queries
    """
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported. Please upload a .csv file."
        )

    # Read file content
    try:
        content = file.file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")

    # Generate unique filename for storage
    unique_filename = f"{uuid.uuid4().hex}_{file.filename}"

    # Create statement record (status: pending)
    statement = Statement(
        filename=unique_filename,
        original_filename=file.filename,
        status="processing"
    )
    db.add(statement)
    db.commit()
    db.refresh(statement)

    # Parse the statement
    parse_result = parse_statement(content)

    if not parse_result.success:
        # Update statement with error
        statement.status = "failed"
        statement.error_message = parse_result.error_message
        db.commit()

        return UploadResponse(
            success=False,
            message="Failed to parse statement",
            statement_id=statement.id,
            error=parse_result.error_message
        )

    # Store parsed transactions
    total_spent = 0.0
    total_income = 0.0

    for parsed_tx in parse_result.transactions:
        # Track totals
        if parsed_tx.amount < 0:
            total_spent += abs(parsed_tx.amount)
        else:
            total_income += parsed_tx.amount

        # Create transaction record
        transaction = Transaction(
            statement_id=statement.id,
            date=parsed_tx.date,
            description=parsed_tx.description,
            amount=parsed_tx.amount,
            # Category will be set by LLM in Phase 2
            # For now, use original_category if available, otherwise "other"
            category=parsed_tx.original_category.lower() if parsed_tx.original_category else "other",
            category_confidence=0.5 if parsed_tx.original_category else 0.0,
            needs_review=parsed_tx.original_category is None  # Flag for LLM categorization
        )
        db.add(transaction)

    # Update statement with results
    statement.status = "completed"  # Will change to "pending_analysis" in Phase 2
    statement.detected_format = parse_result.format_name
    statement.total_transactions = len(parse_result.transactions)
    statement.total_spent = round(total_spent, 2)
    statement.total_income = round(total_income, 2)
    statement.period_start = parse_result.period_start
    statement.period_end = parse_result.period_end

    db.commit()

    # Optionally save the original file for debugging
    if settings.DEBUG:
        UPLOAD_DIR.mkdir(exist_ok=True)
        (UPLOAD_DIR / unique_filename).write_bytes(content)

    return UploadResponse(
        success=True,
        message=f"Successfully parsed {len(parse_result.transactions)} transactions from {parse_result.format_name} statement",
        statement_id=statement.id
    )


@router.get("/formats")
def get_supported_formats():
    """
    Get list of supported statement formats.

    Useful for displaying supported formats in the UI.
    """
    from app.services.parser import get_supported_formats
    return {"formats": get_supported_formats()}
