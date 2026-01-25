"""
Analyzer service - orchestrates the full analysis pipeline.

Pipeline:
1. Detect subscriptions
2. Detect anomalies
3. Calculate spending by category and top merchants
4. Generate insights via LLM

This is the main entry point for analyzing a statement after categorization.
"""

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.models.database import Statement, Transaction, Insight
from app.services.subscriptions import (
    detect_subscriptions,
    TransactionInfo,
    SubscriptionMatch
)
from app.services.anomalies import (
    detect_anomalies,
    TransactionForAnomaly,
    AnomalyResult
)
from app.services.insights import (
    generate_insights,
    SpendingSummary,
    GeneratedInsight
)


@dataclass
class AnalysisResult:
    """Complete analysis result."""
    subscriptions: list[SubscriptionMatch]
    anomalies: list[AnomalyResult]
    insights: list[GeneratedInsight]
    top_merchants: list[dict]
    category_breakdown: list[dict]


def analyze_statement(
    db: Session,
    statement_id: int
) -> AnalysisResult:
    """
    Run full analysis on a statement.

    This should be called after transactions have been categorized.

    Args:
        db: Database session
        statement_id: ID of the statement to analyze

    Returns:
        AnalysisResult with all detected patterns and insights
    """
    # Get statement and transactions
    statement = db.query(Statement).filter(Statement.id == statement_id).first()
    if not statement:
        raise ValueError(f"Statement {statement_id} not found")

    transactions = db.query(Transaction).filter(
        Transaction.statement_id == statement_id
    ).all()

    if not transactions:
        return AnalysisResult(
            subscriptions=[],
            anomalies=[],
            insights=[],
            top_merchants=[],
            category_breakdown=[]
        )

    print(f"Analyzing {len(transactions)} transactions for statement {statement_id}...")

    # 1. Detect subscriptions
    sub_tx_info = [
        TransactionInfo(
            id=t.id,
            merchant=t.merchant or "",
            description=t.description,
            amount=t.amount,
            date=t.date
        )
        for t in transactions
    ]
    subscriptions = detect_subscriptions(sub_tx_info)
    print(f"  Found {len(subscriptions)} subscriptions")

    # Mark subscription transactions in database
    subscription_tx_ids = set()
    for sub in subscriptions:
        subscription_tx_ids.update(sub.transaction_ids)

    for tx in transactions:
        if tx.id in subscription_tx_ids:
            tx.is_recurring = True

    # 2. Detect anomalies
    anomaly_tx_info = [
        TransactionForAnomaly(
            id=t.id,
            merchant=t.merchant or "",
            description=t.description,
            amount=t.amount,
            category=t.category
        )
        for t in transactions
    ]
    anomalies = detect_anomalies(anomaly_tx_info)
    print(f"  Found {len(anomalies)} anomalies")

    # Mark anomaly transactions in database
    for anomaly in anomalies:
        tx = next((t for t in transactions if t.id == anomaly.transaction_id), None)
        if tx:
            tx.is_anomaly = True
            tx.anomaly_reason = anomaly.reason

    # 3. Calculate category breakdown
    category_breakdown = _calculate_category_breakdown(transactions)

    # 4. Calculate top merchants
    top_merchants = _calculate_top_merchants(transactions)

    # 5. Generate insights
    summary = SpendingSummary(
        period_start=statement.period_start,
        period_end=statement.period_end,
        total_spent=statement.total_spent,
        total_income=statement.total_income,
        categories=category_breakdown,
        subscriptions=[
            {
                "merchant": s.merchant,
                "average_amount": s.average_amount,
                "frequency": s.frequency
            }
            for s in subscriptions
        ],
        anomalies=[
            {
                "reason": a.reason,
                "severity": a.severity
            }
            for a in anomalies
        ],
        top_merchants=top_merchants
    )

    insights = generate_insights(summary, statement_id=statement_id)
    print(f"  Generated {len(insights)} insights")

    # 6. Save insights to database
    for insight in insights:
        db_insight = Insight(
            statement_id=statement_id,
            type=insight.type,
            title=insight.title,
            description=insight.description,
            severity=insight.severity,
            category=insight.category,
            amount=insight.amount,
            action_suggestion=insight.action_suggestion
        )
        db.add(db_insight)

    # Commit all changes
    db.commit()

    return AnalysisResult(
        subscriptions=subscriptions,
        anomalies=anomalies,
        insights=insights,
        top_merchants=top_merchants,
        category_breakdown=category_breakdown
    )


def _calculate_category_breakdown(transactions: list) -> list[dict]:
    """Calculate spending breakdown by category."""
    category_totals: dict[str, float] = defaultdict(float)
    category_counts: dict[str, int] = defaultdict(int)

    total_spending = 0.0

    for tx in transactions:
        if tx.amount < 0:  # Only spending
            amount = abs(tx.amount)
            category_totals[tx.category] += amount
            category_counts[tx.category] += 1
            total_spending += amount

    if total_spending == 0:
        return []

    breakdown = []
    for category, total in category_totals.items():
        breakdown.append({
            "category": category,
            "total": round(total, 2),
            "count": category_counts[category],
            "percentage": round((total / total_spending) * 100, 1)
        })

    # Sort by total (highest first)
    breakdown.sort(key=lambda x: x["total"], reverse=True)

    return breakdown


def _calculate_top_merchants(transactions: list, limit: int = 15) -> list[dict]:
    """Calculate top merchants by spending."""
    merchant_totals: dict[str, float] = defaultdict(float)
    merchant_counts: dict[str, int] = defaultdict(int)

    for tx in transactions:
        if tx.amount < 0:  # Only spending
            merchant = tx.merchant or tx.description[:30]
            merchant_totals[merchant] += abs(tx.amount)
            merchant_counts[merchant] += 1

    merchants = []
    for merchant, total in merchant_totals.items():
        merchants.append({
            "merchant": merchant,
            "total": round(total, 2),
            "count": merchant_counts[merchant]
        })

    # Sort by total and limit
    merchants.sort(key=lambda x: x["total"], reverse=True)

    return merchants[:limit]
