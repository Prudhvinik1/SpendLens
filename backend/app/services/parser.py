"""
CSV Parser with automatic format detection.

Supported formats:
- Bank of America (Date, Description, Amount, Running Bal.)
- Discover Card (Trans. Date, Post Date, Description, Amount, Category)

Design pattern: Each format is a parser class that implements a common interface.
The main `parse_statement` function tries each parser until one succeeds.
"""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime
from io import StringIO
from typing import Optional

import pandas as pd


@dataclass
class ParsedTransaction:
    """
    Normalized transaction data from any statement format.

    This is what all parsers output, regardless of the source format.
    Using a dataclass here instead of Pydantic because this is internal
    data processing, not API validation.
    """
    date: date
    description: str
    amount: float  # Negative = spent, positive = income
    original_category: Optional[str] = None  # If the source provides it (Discover does)


@dataclass
class ParseResult:
    """Result of parsing a statement file."""
    success: bool
    format_name: str
    transactions: list[ParsedTransaction]
    period_start: Optional[date]
    period_end: Optional[date]
    error_message: Optional[str] = None


class StatementParser(ABC):
    """
    Abstract base class for statement parsers.

    To add a new format:
    1. Create a subclass
    2. Implement `can_parse()` to detect if the format matches
    3. Implement `parse()` to extract transactions
    4. Add the parser to `PARSERS` list at the bottom
    """

    name: str = "unknown"

    @abstractmethod
    def can_parse(self, df: pd.DataFrame, raw_content: str) -> bool:
        """
        Check if this parser can handle the given CSV.

        Args:
            df: Parsed DataFrame (might have wrong column interpretation)
            raw_content: Raw CSV string (for header inspection)

        Returns:
            True if this parser can handle this format
        """
        pass

    @abstractmethod
    def parse(self, df: pd.DataFrame) -> list[ParsedTransaction]:
        """
        Parse the DataFrame into normalized transactions.

        Args:
            df: DataFrame read with this parser's expected columns

        Returns:
            List of ParsedTransaction objects
        """
        pass

    def _normalize_amount(self, amount: float, negate: bool = False) -> float:
        """
        Normalize amount to our convention: negative = spending, positive = income.

        Args:
            amount: Raw amount from the statement
            negate: If True, flip the sign (some banks use opposite convention)
        """
        result = float(amount)
        if negate:
            result = -result
        return round(result, 2)

    def _parse_date(self, date_str: str, formats: list[str]) -> date:
        """
        Parse a date string trying multiple formats.

        Args:
            date_str: The date string to parse
            formats: List of strptime format strings to try

        Returns:
            Parsed date object

        Raises:
            ValueError: If none of the formats match
        """
        date_str = str(date_str).strip()
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Could not parse date: {date_str}")


class BankOfAmericaParser(StatementParser):
    """
    Parser for Bank of America CSV statements.

    Expected columns: Date, Description, Amount, Running Bal.
    Date format: MM/DD/YYYY
    Amount convention: Negative = spending (matches our convention)
    """

    name = "bank_of_america"

    # Columns we look for (lowercase for matching)
    REQUIRED_COLUMNS = {"date", "description", "amount"}
    OPTIONAL_COLUMNS = {"running bal.", "running bal", "balance"}

    def can_parse(self, df: pd.DataFrame, raw_content: str) -> bool:
        """Check if this looks like a Bank of America statement."""
        # Normalize column names for comparison
        columns = {col.lower().strip() for col in df.columns}

        # Must have all required columns
        if not self.REQUIRED_COLUMNS.issubset(columns):
            return False

        # Should have a balance column (distinguishes from other formats)
        if not columns & self.OPTIONAL_COLUMNS:
            return False

        # Should NOT have "trans. date" or "post date" (that's Discover)
        if "trans. date" in columns or "post date" in columns:
            return False

        return True

    def parse(self, df: pd.DataFrame) -> list[ParsedTransaction]:
        """Parse Bank of America statement."""
        transactions = []

        # Normalize column names
        df.columns = [col.lower().strip() for col in df.columns]

        for _, row in df.iterrows():
            try:
                trans = ParsedTransaction(
                    date=self._parse_date(row["date"], ["%m/%d/%Y", "%m/%d/%y"]),
                    description=str(row["description"]).strip(),
                    amount=self._normalize_amount(row["amount"]),
                    original_category=None  # BofA doesn't provide categories
                )
                transactions.append(trans)
            except (ValueError, KeyError) as e:
                # Skip malformed rows but log them
                print(f"Skipping row due to parse error: {e}")
                continue

        return transactions


class DiscoverParser(StatementParser):
    """
    Parser for Discover Card CSV statements.

    Expected columns: Trans. Date, Post Date, Description, Amount, Category
    Date format: MM/DD/YYYY
    Amount convention: Negative = spending (matches our convention)
    """

    name = "discover"

    REQUIRED_COLUMNS = {"trans. date", "description", "amount"}

    def can_parse(self, df: pd.DataFrame, raw_content: str) -> bool:
        """Check if this looks like a Discover statement."""
        columns = {col.lower().strip() for col in df.columns}

        # Must have trans. date (unique to Discover)
        if "trans. date" not in columns:
            return False

        # Must have description and amount
        if not {"description", "amount"}.issubset(columns):
            return False

        return True

    def parse(self, df: pd.DataFrame) -> list[ParsedTransaction]:
        """Parse Discover statement."""
        transactions = []

        # Normalize column names
        df.columns = [col.lower().strip() for col in df.columns]

        for _, row in df.iterrows():
            try:
                # Get category if available
                category = None
                if "category" in df.columns:
                    category = str(row["category"]).strip()
                    if category.lower() in ("nan", "none", ""):
                        category = None

                trans = ParsedTransaction(
                    date=self._parse_date(row["trans. date"], ["%m/%d/%Y", "%m/%d/%y"]),
                    description=str(row["description"]).strip(),
                    amount=self._normalize_amount(row["amount"]),
                    original_category=category
                )
                transactions.append(trans)
            except (ValueError, KeyError) as e:
                print(f"Skipping row due to parse error: {e}")
                continue

        return transactions


# Register all parsers here (order matters - more specific parsers first)
PARSERS: list[StatementParser] = [
    DiscoverParser(),    # Check Discover first (has unique "Trans. Date" column)
    BankOfAmericaParser(),
]


def parse_statement(content: str | bytes) -> ParseResult:
    """
    Parse a statement file with automatic format detection.

    This function tries each registered parser in order until one succeeds.

    Args:
        content: CSV file content as string or bytes

    Returns:
        ParseResult with transactions and metadata
    """
    # Convert bytes to string if needed
    if isinstance(content, bytes):
        # Try UTF-8 first, fall back to latin-1 (handles most bank exports)
        try:
            content = content.decode("utf-8")
        except UnicodeDecodeError:
            content = content.decode("latin-1")

    # Initial parse to inspect structure
    try:
        df = pd.read_csv(StringIO(content))
    except Exception as e:
        return ParseResult(
            success=False,
            format_name="unknown",
            transactions=[],
            period_start=None,
            period_end=None,
            error_message=f"Failed to read CSV: {str(e)}"
        )

    # Empty file check
    if df.empty:
        return ParseResult(
            success=False,
            format_name="unknown",
            transactions=[],
            period_start=None,
            period_end=None,
            error_message="CSV file is empty"
        )

    # Try each parser
    for parser in PARSERS:
        if parser.can_parse(df, content):
            try:
                # Re-read with fresh DataFrame for the parser
                df = pd.read_csv(StringIO(content))
                transactions = parser.parse(df)

                if not transactions:
                    continue  # Parser matched but found no transactions

                # Calculate date range
                dates = [t.date for t in transactions]
                period_start = min(dates)
                period_end = max(dates)

                return ParseResult(
                    success=True,
                    format_name=parser.name,
                    transactions=transactions,
                    period_start=period_start,
                    period_end=period_end
                )
            except Exception as e:
                # Parser matched but failed - try next parser
                print(f"Parser {parser.name} failed: {e}")
                continue

    # No parser matched
    return ParseResult(
        success=False,
        format_name="unknown",
        transactions=[],
        period_start=None,
        period_end=None,
        error_message="Unrecognized statement format. Supported: Bank of America, Discover"
    )


def get_supported_formats() -> list[dict]:
    """Return information about supported statement formats."""
    return [
        {
            "name": "Bank of America",
            "id": "bank_of_america",
            "columns": "Date, Description, Amount, Running Bal."
        },
        {
            "name": "Discover Card",
            "id": "discover",
            "columns": "Trans. Date, Post Date, Description, Amount, Category"
        }
    ]
