"""
Tests for the matching service and API endpoints.

Modul 3: Invoice comparison, discrepancy detection, tenant isolation.
"""

import uuid
from pathlib import Path

from fastapi.testclient import TestClient

from src.api.database import DEFAULT_TENANT, get_invoice, insert_invoice, insert_line_items
from src.api.services.matching import compare_invoices


def _make_invoice(
    tenant_id: str = DEFAULT_TENANT,
    supplier: str = "Test Corp",
    invoice_number: str = "INV-001",
    total_amount: float = 100.0,
    currency: str = "USD",
    line_items: list[dict] | None = None,
) -> str:
    """Helper: insert a test invoice and return its id."""
    iid = str(uuid.uuid4())
    insert_invoice(
        invoice_id=iid,
        tenant_id=tenant_id,
        filename="test.pdf",
        upload_date="2026-04-20T10:00:00",
        supplier=supplier,
        invoice_number=invoice_number,
        invoice_date="2026-04-20",
        currency=currency,
        total_amount=total_amount,
        payment_due="2026-05-20",
        status="extracted",
        created_at="2026-04-20T10:00:00",
    )
    if line_items:
        items = []
        for li in line_items:
            items.append({
                "id": str(uuid.uuid4()),
                "invoice_id": iid,
                **li,
            })
        insert_line_items(items)
    return iid


class TestCompareInvoices:
    """Test the matching logic directly."""

    def test_identical_invoices_match(self) -> None:
        inv = {
            "supplier": "ACME",
            "invoice_number": "INV-001",
            "invoice_date": "2026-04-20",
            "currency": "USD",
            "total_amount": 500.0,
            "payment_due": "2026-05-20",
            "line_items": [
                {"description": "Widget", "quantity": 10, "unit_price": 50.0, "amount": 500.0},
            ],
        }
        status, diff, details = compare_invoices(inv, inv)
        assert status == "matched"
        assert diff == 0.0
        assert all(d["status"] == "match" for d in details)

    def test_different_total_is_discrepancy(self) -> None:
        inv_a = {
            "supplier": "ACME", "invoice_number": "INV-001",
            "invoice_date": "2026-04-20", "currency": "USD",
            "total_amount": 500.0, "payment_due": "2026-05-20",
            "line_items": [],
        }
        inv_b = {**inv_a, "total_amount": 450.0}
        status, diff, details = compare_invoices(inv_a, inv_b)
        assert status == "discrepancy"
        assert diff == 50.0

    def test_different_supplier_is_discrepancy(self) -> None:
        inv_a = {
            "supplier": "ACME", "invoice_number": "INV-001",
            "invoice_date": "2026-04-20", "currency": "USD",
            "total_amount": 500.0, "payment_due": "2026-05-20",
            "line_items": [],
        }
        inv_b = {**inv_a, "supplier": "Beta Corp"}
        status, _, details = compare_invoices(inv_a, inv_b)
        assert status == "discrepancy"
        supplier_detail = [d for d in details if d["field_name"] == "supplier"][0]
        assert supplier_detail["status"] == "mismatch"

    def test_missing_line_item_detected(self) -> None:
        inv_a = {
            "supplier": "ACME", "invoice_number": "INV-001",
            "invoice_date": "2026-04-20", "currency": "USD",
            "total_amount": 500.0, "payment_due": "2026-05-20",
            "line_items": [
                {"description": "Widget", "quantity": 10, "unit_price": 50.0, "amount": 500.0},
            ],
        }
        inv_b = {**inv_a, "line_items": []}
        status, _, details = compare_invoices(inv_a, inv_b)
        assert status == "discrepancy"
        missing = [d for d in details if d["status"] == "missing_b"]
        assert len(missing) == 1

    def test_line_item_quantity_mismatch(self) -> None:
        items_a = [{"description": "Widget", "quantity": 10, "unit_price": 50.0, "amount": 500.0}]
        items_b = [{"description": "Widget", "quantity": 8, "unit_price": 50.0, "amount": 400.0}]
        inv_a = {
            "supplier": "ACME", "invoice_number": "INV-001",
            "invoice_date": "2026-04-20", "currency": "USD",
            "total_amount": 500.0, "payment_due": "2026-05-20",
            "line_items": items_a,
        }
        inv_b = {**inv_a, "line_items": items_b}
        status, _, details = compare_invoices(inv_a, inv_b)
        assert status == "discrepancy"
        qty_detail = [d for d in details if d["field_name"] == "line_item_1.quantity"][0]
        assert qty_detail["status"] == "mismatch"


class TestMatchAPI:
    """Test the match API endpoints."""

    def _upload_two(self, client: TestClient, sample_pdf: Path) -> tuple[str, str]:
        """Upload two PDFs and return their IDs."""
        with open(sample_pdf, "rb") as f:
            r1 = client.post("/api/invoices/upload", files={"file": ("a.pdf", f, "application/pdf")})
        with open(sample_pdf, "rb") as f:
            r2 = client.post("/api/invoices/upload", files={"file": ("b.pdf", f, "application/pdf")})
        return r1.json()["id"], r2.json()["id"]

    def test_create_match(self, client: TestClient, sample_pdf: Path) -> None:
        id_a, id_b = self._upload_two(client, sample_pdf)
        response = client.post("/api/matches", json={
            "invoice_a_id": id_a,
            "invoice_b_id": id_b,
        })
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "matched"  # Same mock data
        assert len(data["details"]) > 0

    def test_cannot_match_self(self, client: TestClient, sample_pdf: Path) -> None:
        id_a, _ = self._upload_two(client, sample_pdf)
        response = client.post("/api/matches", json={
            "invoice_a_id": id_a,
            "invoice_b_id": id_a,
        })
        assert response.status_code == 400

    def test_match_nonexistent_invoice(self, client: TestClient) -> None:
        response = client.post("/api/matches", json={
            "invoice_a_id": "nonexistent",
            "invoice_b_id": "also-nonexistent",
        })
        assert response.status_code == 404

    def test_list_matches(self, client: TestClient, sample_pdf: Path) -> None:
        id_a, id_b = self._upload_two(client, sample_pdf)
        client.post("/api/matches", json={"invoice_a_id": id_a, "invoice_b_id": id_b})

        response = client.get("/api/matches")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_get_match_detail(self, client: TestClient, sample_pdf: Path) -> None:
        id_a, id_b = self._upload_two(client, sample_pdf)
        created = client.post("/api/matches", json={
            "invoice_a_id": id_a, "invoice_b_id": id_b,
        }).json()

        response = client.get(f"/api/matches/{created['id']}")
        assert response.status_code == 200
        data = response.json()
        assert "details" in data
        assert data["id"] == created["id"]

    def test_delete_match(self, client: TestClient, sample_pdf: Path) -> None:
        id_a, id_b = self._upload_two(client, sample_pdf)
        created = client.post("/api/matches", json={
            "invoice_a_id": id_a, "invoice_b_id": id_b,
        }).json()

        response = client.delete(f"/api/matches/{created['id']}")
        assert response.status_code == 204

        # Verify deleted
        response = client.get(f"/api/matches/{created['id']}")
        assert response.status_code == 404
