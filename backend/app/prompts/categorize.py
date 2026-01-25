"""
Prompts for transaction categorization.

These prompts are designed for batch processing - categorizing multiple
transactions in a single LLM call for efficiency.

You can iterate on these prompts to improve accuracy. Key things to tune:
- Category definitions and examples
- Confidence score calibration
- Edge case handling
"""

from langchain_core.prompts import ChatPromptTemplate

from app.core.config import settings


# Build category definitions with examples
CATEGORY_DEFINITIONS = """
CATEGORIES AND EXAMPLES:

housing - Rent, mortgage, property tax, HOA fees, home insurance
utilities - Electric, gas, water, internet, phone bills (AT&T, Verizon, Comcast, PG&E)
groceries - Supermarkets, grocery stores (Whole Foods, Trader Joe's, Safeway, Costco food)
dining - Restaurants, fast food, coffee shops, food delivery (Uber Eats, DoorDash, Starbucks)
transportation - Gas stations, rideshare (Uber, Lyft), public transit, parking, car maintenance
shopping - Retail stores, Amazon, clothing, electronics, home goods (Target, Walmart, Best Buy)
entertainment - Streaming services, movies, games, concerts, hobbies (Netflix, Spotify, Steam)
health - Medical bills, pharmacy, gym membership, health insurance (CVS, Walgreens, Planet Fitness)
personal_care - Haircuts, spa, cosmetics, personal products
subscriptions - Recurring digital services (Adobe, Dropbox, cloud storage, software)
travel - Airlines, hotels, vacation rentals, travel booking (Delta, Hilton, Airbnb)
education - Tuition, courses, books, educational subscriptions (Coursera, Udemy)
financial - Bank fees, interest charges, investment contributions, loan payments
income - Salary, direct deposits, refunds, reimbursements, Venmo/PayPal received
other - Anything that doesn't clearly fit above
"""

# The main categorization prompt for batch processing
CATEGORIZE_BATCH_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a financial transaction categorizer. Your job is to:
1. Assign the most appropriate category to each transaction
2. Normalize the merchant name to a clean, readable format
3. Provide a confidence score (0.0-1.0) for your categorization

{category_definitions}

CONFIDENCE SCORING:
- 0.9-1.0: Very confident (clear merchant name, obvious category)
- 0.7-0.89: Confident (recognizable merchant, likely category)
- 0.5-0.69: Uncertain (ambiguous description, could be multiple categories)
- Below 0.5: Low confidence (unclear description, guessing)

RULES:
- Use ONLY the categories listed above
- For ambiguous cases, prefer the more specific category
- If a transaction could be "shopping" or a more specific category, use the specific one
- Negative amounts are spending, positive amounts are income
- For positive amounts, use "income" unless it's clearly a refund in a specific category

Respond with a JSON array of objects, one per transaction."""),

    ("human", """Categorize these transactions:

{transactions}

Return JSON array with this exact structure for each transaction:
[
  {{
    "index": 0,
    "merchant": "Clean Merchant Name",
    "category": "category_name",
    "confidence": 0.95
  }},
  ...
]""")
])


def format_transactions_for_prompt(transactions: list[dict]) -> str:
    """
    Format transactions for inclusion in the prompt.

    Args:
        transactions: List of dicts with 'index', 'description', 'amount'

    Returns:
        Formatted string for the prompt
    """
    lines = []
    for tx in transactions:
        amount_str = f"${tx['amount']:,.2f}"
        lines.append(f"{tx['index']}. {tx['description']} | {amount_str}")
    return "\n".join(lines)


def get_categorize_prompt() -> ChatPromptTemplate:
    """Get the categorization prompt with category definitions injected."""
    return CATEGORIZE_BATCH_PROMPT.partial(
        category_definitions=CATEGORY_DEFINITIONS
    )
