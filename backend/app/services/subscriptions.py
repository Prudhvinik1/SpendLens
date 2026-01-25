"""
Subscription detection service.

Detects recurring charges by looking for:
1. Similar merchant names (fuzzy matching)
2. Similar amounts (within tolerance)
3. Regular intervals (weekly, monthly, yearly)

Challenges handled:
- Merchant name variations: "NETFLIX.COM" vs "NETFLIX INC" vs "Netflix"
- Amount variations: taxes, promos, price changes
- Timing variations: billing date shifts, weekends
"""

import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from difflib import SequenceMatcher


@dataclass
class SubscriptionMatch:
    """A detected subscription pattern."""
    merchant: str  # Normalized merchant name
    transaction_ids: list[int]  # IDs of matching transactions
    amounts: list[float]  # All amounts seen
    dates: list[date]  # All dates
    average_amount: float
    frequency: str  # "weekly", "monthly", "yearly", "irregular"
    confidence: float  # 0.0-1.0


@dataclass
class TransactionInfo:
    """Minimal transaction info for subscription detection."""
    id: int
    merchant: str
    description: str
    amount: float
    date: date


def detect_subscriptions(
    transactions: list[TransactionInfo],
    amount_tolerance: float = 0.15,  # 15% variation allowed
    min_occurrences: int = 2
) -> list[SubscriptionMatch]:
    """
    Detect subscription patterns in transactions.

    Args:
        transactions: List of transaction info objects
        amount_tolerance: Allowed percentage variation in amount
        min_occurrences: Minimum times a charge must appear

    Returns:
        List of detected subscription patterns
    """
    if len(transactions) < min_occurrences:
        return []

    # Only look at spending (negative amounts)
    spending = [t for t in transactions if t.amount < 0]

    # Group by similar merchants
    merchant_groups = _group_by_merchant(spending)

    subscriptions = []

    for merchant_key, txs in merchant_groups.items():
        if len(txs) < min_occurrences:
            continue

        # Check if amounts are similar
        amounts = [abs(t.amount) for t in txs]
        if not _amounts_are_similar(amounts, amount_tolerance):
            continue

        # Analyze frequency
        dates = sorted([t.date for t in txs])
        frequency, freq_confidence = _detect_frequency(dates)

        if frequency == "irregular" and freq_confidence < 0.5:
            continue  # Not a subscription

        # Calculate overall confidence
        amount_consistency = _calculate_amount_consistency(amounts)
        confidence = (freq_confidence + amount_consistency) / 2

        subscriptions.append(SubscriptionMatch(
            merchant=txs[0].merchant or _clean_merchant_name(txs[0].description),
            transaction_ids=[t.id for t in txs],
            amounts=amounts,
            dates=dates,
            average_amount=sum(amounts) / len(amounts),
            frequency=frequency,
            confidence=round(confidence, 2)
        ))

    # Sort by confidence (highest first)
    subscriptions.sort(key=lambda s: s.confidence, reverse=True)

    return subscriptions


def _group_by_merchant(transactions: list[TransactionInfo]) -> dict[str, list[TransactionInfo]]:
    """
    Group transactions by similar merchant names.

    Uses fuzzy matching to handle variations like:
    - "NETFLIX.COM" and "NETFLIX INC"
    - "SPOTIFY USA" and "SPOTIFY"
    """
    groups: dict[str, list[TransactionInfo]] = defaultdict(list)
    assigned: set[int] = set()

    # Sort by description for consistent grouping
    sorted_txs = sorted(transactions, key=lambda t: t.description.lower())

    for tx in sorted_txs:
        if tx.id in assigned:
            continue

        # Use merchant if available, otherwise clean description
        key = _normalize_merchant(tx.merchant or tx.description)

        # Find similar transactions
        for other in sorted_txs:
            if other.id in assigned or other.id == tx.id:
                continue

            other_key = _normalize_merchant(other.merchant or other.description)

            if _merchants_match(key, other_key):
                if key not in groups or tx.id not in [t.id for t in groups[key]]:
                    groups[key].append(tx)
                    assigned.add(tx.id)
                groups[key].append(other)
                assigned.add(other.id)

        # If no matches found, still add the transaction
        if tx.id not in assigned:
            groups[key].append(tx)
            assigned.add(tx.id)

    return dict(groups)


def _normalize_merchant(name: str) -> str:
    """Normalize merchant name for comparison."""
    # Lowercase
    name = name.lower()

    # Remove common suffixes/prefixes
    patterns_to_remove = [
        r'\*\w+',  # *ABC123
        r'#\d+',   # #12345
        r'\d{5,}', # Long numbers
        r'\.com',
        r'\.org',
        r'\binc\b',
        r'\bllc\b',
        r'\bcorp\b',
        r'\busa\b',
    ]

    for pattern in patterns_to_remove:
        name = re.sub(pattern, '', name)

    # Remove special characters, keep only alphanumeric and space
    name = re.sub(r'[^a-z0-9\s]', '', name)

    # Collapse whitespace
    name = ' '.join(name.split())

    return name.strip()


def _clean_merchant_name(description: str) -> str:
    """Create a clean, readable merchant name from description."""
    # Remove transaction IDs
    name = re.sub(r'[*#]\s*\w+', '', description)
    name = re.sub(r'\s+\d{5,}', '', name)

    # Title case
    name = ' '.join(word.capitalize() for word in name.split())

    return name.strip()[:50]


def _merchants_match(name1: str, name2: str) -> bool:
    """Check if two merchant names are similar enough to be the same."""
    if name1 == name2:
        return True

    # Check if one contains the other
    if name1 in name2 or name2 in name1:
        return True

    # Fuzzy match using SequenceMatcher
    ratio = SequenceMatcher(None, name1, name2).ratio()
    return ratio > 0.7


def _amounts_are_similar(amounts: list[float], tolerance: float) -> bool:
    """Check if all amounts are within tolerance of each other."""
    if not amounts:
        return False

    avg = sum(amounts) / len(amounts)
    if avg == 0:
        return all(a == 0 for a in amounts)

    for amount in amounts:
        if abs(amount - avg) / avg > tolerance:
            return False

    return True


def _calculate_amount_consistency(amounts: list[float]) -> float:
    """Calculate how consistent the amounts are (0-1)."""
    if len(amounts) < 2:
        return 1.0

    avg = sum(amounts) / len(amounts)
    if avg == 0:
        return 1.0

    # Calculate coefficient of variation
    variance = sum((a - avg) ** 2 for a in amounts) / len(amounts)
    std_dev = variance ** 0.5
    cv = std_dev / avg

    # Convert to 0-1 score (lower variation = higher score)
    return max(0, 1 - cv)


def _detect_frequency(dates: list[date]) -> tuple[str, float]:
    """
    Detect the billing frequency from transaction dates.

    Returns:
        Tuple of (frequency_name, confidence)
    """
    if len(dates) < 2:
        return ("irregular", 0.0)

    # Calculate intervals between consecutive dates
    intervals = []
    sorted_dates = sorted(dates)
    for i in range(1, len(sorted_dates)):
        delta = (sorted_dates[i] - sorted_dates[i-1]).days
        intervals.append(delta)

    avg_interval = sum(intervals) / len(intervals)

    # Define expected intervals with tolerance
    frequencies = [
        ("weekly", 7, 2),      # ~7 days, ±2 days tolerance
        ("biweekly", 14, 3),   # ~14 days
        ("monthly", 30, 5),    # ~30 days
        ("yearly", 365, 30),   # ~365 days
    ]

    best_match = ("irregular", 0.0)

    for name, expected, tolerance in frequencies:
        if abs(avg_interval - expected) <= tolerance:
            # Calculate consistency
            variance = sum((i - expected) ** 2 for i in intervals) / len(intervals)
            consistency = max(0, 1 - (variance ** 0.5) / expected)

            if consistency > best_match[1]:
                best_match = (name, consistency)

    return best_match
