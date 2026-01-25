"""
Pydantic schemas for API request/response validation.

Key distinction:
- SQLAlchemy models (database.py) = how data is stored in the database
- Pydantic schemas (this file) = how data is validated and serialized for API

Naming convention:
- XxxBase: Common fields shared across operations
- XxxCreate: Fields needed when creating a new resource
- XxxUpdate: Fields that can be updated (usually all Optional)
- XxxResponse: Fields returned in API responses
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.core.config import settings


# ============== Transaction Schemas ==============

class TransactionBase(BaseModel):
    """Base transaction fields."""
    date: date
    description: str
    amount: float
    merchant: Optional[str] = None
    category: str = "other"


class TransactionResponse(TransactionBase):
    """Transaction as returned in API responses."""
    id: int
    statement_id: int
    category_confidence: float = 0.0
    needs_review: bool = False
    is_recurring: bool = False
    is_anomaly: bool = False
    anomaly_reason: Optional[str] = None

    # This allows Pydantic to read from SQLAlchemy model attributes
    model_config = ConfigDict(from_attributes=True)


class TransactionUpdate(BaseModel):
    """
    Fields that can be updated on a transaction.

    All fields optional - only provided fields will be updated.
    This is the PATCH semantics.
    """
    category: Optional[str] = Field(
        default=None,
        description="New category for the transaction"
    )
    merchant: Optional[str] = Field(
        default=None,
        description="Corrected merchant name"
    )
    is_recurring: Optional[bool] = Field(
        default=None,
        description="Mark as recurring subscription"
    )

    def model_post_init(self, __context) -> None:
        """Validate category if provided."""
        if self.category is not None and self.category not in settings.VALID_CATEGORIES:
            raise ValueError(
                f"Invalid category: {self.category}. "
                f"Valid categories: {settings.VALID_CATEGORIES}"
            )


# ============== Insight Schemas ==============

class InsightResponse(BaseModel):
    """Insight as returned in API responses."""
    id: int
    statement_id: int
    type: str  # subscription, anomaly, trend, tip
    title: str
    description: str
    severity: str = "info"  # info, warning, alert
    category: Optional[str] = None
    amount: Optional[float] = None
    action_suggestion: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ============== Statement Schemas ==============

class StatementBase(BaseModel):
    """Base statement fields."""
    filename: str
    original_filename: str


class StatementResponse(BaseModel):
    """Statement summary as returned in API responses."""
    id: int
    filename: str
    original_filename: str
    upload_date: datetime
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    total_transactions: int = 0
    total_spent: float = 0.0
    total_income: float = 0.0
    status: str = "pending"
    error_message: Optional[str] = None
    detected_format: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class StatementStatus(BaseModel):
    """Lightweight status check response."""
    id: int
    status: str
    error_message: Optional[str] = None
    total_transactions: int = 0

    model_config = ConfigDict(from_attributes=True)


# ============== Upload Response ==============

class UploadResponse(BaseModel):
    """Response after uploading a statement."""
    success: bool
    message: str
    statement_id: Optional[int] = None
    error: Optional[str] = None


# ============== Analysis Response ==============

class SpendingByCategory(BaseModel):
    """Spending breakdown for a single category."""
    category: str
    total: float
    count: int
    percentage: float


class AnalysisSummary(BaseModel):
    """Summary statistics for the analysis."""
    total_transactions: int
    total_spent: float
    total_income: float
    net_change: float
    period_start: Optional[date]
    period_end: Optional[date]
    detected_format: Optional[str]


class FullAnalysisResponse(BaseModel):
    """
    Complete analysis response including all data.

    This is the main response for GET /api/analysis/{id}
    """
    statement: StatementResponse
    summary: AnalysisSummary
    spending_by_category: list[SpendingByCategory]
    transactions: list[TransactionResponse]
    insights: list[InsightResponse]
    needs_review_count: int = Field(
        description="Number of transactions flagged for user review"
    )


# ============== Utility Schemas ==============

class SupportedFormat(BaseModel):
    """Information about a supported statement format."""
    name: str
    id: str
    columns: str


class ValidCategories(BaseModel):
    """List of valid transaction categories."""
    categories: list[str]
