"""
Tests for the report API endpoints.

Modul 4: Summary statistics and CSV export.
"""

import csv
import io
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


class TestSummary:
    """Test the summary report endpoint."""

    def test_empty_summary(self, client: TestClient) -> None:
        response = client.get("/api/reports/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 0
        assert data["total_amount"] == 0
        assert data["by_status"] == []
        assert data["by_supplier"] == []
        assert data["by_currency"] == []

    def test_summary_with_invoices(
        self, client: TestClient, sample_pdf: Path
    ) -> None:
        _upload_pdf(client, sample_pdf)
        _upload_pdf(client, sample_pdf)

        response = client.get("/api/reports/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 2
        assert data["total_amount"] > 0
        assert len(data["by_status"]) >= 1
        assert len(data["by_supplier"]) >= 1

    def test_summary_by_status_breakdown(
        self, client: TestClient, sample_pdf: Path
    ) -> None:
        uploaded = _upload_pdf(client, sample_pdf)
        _upload_pdf(client, sample_pdf)
        # Confirm one
        client.put(f"/api/invoices/{uploaded['id']}", json={"status": "confirmed"})

        data = client.get("/api/reports/summary").json()
        statuses = {s["status"]: s["count"] for s in data["by_status"]}
        assert statuses.get("confirmed", 0) == 1
        assert statuses.get("extracted", 0) == 1

    def test_summary_date_filter(
        self, client: TestClient, sample_pdf: Path
    ) -> None:
        _upload_pdf(client, sample_pdf)
        # Mock data has invoice_date 2026-04-18
        # Filter that excludes it
        data = client.get("/api/reports/summary?date_from=2027-01-01").json()
        assert data["total_count"] == 0


class TestCsvExport:
    """Test the CSV export endpoint."""

    def test_export_empty(self, client: TestClient) -> None:
        response = client.get("/api/reports/export/csv")
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]
        # Should still have a header row
        lines = response.text.strip().split("\n")
        assert len(lines) == 1  # Just header

    def test_export_with_data(
        self, client: TestClient, sample_pdf: Path
    ) -> None:
        _upload_pdf(client, sample_pdf)
        _upload_pdf(client, sample_pdf)

        response = client.get("/api/reports/export/csv")
        assert response.status_code == 200

        reader = csv.reader(io.StringIO(response.text))
        rows = list(reader)
        assert len(rows) == 3  # Header + 2 data rows
        assert rows[0][0] == "Invoice ID"
        assert rows[0][2] == "Supplier"

    def test_export_has_correct_filename(self, client: TestClient) -> None:
        response = client.get("/api/reports/export/csv")
        assert "invoices_export.csv" in response.headers.get("content-disposition", "")

    def test_export_date_filter(
        self, client: TestClient, sample_pdf: Path
    ) -> None:
        _upload_pdf(client, sample_pdf)

        # Filter that excludes our mock data
        response = client.get("/api/reports/export/csv?date_from=2027-01-01")
        reader = csv.reader(io.StringIO(response.text))
        rows = list(reader)
        assert len(rows) == 1  # Just header
