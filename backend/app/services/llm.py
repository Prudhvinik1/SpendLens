"""
LLM client using LangChain with OpenRouter.

OpenRouter provides access to many models through an OpenAI-compatible API.
We use langchain-openai with a custom base_url pointing to OpenRouter.

Key pattern:
- All LLM calls go through this module for consistency
- Opik tracing is automatically attached via callbacks
- Structured output parsing with Pydantic models
"""

from typing import TypeVar

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel

from app.core.config import settings
from app.core.opik_setup import get_opik_tracer


# Type variable for generic structured output
T = TypeVar("T", bound=BaseModel)


def get_llm(temperature: float = 0.0) -> ChatOpenAI:
    """
    Get a configured LLM client for OpenRouter.

    Args:
        temperature: Controls randomness (0.0 = deterministic, 1.0 = creative)
                    Use 0.0 for categorization (consistent results)

    Returns:
        ChatOpenAI instance configured for OpenRouter
    """
    return ChatOpenAI(
        model=settings.OPENROUTER_MODEL,
        openai_api_key=settings.OPENROUTER_API_KEY,
        openai_api_base=settings.OPENROUTER_BASE_URL,
        temperature=temperature,
        # OpenRouter-specific headers
        default_headers={
            "HTTP-Referer": "https://spendlens.app",  # Required by OpenRouter
            "X-Title": "SpendLens",  # Shows in OpenRouter dashboard
        }
    )


def create_chain_with_tracing(
    prompt: ChatPromptTemplate,
    output_schema: type[T],
    tags: list[str] | None = None,
    metadata: dict | None = None,
    temperature: float = 0.0
):
    """
    Create a LangChain chain with Opik tracing and structured output.

    This is the main factory for creating traced LLM chains.

    Args:
        prompt: The prompt template to use
        output_schema: Pydantic model for structured output parsing
        tags: Tags for Opik tracing
        metadata: Metadata for Opik tracing
        temperature: LLM temperature setting

    Returns:
        A chain that can be invoked with .invoke({"key": "value"})

    Example:
        class CategoryOutput(BaseModel):
            category: str
            confidence: float

        chain = create_chain_with_tracing(
            prompt=categorize_prompt,
            output_schema=CategoryOutput,
            tags=["categorization"]
        )
        result = chain.invoke({"description": "AMAZON.COM*12345"})
    """
    llm = get_llm(temperature=temperature)

    # Create JSON output parser with the schema
    parser = JsonOutputParser(pydantic_object=output_schema)

    # Build the chain: prompt -> llm -> parser
    chain = prompt | llm | parser

    return chain, get_opik_tracer(tags=tags, metadata=metadata)


def invoke_with_tracing(
    chain,
    inputs: dict,
    tracer=None
) -> dict:
    """
    Invoke a chain with optional Opik tracing.

    Args:
        chain: The LangChain chain to invoke
        inputs: Input dict for the chain
        tracer: Optional Opik tracer (from create_chain_with_tracing)

    Returns:
        The chain output (parsed according to output_schema)
    """
    config = {}
    if tracer:
        config["callbacks"] = [tracer]

    return chain.invoke(inputs, config=config)
