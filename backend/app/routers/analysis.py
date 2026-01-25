"""
Analysis router - retrieve analysis results and manage transactions.

GET /api/status/{id} - Check processing status
GET /api/analysis/{id} - Get complete analysis with insights
PATCH /api/transactions/{id} - Update a transaction's category
GET /api/categories - Get list of valid categories
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.database import Statement, Transaction, Insight, get_db
from app.models.schemas import (
    StatementStatus,
    FullAnalysisResponse,
    AnalysisSummary,
    SpendingByCategory,
    TransactionResponse,
    TransactionUpdate,
    InsightResponse,
    StatementResponse,
    ValidCategories
)


router = APIRouter(prefix="/api", tags=["analysis"])


@router.get("/status/{statement_id}", response_model=StatementStatus)
def get_status(statement_id: int, db: Session = Depends(get_db)) -> StatementStatus:
    """
    Check the processing status of a statement.

    Useful for polling during async processing (Phase 2+).
    For now with sync processing, status will be 'completed' or 'failed'.
    """
    statement = db.query(Statement).filter(Statement.id == statement_id).first()

    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found")

    return StatementStatus.model_validate(statement)


@router.get("/analysis/{statement_id}", response_model=FullAnalysisResponse)
def get_analysis(statement_id: int, db: Session = Depends(get_db)) -> FullAnalysisResponse:
    """
    Get the complete analysis for a statement.

    Returns:
    - Statement metadata
    - Summary statistics
    - Spending breakdown by category
    - All transactions
    - AI-generated insights
    """
    # Get statement
    statement = db.query(Statement).filter(Statement.id == statement_id).first()

    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found")

    if statement.status == "processing":
        raise HTTPException(
            status_code=202,
            detail="Statement is still being processed. Please try again later."
        )

    if statement.status == "failed":
        raise HTTPException(
            status_code=400,
            detail=f"Statement processing failed: {statement.error_message}"
        )

    # Get all transactions
    transactions = db.query(Transaction).filter(
        Transaction.statement_id == statement_id
    ).order_by(Transaction.date.desc()).all()

    # Get all insights
    insights = db.query(Insight).filter(
        Insight.statement_id == statement_id
    ).all()

    # Calculate spending by category
    # Using SQLAlchemy aggregation for efficiency
    category_stats = db.query(
        Transaction.category,
        func.sum(Transaction.amount).label("total"),
        func.count(Transaction.id).label("count")
    ).filter(
        Transaction.statement_id == statement_id,
        Transaction.amount < 0  # Only spending (negative amounts)
    ).group_by(
        Transaction.category
    ).all()

    # Calculate percentages
    total_spent = statement.total_spent or 0.01  # Avoid division by zero
    spending_by_category = [
        SpendingByCategory(
            category=stat.category,
            total=abs(stat.total),  # Make positive for display
            count=stat.count,
            percentage=round((abs(stat.total) / total_spent) * 100, 1)
        )
        for stat in category_stats
    ]

    # Sort by total (highest first)
    spending_by_category.sort(key=lambda x: x.total, reverse=True)

    # Count transactions needing review
    needs_review_count = sum(1 for t in transactions if t.needs_review)

    # Build summary
    summary = AnalysisSummary(
        total_transactions=statement.total_transactions,
        total_spent=statement.total_spent,
        total_income=statement.total_income,
        net_change=statement.total_income - statement.total_spent,
        period_start=statement.period_start,
        period_end=statement.period_end,
        detected_format=statement.detected_format
    )

    return FullAnalysisResponse(
        statement=StatementResponse.model_validate(statement),
        summary=summary,
        spending_by_category=spending_by_category,
        transactions=[TransactionResponse.model_validate(t) for t in transactions],
        insights=[InsightResponse.model_validate(i) for i in insights],
        needs_review_count=needs_review_count
    )


@router.patch("/transactions/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    update: TransactionUpdate,
    db: Session = Depends(get_db)
) -> TransactionResponse:
    """
    Update a transaction's category or merchant.

    Used when user corrects an AI-categorized transaction.
    This feedback could be used for model improvement in the future.
    """
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Apply updates (only non-None fields)
    update_data = update.model_dump(exclude_unset=True, exclude_none=True)

    if "category" in update_data:
        # Validate category
        if update_data["category"] not in settings.VALID_CATEGORIES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category. Valid categories: {settings.VALID_CATEGORIES}"
            )
        transaction.category = update_data["category"]
        transaction.category_confidence = 1.0  # User-confirmed
        transaction.needs_review = False

    if "merchant" in update_data:
        transaction.merchant = update_data["merchant"]

    if "is_recurring" in update_data:
        transaction.is_recurring = update_data["is_recurring"]

    db.commit()
    db.refresh(transaction)

    return TransactionResponse.model_validate(transaction)


@router.get("/categories", response_model=ValidCategories)
def get_categories() -> ValidCategories:
    """
    Get the list of valid transaction categories.

    Useful for populating category dropdowns in the UI.
    """
    return ValidCategories(categories=settings.VALID_CATEGORIES)
