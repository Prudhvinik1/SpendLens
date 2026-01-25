"""
Prompts for generating spending insights.

The LLM receives:
- Spending summary by category
- Detected subscriptions
- Detected anomalies
- Time period

And generates actionable, personalized insights.
"""

from langchain_core.prompts import ChatPromptTemplate


INSIGHTS_SYSTEM_PROMPT = """You are a helpful financial advisor assistant. Your job is to analyze spending data and provide specific, actionable insights.

INSIGHT TYPES:
- subscription: About recurring charges (found or potential savings)
- anomaly: About unusual transactions that need attention
- trend: About spending patterns and habits
- tip: Actionable savings suggestions

RULES:
1. Be specific - use actual numbers from the data
2. Be actionable - tell the user exactly what they can do
3. Be concise - each insight should be 1-2 sentences
4. Prioritize by impact - biggest savings opportunities first
5. Don't be preachy - no generic "you should budget more" advice
6. If subscriptions are detected, calculate monthly/yearly totals

SEVERITY LEVELS:
- info: General observations, neutral
- warning: Worth paying attention to, potential savings
- alert: Needs immediate attention, unusual activity

Return JSON array of insights with this structure:
[
  {{
    "type": "subscription|anomaly|trend|tip",
    "title": "Short title (max 50 chars)",
    "description": "Detailed insight with specific numbers",
    "severity": "info|warning|alert",
    "category": "category name or null",
    "amount": 123.45 or null,
    "action_suggestion": "Specific action to take"
  }}
]

Generate 3-7 insights based on what's most relevant in the data."""


INSIGHTS_HUMAN_PROMPT = """Analyze this spending data and generate insights:

PERIOD: {period_start} to {period_end}

SPENDING SUMMARY:
Total Spent: ${total_spent:.2f}
Total Income: ${total_income:.2f}
Net Change: ${net_change:.2f}

SPENDING BY CATEGORY:
{category_breakdown}

DETECTED SUBSCRIPTIONS:
{subscriptions}

DETECTED ANOMALIES:
{anomalies}

TOP MERCHANTS BY SPENDING:
{top_merchants}

Generate specific, actionable insights based on this data."""


INSIGHTS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", INSIGHTS_SYSTEM_PROMPT),
    ("human", INSIGHTS_HUMAN_PROMPT)
])


def format_category_breakdown(categories: list[dict]) -> str:
    """Format category spending for the prompt."""
    if not categories:
        return "No spending data"

    lines = []
    for cat in categories:
        pct = cat.get("percentage", 0)
        lines.append(f"- {cat['category']}: ${cat['total']:.2f} ({pct:.1f}%)")

    return "\n".join(lines)


def format_subscriptions(subscriptions: list[dict]) -> str:
    """Format detected subscriptions for the prompt."""
    if not subscriptions:
        return "No recurring subscriptions detected"

    lines = []
    for sub in subscriptions:
        freq = sub.get("frequency", "recurring")
        avg = sub.get("average_amount", 0)
        lines.append(f"- {sub['merchant']}: ${avg:.2f}/{freq}")

    return "\n".join(lines)


def format_anomalies(anomalies: list[dict]) -> str:
    """Format detected anomalies for the prompt."""
    if not anomalies:
        return "No unusual transactions detected"

    lines = []
    for anomaly in anomalies:
        lines.append(f"- {anomaly['reason']}")

    return "\n".join(lines)


def format_top_merchants(merchants: list[dict], limit: int = 10) -> str:
    """Format top merchants by spending."""
    if not merchants:
        return "No merchant data"

    lines = []
    for m in merchants[:limit]:
        lines.append(f"- {m['merchant']}: ${m['total']:.2f} ({m['count']} transactions)")

    return "\n".join(lines)
