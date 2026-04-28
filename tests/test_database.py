"""
Tests for the database module.

Covers CRUD operations, tenant isolation (L3), and search (Modul 2).
"""

import uuid

from src.api.database import (
    DEFAULT_TENANT,
    get_all_invoices,
    get_invoice,
    insert_invoice,
    insert_line_items,
    search_invoices,
    update_invoice,
)


def _make_invoice_id() -> str:
    return str(uuid.uuid4())


def _insert_test_invoice(
    invoice_id: str | None = None,
    tenant_id: str = DEFAULT_TENANT,
    supplier: str = "Test Supplier",
    invoice_number: str = "INV-001",
    invoice_date: str = "2026-04-20",
    currency: str = "USD",
    total_amount: float = 100.0,
    status: str = "extracted",
) -> str:
    """Helper to insert a test invoice and return its id."""
    iid = invoice_id or _make_invoice_id()
    insert_invoice(
        invoice_id=iid,
        tenant_id=tenant_id,
        filename="test.pdf",
        upload_date="2026-04-20T10:00:00",
        supplier=supplier,
        invoice_number=invoice_number,
        invoice_date=invoice_date,
        currency=currency,
        total_amount=total_amount,
        payment_due="2026-05-20",
        status=status,
        created_at="2026-04-20T10:00:00",
    )
    return iid


class TestInsertAndGet:
    """Test basic CRUD operations."""

    def test_insert_and_get_invoice(self) -> None:
        iid = _insert_test_invoice(supplier="ACME Corp")
        invoice = get_invoice(iid)
        assert invoice is not None
        assert invoice["supplier"] == "ACME Corp"
        assert invoice["tenant_id"] == DEFAULT_TENANT

    def test_get_invoice_includes_line_items(self) -> None:
        iid = _insert_test_invoice()
        items = [
            {
                "id": str(uuid.uuid4()),
                "invoice_id": iid,
                "description": "Widget",
                "quantity": 10,
                "unit_price": 5.0,
                "amount": 50.0,
            },
            {
                "id": str(uuid.uuid4()),
                "invoice_id": iid,
                "description": "Gadget",
                "quantity": 5,
                "unit_price": 10.0,
                "amount": 50.0,
            },
        ]
        insert_line_items(items)

        invoice = get_invoice(iid)
        assert invoice is not None
        assert len(invoice["line_items"]) == 2

    def test_get_nonexistent_invoice_returns_none(self) -> None:
        result = get_invoice("nonexistent-id")
        assert result is None

    def test_get_all_invoices(self) -> None:
        _insert_test_invoice(supplier="First")
        _insert_test_invoice(supplier="Second")
        invoices = get_all_invoices()
        assert len(invoices) == 2

    def test_update_invoice(self) -> None:
        iid = _insert_test_invoice(supplier="Old Name")
        updated = update_invoice(iid, supplier="New Name")
        assert updated is True

        invoice = get_invoice(iid)
        assert invoice is not None
        assert invoice["supplier"] == "New Name"

    def test_update_nonexistent_returns_false(self) -> None:
        result = update_invoice("nonexistent", supplier="Test")
        assert result is False


class TestTenantIsolation:
    """L3: Verify customer isolation works correctly."""

    def test_invoice_belongs_to_tenant(self) -> None:
        iid = _insert_test_invoice(tenant_id="tenant-a")
        # Can find with correct tenant
        assert get_invoice(iid, tenant_id="tenant-a") is not None
        # Cannot find with wrong tenant
        assert get_invoice(iid, tenant_id="tenant-b") is None

    def test_list_only_shows_own_tenant(self) -> None:
        _insert_test_invoice(tenant_id="tenant-a", supplier="A Corp")
        _insert_test_invoice(tenant_id="tenant-b", supplier="B Corp")
        _insert_test_invoice(tenant_id="tenant-a", supplier="A Corp 2")

        a_invoices = get_all_invoices(tenant_id="tenant-a")
        b_invoices = get_all_invoices(tenant_id="tenant-b")

        assert len(a_invoices) == 2
        assert len(b_invoices) == 1

    def test_update_only_affects_own_tenant(self) -> None:
        iid = _insert_test_invoice(tenant_id="tenant-a", supplier="Original")
        # Try to update from wrong tenant
        result = update_invoice(iid, tenant_id="tenant-b", supplier="Hacked")
        assert result is False
        # Original value preserved
        invoice = get_invoice(iid, tenant_id="tenant-a")
        assert invoice is not None
        assert invoice["supplier"] == "Original"

    def test_search_only_returns_own_tenant(self) -> None:
        _insert_test_invoice(tenant_id="tenant-a", supplier="Alpha Inc")
        _insert_test_invoice(tenant_id="tenant-b", supplier="Alpha Ltd")

        results = search_invoices(tenant_id="tenant-a", query="Alpha")
        assert len(results) == 1
        assert results[0]["supplier"] == "Alpha Inc"


class TestSearch:
    """Modul 2: Test search and filter functionality."""

    def test_search_by_supplier(self) -> None:
        _insert_test_invoice(supplier="Shanghai Electronics")
        _insert_test_invoice(supplier="Tokyo Parts Ltd")

        results = search_invoices(query="Shanghai")
        assert len(results) == 1
        assert results[0]["supplier"] == "Shanghai Electronics"

    def test_search_by_invoice_number(self) -> None:
        _insert_test_invoice(invoice_number="INV-2026-001")
        _insert_test_invoice(invoice_number="INV-2026-002")

        results = search_invoices(query="001")
        assert len(results) == 1

    def test_filter_by_status(self) -> None:
        _insert_test_invoice(status="extracted")
        _insert_test_invoice(status="confirmed")

        results = search_invoices(status="confirmed")
        assert len(results) == 1
        assert results[0]["status"] == "confirmed"

    def test_filter_by_date_range(self) -> None:
        _insert_test_invoice(invoice_date="2026-01-15")
        _insert_test_invoice(invoice_date="2026-03-20")
        _insert_test_invoice(invoice_date="2026-06-01")

        results = search_invoices(date_from="2026-02-01", date_to="2026-04-30")
        assert len(results) == 1
        assert results[0]["invoice_date"] == "2026-03-20"

    def test_filter_by_currency(self) -> None:
        _insert_test_invoice(currency="USD")
        _insert_test_invoice(currency="HKD")

        results = search_invoices(currency="HKD")
        assert len(results) == 1
        assert results[0]["currency"] == "HKD"

    def test_combined_filters(self) -> None:
        _insert_test_invoice(supplier="Alpha", status="confirmed", currency="USD")
        _insert_test_invoice(supplier="Alpha", status="extracted", currency="USD")
        _insert_test_invoice(supplier="Beta", status="confirmed", currency="USD")

        results = search_invoices(supplier="Alpha", status="confirmed")
        assert len(results) == 1
        assert results[0]["supplier"] == "Alpha"

    def test_empty_search_returns_all(self) -> None:
        _insert_test_invoice(supplier="One")
        _insert_test_invoice(supplier="Two")

        results = search_invoices()
        assert len(results) == 2

    def test_no_matches_returns_empty(self) -> None:
        _insert_test_invoice(supplier="Existing Corp")

        results = search_invoices(query="NonExistent")
        assert len(results) == 0
