"""
Invoice extraction service.

L5 (Adapter Pattern): Clean interface — extract_invoice() returns
ExtractionResult regardless of whether it uses Claude API or mock.
Swap the implementation without touching the rest of the API.

Uses Claude Vision API when ANTHROPIC_API_KEY is configured.
Falls back to mock data otherwise.
"""

import base64
import json
import logging
from typing import Any, Optional

from src.api.models import ExtractionResult, FieldConfidence, LineItemCreate

logger = logging.getLogger(__name__)

# Extraction prompt for Claude Vision API
_EXTRACTION_PROMPT: str = """Analyze this invoice image/PDF and extract the following information.
Return ONLY a JSON object with this exact structure, no other text:

{
  "supplier": {"value": "supplier name", "confidence": 0.95},
  "invoice_number": {"value": "INV-123", "confidence": 0.98},
  "invoice_date": {"value": "2026-01-15", "confidence": 0.92},
  "currency": {"value": "USD", "confidence": 0.99},
  "total_amount": {"value": 1234.56, "confidence": 0.96},
  "payment_due": {"value": "2026-02-15", "confidence": 0.88},
  "line_items": [
    {
      "description": "Item description",
      "quantity": 10,
      "unit_price": 5.00,
      "amount": 50.00
    }
  ]
}

Rules:
- Dates in ISO format (YYYY-MM-DD)
- total_amount as a number, not string
- confidence: 0.0 to 1.0 based on how clearly you can read the field
- If a field is not found, use null for value and 0.0 for confidence
- Extract ALL line items visible on the invoice
- For supplier, include the full company name as shown"""


def extract_invoice(file_path: str) -> ExtractionResult:
    """Extract invoice data from a PDF file.

    Uses Claude Vision API if configured, otherwise returns mock data.

    Args:
        file_path: Absolute path to the uploaded PDF file.

    Returns:
        ExtractionResult with extracted fields and confidence scores.
    """
    from src.api.config import get_anthropic_api_key

    api_key = get_anthropic_api_key()
    if api_key:
        return _extract_with_claude(file_path, api_key)
    else:
        logger.warning("No ANTHROPIC_API_KEY configured — using mock extraction")
        return _extract_mock(file_path)


def _extract_with_claude(file_path: str, api_key: str) -> ExtractionResult:
    """Extract invoice data using Claude Vision API.

    Args:
        file_path: Path to the PDF file.
        api_key: Anthropic API key.

    Returns:
        ExtractionResult from Claude's analysis.
    """
    import anthropic

    from src.api.config import get_anthropic_model

    model = get_anthropic_model()
    logger.info("Extracting invoice with Claude (%s): %s", model, file_path)

    # Read PDF and encode as base64
    with open(file_path, "rb") as f:
        pdf_bytes = f.read()
    pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model=model,
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_base64,
                        },
                    },
                    {
                        "type": "text",
                        "text": _EXTRACTION_PROMPT,
                    },
                ],
            }
        ],
    )

    # Parse response
    response_text = message.content[0].text  # type: ignore[union-attr]
    logger.info("Claude response received (%d chars)", len(response_text))

    return _parse_claude_response(response_text)


def _parse_claude_response(response_text: str) -> ExtractionResult:
    """Parse Claude's JSON response into an ExtractionResult.

    Args:
        response_text: Raw text from Claude API.

    Returns:
        Parsed ExtractionResult.

    Raises:
        ValueError: If the response cannot be parsed.
    """
    # Strip markdown code fences if present
    text = response_text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first line (```json) and last line (```)
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)

    data: dict[str, Any] = json.loads(text)

    def _field(key: str) -> FieldConfidence:
        field_data = data.get(key, {})
        if field_data is None:
            return FieldConfidence(value=None, confidence=0.0)
        return FieldConfidence(
            value=field_data.get("value"),
            confidence=float(field_data.get("confidence", 0.0)),
        )

    line_items: list[LineItemCreate] = []
    for item in data.get("line_items", []):
        line_items.append(LineItemCreate(
            description=str(item.get("description", "")),
            quantity=float(item.get("quantity", 0)),
            unit_price=float(item.get("unit_price", 0)),
            amount=float(item.get("amount", 0)),
        ))

    return ExtractionResult(
        supplier=_field("supplier"),
        invoice_number=_field("invoice_number"),
        invoice_date=_field("invoice_date"),
        currency=_field("currency"),
        total_amount=_field("total_amount"),
        payment_due=_field("payment_due"),
        line_items=line_items,
    )


def _extract_mock(file_path: str) -> ExtractionResult:
    """Return mock extraction data for development/testing.

    Args:
        file_path: Path to the PDF (logged but not read).

    Returns:
        ExtractionResult with realistic dummy data.
    """
    logger.info("Mock extraction for file: %s", file_path)

    line_items: list[LineItemCreate] = [
        LineItemCreate(
            description="IC Chip STC89C52RC (DIP-40)",
            quantity=500,
            unit_price=0.85,
            amount=425.00,
        ),
        LineItemCreate(
            description="Capacitor 100uF 25V Electrolytic",
            quantity=2000,
            unit_price=0.03,
            amount=60.00,
        ),
        LineItemCreate(
            description="PCB Assembly Service (2-layer, 50x80mm)",
            quantity=200,
            unit_price=1.20,
            amount=240.00,
        ),
        LineItemCreate(
            description="Shipping & Handling (DHL Express)",
            quantity=1,
            unit_price=75.00,
            amount=75.00,
        ),
    ]

    return ExtractionResult(
        supplier=FieldConfidence(
            value="Shanghai Electronics Co., Ltd. / \u4e0a\u6d77\u7535\u5b50\u6709\u9650\u516c\u53f8",
            confidence=0.95,
        ),
        invoice_number=FieldConfidence(
            value="INV-2026-SH-004871",
            confidence=0.98,
        ),
        invoice_date=FieldConfidence(
            value="2026-04-18",
            confidence=0.92,
        ),
        currency=FieldConfidence(
            value="USD",
            confidence=0.99,
        ),
        total_amount=FieldConfidence(
            value=800.00,
            confidence=0.96,
        ),
        payment_due=FieldConfidence(
            value="2026-05-18",
            confidence=0.88,
        ),
        line_items=line_items,
    )


def extraction_result_to_flat(result: ExtractionResult) -> dict[str, Any]:
    """Convert an ExtractionResult to a flat dict for database insertion.

    Extracts the .value from each FieldConfidence field so the data
    can be passed directly to database helper functions.

    Args:
        result: The structured extraction result.

    Returns:
        Dict with flat field values ready for DB storage.
    """
    return {
        "supplier": str(result.supplier.value) if result.supplier.value is not None else None,
        "invoice_number": str(result.invoice_number.value) if result.invoice_number.value is not None else None,
        "invoice_date": str(result.invoice_date.value) if result.invoice_date.value is not None else None,
        "currency": str(result.currency.value) if result.currency.value is not None else None,
        "total_amount": float(result.total_amount.value) if result.total_amount.value is not None else None,
        "payment_due": str(result.payment_due.value) if result.payment_due.value is not None else None,
        "supplier_confidence": result.supplier.confidence,
        "invoice_number_confidence": result.invoice_number.confidence,
        "invoice_date_confidence": result.invoice_date.confidence,
        "currency_confidence": result.currency.confidence,
        "total_amount_confidence": result.total_amount.confidence,
        "payment_due_confidence": result.payment_due.confidence,
    }
