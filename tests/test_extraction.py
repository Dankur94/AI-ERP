"""
Tests for the extraction service.

Tests mock extraction and response parsing.
"""

from src.api.services.extraction import (
    _extract_mock,
    _parse_claude_response,
    extraction_result_to_flat,
)


class TestMockExtraction:

    def test_mock_returns_valid_result(self) -> None:
        result = _extract_mock("/fake/path.pdf")
        assert result.supplier.value is not None
        assert result.supplier.confidence > 0
        assert len(result.line_items) > 0

    def test_mock_has_all_fields(self) -> None:
        result = _extract_mock("/fake/path.pdf")
        assert result.invoice_number.value is not None
        assert result.invoice_date.value is not None
        assert result.currency.value is not None
        assert result.total_amount.value is not None
        assert result.payment_due.value is not None

    def test_extraction_result_to_flat(self) -> None:
        result = _extract_mock("/fake/path.pdf")
        flat = extraction_result_to_flat(result)

        assert isinstance(flat["supplier"], str)
        assert isinstance(flat["total_amount"], float)
        assert isinstance(flat["supplier_confidence"], float)
        assert 0.0 <= flat["supplier_confidence"] <= 1.0


class TestParseClaudeResponse:

    def test_parse_valid_json(self) -> None:
        response = """{
            "supplier": {"value": "Test Corp", "confidence": 0.95},
            "invoice_number": {"value": "INV-001", "confidence": 0.98},
            "invoice_date": {"value": "2026-01-15", "confidence": 0.92},
            "currency": {"value": "USD", "confidence": 0.99},
            "total_amount": {"value": 500.00, "confidence": 0.96},
            "payment_due": {"value": "2026-02-15", "confidence": 0.88},
            "line_items": [
                {"description": "Widget", "quantity": 10, "unit_price": 50.0, "amount": 500.0}
            ]
        }"""
        result = _parse_claude_response(response)
        assert result.supplier.value == "Test Corp"
        assert result.total_amount.value == 500.0
        assert len(result.line_items) == 1

    def test_parse_json_with_code_fences(self) -> None:
        response = """```json
{
    "supplier": {"value": "Fenced Corp", "confidence": 0.90},
    "invoice_number": {"value": "INV-002", "confidence": 0.95},
    "invoice_date": {"value": "2026-03-01", "confidence": 0.85},
    "currency": {"value": "HKD", "confidence": 0.99},
    "total_amount": {"value": 1000.0, "confidence": 0.93},
    "payment_due": {"value": "2026-04-01", "confidence": 0.80},
    "line_items": []
}
```"""
        result = _parse_claude_response(response)
        assert result.supplier.value == "Fenced Corp"
        assert result.currency.value == "HKD"

    def test_parse_with_missing_fields(self) -> None:
        response = """{
            "supplier": {"value": "Partial Corp", "confidence": 0.90},
            "invoice_number": null,
            "invoice_date": {"value": "2026-01-01", "confidence": 0.5},
            "currency": {"value": "EUR", "confidence": 0.99},
            "total_amount": {"value": 0, "confidence": 0.0},
            "payment_due": null,
            "line_items": []
        }"""
        result = _parse_claude_response(response)
        assert result.supplier.value == "Partial Corp"
        assert result.invoice_number.confidence == 0.0
        assert result.payment_due.confidence == 0.0
