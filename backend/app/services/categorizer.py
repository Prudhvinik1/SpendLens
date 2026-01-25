"""
Transaction categorization service.

Handles batch categorization of transactions using LLM.
All LLM calls are traced via Opik for observability.

Key design decisions:
- Batch processing: Multiple transactions per LLM call (configurable batch size)
- Fallback handling: If LLM fails, transactions get default category + low confidence
- Validation: Results are validated against known categories
"""

import json
from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel

from app.core.config import settings
from app.core.opik_setup import get_opik_tracer
from app.services.llm import get_llm
from app.prompts.categorize import get_categorize_prompt, format_transactions_for_prompt


@dataclass
class CategorizationResult:
    """Result for a single transaction categorization."""
    index: int
    merchant: str
    category: str
    confidence: float
    needs_review: bool


class BatchCategorizationOutput(BaseModel):
    """Expected output structure from LLM."""
    results: list[dict]


def categorize_transactions(
    transactions: list[dict],
    statement_id: int | None = None
) -> list[CategorizationResult]:
    """
    Categorize a list of transactions using LLM.

    Processes transactions in batches for efficiency.
    Each batch is a single LLM call.

    Args:
        transactions: List of dicts with 'description' and 'amount' keys
        statement_id: Optional statement ID for tracing

    Returns:
        List of CategorizationResult objects (same order as input)
    """
    if not transactions:
        return []

    results = []
    batch_size = settings.CATEGORIZATION_BATCH_SIZE

    # Process in batches
    for batch_start in range(0, len(transactions), batch_size):
        batch_end = min(batch_start + batch_size, len(transactions))
        batch = transactions[batch_start:batch_end]

        # Add index to each transaction for matching results
        indexed_batch = [
            {
                "index": i,
                "description": tx["description"],
                "amount": tx["amount"]
            }
            for i, tx in enumerate(batch, start=batch_start)
        ]

        batch_results = _categorize_batch(
            indexed_batch,
            statement_id=statement_id,
            batch_number=batch_start // batch_size + 1
        )
        results.extend(batch_results)

    return results


def _categorize_batch(
    batch: list[dict],
    statement_id: int | None = None,
    batch_number: int = 1
) -> list[CategorizationResult]:
    """
    Categorize a single batch of transactions.

    Args:
        batch: List of indexed transaction dicts
        statement_id: Optional statement ID for tracing
        batch_number: Which batch this is (for logging)

    Returns:
        List of CategorizationResult objects
    """
    # Get the prompt and format transactions
    prompt = get_categorize_prompt()
    formatted_transactions = format_transactions_for_prompt(batch)

    # Get LLM with tracing
    llm = get_llm(temperature=0.0)

    # Set up Opik tracing
    tracer = get_opik_tracer(
        tags=["categorization", f"batch:{batch_number}"],
        metadata={
            "statement_id": statement_id,
            "batch_size": len(batch),
            "batch_number": batch_number
        }
    )

    # Build config with tracer if available
    config = {}
    if tracer:
        config["callbacks"] = [tracer]

    try:
        # Invoke the chain
        chain = prompt | llm

        response = chain.invoke(
            {"transactions": formatted_transactions},
            config=config
        )

        # Parse the response
        llm_results = _parse_llm_response(response.content)

        # Match results to transactions and validate
        return _process_results(batch, llm_results)

    except Exception as e:
        print(f"Batch categorization failed: {e}")
        # Return default results for all transactions in batch
        return [
            CategorizationResult(
                index=tx["index"],
                merchant=_extract_merchant_fallback(tx["description"]),
                category="other",
                confidence=0.0,
                needs_review=True
            )
            for tx in batch
        ]


def _parse_llm_response(content: str) -> list[dict]:
    """
    Parse LLM response content into a list of result dicts.

    Handles both raw JSON and markdown-wrapped JSON.
    """
    # Clean up the response
    content = content.strip()

    # Remove markdown code blocks if present
    if content.startswith("```"):
        # Find the end of the opening fence
        first_newline = content.find("\n")
        # Find the closing fence
        last_fence = content.rfind("```")
        if last_fence > first_newline:
            content = content[first_newline + 1:last_fence].strip()

    try:
        parsed = json.loads(content)
        # Handle both array and object with "results" key
        if isinstance(parsed, list):
            return parsed
        elif isinstance(parsed, dict) and "results" in parsed:
            return parsed["results"]
        else:
            print(f"Unexpected LLM response structure: {type(parsed)}")
            return []
    except json.JSONDecodeError as e:
        print(f"Failed to parse LLM response as JSON: {e}")
        print(f"Response was: {content[:500]}")
        return []


def _process_results(
    batch: list[dict],
    llm_results: list[dict]
) -> list[CategorizationResult]:
    """
    Process and validate LLM results.

    Matches results to original transactions by index.
    Validates categories and sets needs_review flag.
    """
    # Create a lookup by index
    result_by_index = {r.get("index", -1): r for r in llm_results}

    processed = []
    for tx in batch:
        idx = tx["index"]
        result = result_by_index.get(idx)

        if result:
            # Validate and normalize category
            category = result.get("category", "other").lower().strip()
            if category not in settings.VALID_CATEGORIES:
                category = "other"

            confidence = float(result.get("confidence", 0.5))
            # Clamp confidence to valid range
            confidence = max(0.0, min(1.0, confidence))

            merchant = result.get("merchant", tx["description"])

            processed.append(CategorizationResult(
                index=idx,
                merchant=merchant,
                category=category,
                confidence=confidence,
                needs_review=confidence < settings.LOW_CONFIDENCE_THRESHOLD
            ))
        else:
            # No result for this transaction - use fallback
            processed.append(CategorizationResult(
                index=idx,
                merchant=_extract_merchant_fallback(tx["description"]),
                category="other",
                confidence=0.0,
                needs_review=True
            ))

    return processed


def _extract_merchant_fallback(description: str) -> str:
    """
    Simple fallback merchant extraction when LLM fails.

    Just cleans up the description a bit.
    """
    # Remove common suffixes/prefixes
    merchant = description.strip()

    # Remove transaction IDs (sequences of numbers/letters at end)
    import re
    merchant = re.sub(r'[*#]\s*\w+$', '', merchant)
    merchant = re.sub(r'\s+\d{5,}$', '', merchant)

    # Clean up extra whitespace
    merchant = ' '.join(merchant.split())

    return merchant[:100]  # Limit length
