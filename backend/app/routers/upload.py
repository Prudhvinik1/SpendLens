"""
Upload router - handles statement file uploads and processing.

POST /api/upload - Upload and process a statement file

Processing flow (synchronous):
1. Receives the file
2. Parses it (auto-detecting format)
3. Categorizes transactions via LLM (batched)
4. Stores everything in the database
5. Returns with the statement ID
"""

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.database import Statement, Transaction, get_db
from app.models.schemas import UploadResponse
from app.services.parser import parse_statement
from app.services.categorizer import categorize_transactions


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

    # Prepare transactions for LLM categorization
    transactions_for_llm = [
        {
            "description": tx.description,
            "amount": tx.amount
        }
        for tx in parse_result.transactions
    ]

    # Categorize using LLM (batched, traced via Opik)
    print(f"Categorizing {len(transactions_for_llm)} transactions via LLM...")
    categorization_results = categorize_transactions(
        transactions_for_llm,
        statement_id=statement.id
    )

    # Create a lookup for categorization results by index
    cat_by_index = {r.index: r for r in categorization_results}

    # Store parsed transactions with LLM categories
    total_spent = 0.0
    total_income = 0.0

    for idx, parsed_tx in enumerate(parse_result.transactions):
        # Track totals
        if parsed_tx.amount < 0:
            total_spent += abs(parsed_tx.amount)
        else:
            total_income += parsed_tx.amount

        # Get LLM categorization result
        cat_result = cat_by_index.get(idx)

        if cat_result:
            category = cat_result.category
            confidence = cat_result.confidence
            merchant = cat_result.merchant
            needs_review = cat_result.needs_review
        else:
            # Fallback if LLM didn't return result for this index
            category = parsed_tx.original_category.lower() if parsed_tx.original_category else "other"
            confidence = 0.5 if parsed_tx.original_category else 0.0
            merchant = parsed_tx.description
            needs_review = True

        # Create transaction record
        transaction = Transaction(
            statement_id=statement.id,
            date=parsed_tx.date,
            description=parsed_tx.description,
            merchant=merchant,
            amount=parsed_tx.amount,
            category=category,
            category_confidence=confidence,
            needs_review=needs_review
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

    # Count how many need review
    needs_review_count = sum(1 for r in categorization_results if r.needs_review)

    return UploadResponse(
        success=True,
        message=f"Processed {len(parse_result.transactions)} transactions ({needs_review_count} need review)",
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
