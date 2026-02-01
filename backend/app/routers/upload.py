"""
Upload router - handles statement file uploads and processing.

POST /api/upload - Upload and process a statement file

Processing flow (synchronous):
1. Receives the file
2. Parses it (auto-detecting format)
3. Categorizes transactions via LLM (batched)
4. Stores transactions in database
5. Runs analysis (subscriptions, anomalies, insights)
6. Returns with the statement ID
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
from app.services.analyzer import analyze_statement


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

    # Run analysis (subscriptions, anomalies, insights)
    print("Running analysis...")
    try:
        analysis_result = analyze_statement(db, statement.id)
        insights_count = len(analysis_result.insights)
        subscriptions_count = len(analysis_result.subscriptions)
    except Exception as e:
        print(f"Analysis failed: {e}")
        insights_count = 0
        subscriptions_count = 0

    # Count how many need review
    needs_review_count = sum(1 for r in categorization_results if r.needs_review)

    return UploadResponse(
        success=True,
        message=f"Processed {len(parse_result.transactions)} transactions, found {subscriptions_count} subscriptions, generated {insights_count} insights",
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


# Path to sample data (relative to backend directory)
SAMPLE_DATA_DIR = Path(__file__).parent.parent.parent.parent / "sample_data"


@router.get("/sample-data")
def list_sample_data():
    """
    List available sample data files for demo.
    """
    samples = []
    if SAMPLE_DATA_DIR.exists():
        for file in SAMPLE_DATA_DIR.glob("*.csv"):
            samples.append({
                "name": file.stem.replace("sample_", "").replace("_", " ").title(),
                "filename": file.name,
                "id": file.stem
            })
    return {"samples": samples}


@router.post("/demo/{sample_id}", response_model=UploadResponse)
def process_demo_data(
    sample_id: str,
    db: Session = Depends(get_db)
) -> UploadResponse:
    """
    Process sample demo data without requiring file upload.

    This allows the "Try with sample data" feature to work.
    Sample IDs: sample_bofa, sample_discover
    """
    # Find the sample file
    sample_file = SAMPLE_DATA_DIR / f"{sample_id}.csv"

    if not sample_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Sample data '{sample_id}' not found. Available: sample_bofa, sample_discover"
        )

    # Read sample file
    content = sample_file.read_bytes()

    # Create statement record
    statement = Statement(
        filename=f"demo_{sample_id}.csv",
        original_filename=f"{sample_id}.csv",
        status="processing"
    )
    db.add(statement)
    db.commit()
    db.refresh(statement)

    # Parse the statement
    parse_result = parse_statement(content)

    if not parse_result.success:
        statement.status = "failed"
        statement.error_message = parse_result.error_message
        db.commit()

        return UploadResponse(
            success=False,
            message="Failed to parse sample data",
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

    # Categorize using LLM
    print(f"[DEMO] Categorizing {len(transactions_for_llm)} transactions via LLM...")
    categorization_results = categorize_transactions(
        transactions_for_llm,
        statement_id=statement.id
    )

    # Create lookup for categorization results
    cat_by_index = {r.index: r for r in categorization_results}

    # Store transactions
    total_spent = 0.0
    total_income = 0.0

    for idx, parsed_tx in enumerate(parse_result.transactions):
        if parsed_tx.amount < 0:
            total_spent += abs(parsed_tx.amount)
        else:
            total_income += parsed_tx.amount

        cat_result = cat_by_index.get(idx)

        if cat_result:
            category = cat_result.category
            confidence = cat_result.confidence
            merchant = cat_result.merchant
            needs_review = cat_result.needs_review
        else:
            category = parsed_tx.original_category.lower() if parsed_tx.original_category else "other"
            confidence = 0.5 if parsed_tx.original_category else 0.0
            merchant = parsed_tx.description
            needs_review = True

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

    # Update statement
    statement.status = "completed"
    statement.detected_format = parse_result.format_name
    statement.total_transactions = len(parse_result.transactions)
    statement.total_spent = round(total_spent, 2)
    statement.total_income = round(total_income, 2)
    statement.period_start = parse_result.period_start
    statement.period_end = parse_result.period_end

    db.commit()

    # Run analysis
    print("[DEMO] Running analysis...")
    try:
        analysis_result = analyze_statement(db, statement.id)
        insights_count = len(analysis_result.insights)
        subscriptions_count = len(analysis_result.subscriptions)
    except Exception as e:
        print(f"[DEMO] Analysis failed: {e}")
        insights_count = 0
        subscriptions_count = 0

    return UploadResponse(
        success=True,
        message=f"Demo: Processed {len(parse_result.transactions)} transactions, found {subscriptions_count} subscriptions, generated {insights_count} insights",
        statement_id=statement.id
    )
