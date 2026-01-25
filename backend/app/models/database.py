"""
SQLAlchemy database models using SQLAlchemy 2.0 style.

Key patterns:
1. `Mapped[type]` provides type hints for columns
2. `mapped_column()` replaces the old Column() with better defaults
3. `relationship()` with `back_populates` creates bidirectional references
4. We use a sync engine since the processing is synchronous for now
"""

from datetime import datetime, date
from typing import Optional

from sqlalchemy import (
    create_engine, ForeignKey, String, Text, Float, Boolean, Date, DateTime, Enum
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
)

from app.core.config import settings


# Base class for all models
class Base(DeclarativeBase):
    """Base class that all models inherit from."""
    pass


class Statement(Base):
    """
    Represents an uploaded bank/credit card statement.

    Lifecycle: pending -> processing -> completed/failed
    """
    __tablename__ = "statements"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(255))
    original_filename: Mapped[str] = mapped_column(String(255))  # User's filename
    upload_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Date range of transactions in this statement
    period_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    period_end: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Aggregated stats (computed after processing)
    total_transactions: Mapped[int] = mapped_column(default=0)
    total_spent: Mapped[float] = mapped_column(Float, default=0.0)
    total_income: Mapped[float] = mapped_column(Float, default=0.0)

    # Processing status
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending"  # pending, processing, completed, failed
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Detected statement format
    detected_format: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationships
    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="statement",
        cascade="all, delete-orphan"  # Delete transactions when statement is deleted
    )
    insights: Mapped[list["Insight"]] = relationship(
        back_populates="statement",
        cascade="all, delete-orphan"
    )


class Transaction(Base):
    """
    Individual transaction from a statement.

    Note on amount convention:
    - Negative = money spent (outflow)
    - Positive = money received (income)
    """
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    statement_id: Mapped[int] = mapped_column(ForeignKey("statements.id"))

    # Core transaction data
    date: Mapped[date] = mapped_column(Date)
    description: Mapped[str] = mapped_column(Text)  # Original description from bank
    merchant: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Normalized name
    amount: Mapped[float] = mapped_column(Float)

    # LLM-assigned category
    category: Mapped[str] = mapped_column(String(50), default="other")
    category_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    needs_review: Mapped[bool] = mapped_column(Boolean, default=False)  # Low confidence flag

    # Pattern detection
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    is_anomaly: Mapped[bool] = mapped_column(Boolean, default=False)
    anomaly_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationship back to statement
    statement: Mapped["Statement"] = relationship(back_populates="transactions")


class Insight(Base):
    """
    AI-generated insights about spending patterns.

    Types:
    - subscription: Detected recurring charge
    - anomaly: Unusual transaction
    - trend: Spending pattern observation
    - tip: Actionable savings suggestion
    """
    __tablename__ = "insights"

    id: Mapped[int] = mapped_column(primary_key=True)
    statement_id: Mapped[int] = mapped_column(ForeignKey("statements.id"))

    # Insight content
    type: Mapped[str] = mapped_column(String(50))  # subscription, anomaly, trend, tip
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)

    # Context
    severity: Mapped[str] = mapped_column(String(20), default="info")  # info, warning, alert
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    action_suggestion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationship
    statement: Mapped["Statement"] = relationship(back_populates="insights")


# Database engine and session factory
# Using check_same_thread=False for SQLite to work with FastAPI
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.DEBUG  # Log SQL queries in debug mode
)

# Session factory - call SessionLocal() to get a new session
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def init_db() -> None:
    """Create all tables. Call this on app startup."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """
    Dependency for FastAPI endpoints.

    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...

    The `yield` makes this a context manager - the finally block
    always runs, ensuring we close the session even if there's an error.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
