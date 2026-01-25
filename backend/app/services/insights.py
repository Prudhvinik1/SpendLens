"""
Insights generation service.

Uses LLM to generate personalized spending insights based on:
- Category breakdown
- Detected subscriptions
- Detected anomalies
- Top merchants

All LLM calls are traced via Opik.
"""

import json
from dataclasses import dataclass
from datetime import date
from typing import Optional

from app.core.config import settings
from app.core.opik_setup import get_opik_tracer
from app.services.llm import get_llm
from app.prompts.insights import (
    INSIGHTS_PROMPT,
    format_category_breakdown,
    format_subscriptions,
    format_anomalies,
    format_top_merchants
)


@dataclass
class SpendingSummary:
    """Summary data for insight generation."""
    period_start: Optional[date]
    period_end: Optional[date]
    total_spent: float
    total_income: float
    categories: list[dict]  # [{category, total, percentage}]
    subscriptions: list[dict]  # [{merchant, average_amount, frequency}]
    anomalies: list[dict]  # [{reason, severity}]
    top_merchants: list[dict]  # [{merchant, total, count}]


@dataclass
class GeneratedInsight:
    """A single generated insight."""
    type: str  # subscription, anomaly, trend, tip
    title: str
    description: str
    severity: str  # info, warning, alert
    category: Optional[str]
    amount: Optional[float]
    action_suggestion: Optional[str]


def generate_insights(
    summary: SpendingSummary,
    statement_id: int | None = None
) -> list[GeneratedInsight]:
    """
    Generate spending insights using LLM.

    Args:
        summary: Spending summary data
        statement_id: Optional statement ID for tracing

    Returns:
        List of generated insights
    """
    # Format data for the prompt
    prompt_data = {
        "period_start": str(summary.period_start) if summary.period_start else "Unknown",
        "period_end": str(summary.period_end) if summary.period_end else "Unknown",
        "total_spent": summary.total_spent,
        "total_income": summary.total_income,
        "net_change": summary.total_income - summary.total_spent,
        "category_breakdown": format_category_breakdown(summary.categories),
        "subscriptions": format_subscriptions(summary.subscriptions),
        "anomalies": format_anomalies(summary.anomalies),
        "top_merchants": format_top_merchants(summary.top_merchants),
    }

    # Get LLM with tracing
    llm = get_llm(temperature=0.3)  # Slightly creative for insights

    # Set up Opik tracing
    tracer = get_opik_tracer(
        tags=["insights", "generation"],
        metadata={
            "statement_id": statement_id,
            "total_spent": summary.total_spent,
            "category_count": len(summary.categories),
            "subscription_count": len(summary.subscriptions),
            "anomaly_count": len(summary.anomalies)
        }
    )

    config = {}
    if tracer:
        config["callbacks"] = [tracer]

    try:
        # Build and invoke chain
        chain = INSIGHTS_PROMPT | llm
        response = chain.invoke(prompt_data, config=config)

        # Parse response
        insights_data = _parse_insights_response(response.content)

        # Convert to dataclass objects
        insights = []
        for data in insights_data:
            insight = GeneratedInsight(
                type=data.get("type", "tip"),
                title=data.get("title", "Insight")[:50],
                description=data.get("description", ""),
                severity=_validate_severity(data.get("severity", "info")),
                category=data.get("category"),
                amount=data.get("amount"),
                action_suggestion=data.get("action_suggestion")
            )
            insights.append(insight)

        return insights

    except Exception as e:
        print(f"Failed to generate insights: {e}")
        # Return basic fallback insights
        return _generate_fallback_insights(summary)


def _parse_insights_response(content: str) -> list[dict]:
    """Parse LLM response into insight dicts."""
    content = content.strip()

    # Remove markdown code blocks if present
    if content.startswith("```"):
        first_newline = content.find("\n")
        last_fence = content.rfind("```")
        if last_fence > first_newline:
            content = content[first_newline + 1:last_fence].strip()

    try:
        parsed = json.loads(content)
        if isinstance(parsed, list):
            return parsed
        elif isinstance(parsed, dict) and "insights" in parsed:
            return parsed["insights"]
        else:
            return []
    except json.JSONDecodeError as e:
        print(f"Failed to parse insights JSON: {e}")
        return []


def _validate_severity(severity: str) -> str:
    """Validate severity is one of the allowed values."""
    valid = ["info", "warning", "alert"]
    severity = severity.lower().strip()
    return severity if severity in valid else "info"


def _generate_fallback_insights(summary: SpendingSummary) -> list[GeneratedInsight]:
    """Generate basic insights without LLM if it fails."""
    insights = []

    # Top spending category insight
    if summary.categories:
        top_cat = summary.categories[0]
        insights.append(GeneratedInsight(
            type="trend",
            title=f"Top spending: {top_cat['category'].title()}",
            description=f"Your highest spending category is {top_cat['category']} at ${top_cat['total']:.2f} ({top_cat['percentage']:.1f}% of total spending).",
            severity="info",
            category=top_cat['category'],
            amount=top_cat['total'],
            action_suggestion="Review transactions in this category for potential savings."
        ))

    # Subscription summary
    if summary.subscriptions:
        total_subs = sum(s.get("average_amount", 0) for s in summary.subscriptions)
        insights.append(GeneratedInsight(
            type="subscription",
            title=f"{len(summary.subscriptions)} subscriptions detected",
            description=f"You have {len(summary.subscriptions)} recurring charges totaling approximately ${total_subs:.2f}/month.",
            severity="info",
            category="subscriptions",
            amount=total_subs,
            action_suggestion="Review your subscriptions to ensure you're using all of them."
        ))

    # Anomaly summary
    if summary.anomalies:
        insights.append(GeneratedInsight(
            type="anomaly",
            title=f"{len(summary.anomalies)} unusual transactions",
            description=f"We detected {len(summary.anomalies)} transactions that seem unusual compared to your normal spending.",
            severity="warning",
            category=None,
            amount=None,
            action_suggestion="Review these transactions to ensure they're legitimate."
        ))

    return insights
