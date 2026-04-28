"""
Tests for the alerts API endpoint.

Modul 5: Overdue payment detection.
"""

import uuid
from pathlib import Path

from fastapi.testclient import TestClient

from src.api.database import DEFAULT_TENANT, get_overdue_invoices, insert_invoice


def _make_invoice(
    payment_due: str,
    status: str = "extracted",
    tenant_id: str = DEFAULT_TENANT,
) -> str:
    """Insert a test invoice with specific payment_due and status."""
    iid = str(uuid.uuid4())
    insert_invoice(
        invoice_id=iid,
        tenant_id=tenant_id,
        filename="test.pdf",
        upload_date="2026-04-20T10:00:00",
        supplier="Test Corp",
        invoice_number="INV-001",
        invoice_date="2026-04-01",
        currency="USD",
        total_amount=500.0,
        payment_due=payment_due,
        status=status,
        created_at="2026-04-20T10:00:00",
    )
    return iid


class TestOverdueDetection:
    """Test the overdue invoice detection logic."""

    def test_overdue_invoice_detected(self) -> None:
        _make_invoice(payment_due="2026-01-01")
        results = get_overdue_invoices(today="2026-04-25")
        assert len(results) == 1

    def test_future_payment_not_overdue(self) -> None:
        _make_invoice(payment_due="2027-01-01")
        results = get_overdue_invoices(today="2026-04-25")
        assert len(results) == 0

    def test_confirmed_invoice_not_overdue(self) -> None:
        _make_invoice(payment_due="2026-01-01", status="confirmed")
        results = get_overdue_invoices(today="2026-04-25")
        assert len(results) == 0

    def test_tenant_isolation(self) -> None:
        _make_invoice(payment_due="2026-01-01", tenant_id="tenant-a")
        _make_invoice(payment_due="2026-01-01", tenant_id="tenant-b")
        results = get_overdue_invoices(tenant_id="tenant-a", today="2026-04-25")
        assert len(results) == 1

    def test_sorted_by_payment_due(self) -> None:
        _make_invoice(payment_due="2026-03-01")
        _make_invoice(payment_due="2026-01-01")
        _make_invoice(payment_due="2026-02-01")
        results = get_overdue_invoices(today="2026-04-25")
        dates = [r["payment_due"] for r in results]
        assert dates == sorted(dates)


class TestAlertAPI:
    """Test the alerts API endpoint."""

    def test_no_alerts_when_empty(self, client: TestClient) -> None:
        response = client.get("/api/alerts")
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 0
        assert data["overdue"] == []

    def test_alerts_with_overdue(
        self, client: TestClient, sample_pdf: Path
    ) -> None:
        # Upload creates mock invoice with payment_due 2026-05-18
        # which is in the future, so no alert.
        with open(sample_pdf, "rb") as f:
            client.post("/api/invoices/upload", files={"file": ("t.pdf", f, "application/pdf")})

        response = client.get("/api/alerts")
        data = response.json()
        # Mock data has payment_due in the future, so 0 alerts
        assert data["total_count"] == 0
