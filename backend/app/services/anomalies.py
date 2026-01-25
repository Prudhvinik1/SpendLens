"""
Anomaly detection service.

Detects unusual transactions by looking for:
1. Unusually large amounts (statistical outliers)
2. Category outliers (much higher than category average)
3. Rare merchants with large amounts

Uses z-score based detection - simple but effective.
Z-score = (value - mean) / standard_deviation
"""

from dataclasses import dataclass
from collections import defaultdict


@dataclass
class TransactionForAnomaly:
    """Minimal transaction info for anomaly detection."""
    id: int
    merchant: str
    description: str
    amount: float
    category: str


@dataclass
class AnomalyResult:
    """Detected anomaly information."""
    transaction_id: int
    reason: str
    severity: str  # "warning" or "alert"
    z_score: float  # How many std deviations from mean
    context: dict  # Additional context (e.g., category avg)


def detect_anomalies(
    transactions: list[TransactionForAnomaly],
    z_threshold: float = 2.0,  # 2 standard deviations = ~95th percentile
    min_transactions: int = 5  # Need enough data for stats
) -> list[AnomalyResult]:
    """
    Detect anomalous transactions.

    Args:
        transactions: List of transaction info
        z_threshold: Z-score threshold for anomaly
        min_transactions: Minimum transactions needed for analysis

    Returns:
        List of detected anomalies
    """
    if len(transactions) < min_transactions:
        return []

    # Only analyze spending (negative amounts)
    spending = [t for t in transactions if t.amount < 0]

    if len(spending) < min_transactions:
        return []

    anomalies = []

    # 1. Global amount outliers
    global_anomalies = _detect_global_outliers(spending, z_threshold)
    anomalies.extend(global_anomalies)

    # 2. Category-specific outliers
    category_anomalies = _detect_category_outliers(spending, z_threshold)
    anomalies.extend(category_anomalies)

    # Deduplicate (prefer higher severity)
    seen_ids = {}
    for anomaly in anomalies:
        if anomaly.transaction_id not in seen_ids:
            seen_ids[anomaly.transaction_id] = anomaly
        elif anomaly.severity == "alert" and seen_ids[anomaly.transaction_id].severity == "warning":
            seen_ids[anomaly.transaction_id] = anomaly

    return list(seen_ids.values())


def _detect_global_outliers(
    transactions: list[TransactionForAnomaly],
    z_threshold: float
) -> list[AnomalyResult]:
    """Detect transactions that are outliers across all spending."""
    amounts = [abs(t.amount) for t in transactions]
    mean, std = _calculate_stats(amounts)

    if std == 0:
        return []

    anomalies = []
    for tx in transactions:
        amount = abs(tx.amount)
        z_score = (amount - mean) / std

        if z_score > z_threshold:
            severity = "alert" if z_score > z_threshold * 1.5 else "warning"

            anomalies.append(AnomalyResult(
                transaction_id=tx.id,
                reason=f"Unusually large transaction (${amount:.2f} vs avg ${mean:.2f})",
                severity=severity,
                z_score=round(z_score, 2),
                context={
                    "amount": amount,
                    "average": round(mean, 2),
                    "std_dev": round(std, 2),
                    "merchant": tx.merchant or tx.description
                }
            ))

    return anomalies


def _detect_category_outliers(
    transactions: list[TransactionForAnomaly],
    z_threshold: float,
    min_in_category: int = 3
) -> list[AnomalyResult]:
    """Detect transactions that are outliers within their category."""
    # Group by category
    by_category: dict[str, list[TransactionForAnomaly]] = defaultdict(list)
    for tx in transactions:
        by_category[tx.category].append(tx)

    anomalies = []

    for category, cat_txs in by_category.items():
        if len(cat_txs) < min_in_category:
            continue

        amounts = [abs(t.amount) for t in cat_txs]
        mean, std = _calculate_stats(amounts)

        if std == 0:
            continue

        for tx in cat_txs:
            amount = abs(tx.amount)
            z_score = (amount - mean) / std

            if z_score > z_threshold:
                anomalies.append(AnomalyResult(
                    transaction_id=tx.id,
                    reason=f"High for {category}: ${amount:.2f} vs category avg ${mean:.2f}",
                    severity="warning",
                    z_score=round(z_score, 2),
                    context={
                        "amount": amount,
                        "category": category,
                        "category_average": round(mean, 2),
                        "category_std_dev": round(std, 2),
                        "merchant": tx.merchant or tx.description
                    }
                ))

    return anomalies


def _calculate_stats(values: list[float]) -> tuple[float, float]:
    """Calculate mean and standard deviation."""
    if not values:
        return (0.0, 0.0)

    n = len(values)
    mean = sum(values) / n

    if n < 2:
        return (mean, 0.0)

    variance = sum((x - mean) ** 2 for x in values) / (n - 1)  # Sample std dev
    std = variance ** 0.5

    return (mean, std)
