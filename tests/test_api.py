"""
Tests for the FastAPI endpoints.

Covers upload, listing, search, update, and PDF serving.
L3: Verifies tenant isolation at the API level.
"""

from pathlib import Path

from fastapi.testclient import TestClient


def _upload_pdf(client: TestClient, sample_pdf: Path) -> dict:
    """Helper: upload a PDF and return the response JSON."""
    with open(sample_pdf, "rb") as f:
        response = client.post(
            "/api/invoices/upload",
            files={"file": ("test.pdf", f, "application/pdf")},
        )
    assert response.status_code == 201
    return response.json()


class TestHealthCheck:

    def test_health_returns_ok(self, client: TestClient) -> None:
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


class TestUpload:

    def test_upload_pdf_returns_extracted_data(
        self, client: TestClient, sample_pdf: Path
    ) -> None:
        data = _upload_pdf(client, sample_pdf)
        assert "id" in data
        assert data["status"] == "extracted"
        assert data["tenant_id"] == "default"
        assert data["supplier"] is not None

    def test_upload_non_pdf_rejected(self, client: TestClient) -> None:
        response = client.post(
            "/api/invoices/upload",
            files={"file": ("test.txt", b"hello", "text/plain")},
        )
        assert response.status_code == 400

    def test_upload_creates_line_items(
        self, client: TestClient, sample_pdf: Path
    ) -> None:
        data = _upload_pdf(client, sample_pdf)
        assert len(data["line_items"]) > 0


class TestListAndGet:

    def test_list_invoices(
        self, client: TestClient, sample_pdf: Path
    ) -> None:
        _upload_pdf(client, sample_pdf)
        _upload_pdf(client, sample_pdf)

        response = client.get("/api/invoices")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_single_invoice(
        self, client: TestClient, sample_pdf: Path
    ) -> None:
        uploaded = _upload_pdf(client, sample_pdf)
        response = client.get(f"/api/invoices/{uploaded['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == uploaded["id"]
        assert "line_items" in data

    def test_get_nonexistent_returns_404(self, client: TestClient) -> None:
        response = client.get("/api/invoices/nonexistent-id")
        assert response.status_code == 404


class TestUpdate:

    def test_update_invoice_fields(
        self, client: TestClient, sample_pdf: Path
    ) -> None:
        uploaded = _upload_pdf(client, sample_pdf)
        response = client.put(
            f"/api/invoices/{uploaded['id']}",
            json={"supplier": "Corrected Supplier Name"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["supplier"] == "Corrected Supplier Name"
        assert data["status"] == "corrected"

    def test_confirm_invoice(
        self, client: TestClient, sample_pdf: Path
    ) -> None:
        uploaded = _upload_pdf(client, sample_pdf)
        response = client.put(
            f"/api/invoices/{uploaded['id']}",
            json={"status": "confirmed"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "confirmed"


class TestSearch:
    """Modul 2: Search endpoint tests."""

    def test_search_no_params_returns_all(
        self, client: TestClient, sample_pdf: Path
    ) -> None:
        _upload_pdf(client, sample_pdf)
        _upload_pdf(client, sample_pdf)

        response = client.get("/api/invoices/search")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_search_by_query(
        self, client: TestClient, sample_pdf: Path
    ) -> None:
        _upload_pdf(client, sample_pdf)
        # Mock extraction always returns "Shanghai Electronics"
        response = client.get("/api/invoices/search?q=Shanghai")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_search_by_status(
        self, client: TestClient, sample_pdf: Path
    ) -> None:
        uploaded = _upload_pdf(client, sample_pdf)
        # Confirm one invoice
        client.put(
            f"/api/invoices/{uploaded['id']}",
            json={"status": "confirmed"},
        )
        _upload_pdf(client, sample_pdf)  # This stays "extracted"

        confirmed = client.get("/api/invoices/search?status=confirmed")
        assert len(confirmed.json()) == 1

        extracted = client.get("/api/invoices/search?status=extracted")
        assert len(extracted.json()) == 1

    def test_search_no_results(self, client: TestClient) -> None:
        response = client.get("/api/invoices/search?q=nonexistent")
        assert response.status_code == 200
        assert len(response.json()) == 0


class TestPdf:

    def test_get_pdf(
        self, client: TestClient, sample_pdf: Path
    ) -> None:
        uploaded = _upload_pdf(client, sample_pdf)
        response = client.get(f"/api/invoices/{uploaded['id']}/pdf")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"

    def test_get_pdf_nonexistent_returns_404(
        self, client: TestClient
    ) -> None:
        response = client.get("/api/invoices/nonexistent-id/pdf")
        assert response.status_code == 404
