"""
Test configuration and shared fixtures.

Uses a separate in-memory SQLite database for test isolation.
"""

import os
import tempfile
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def _isolate_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Use a temporary database for each test (L3: isolation)."""
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("src.api.database.DB_PATH", db_path)
    monkeypatch.setattr("src.api.database.DB_DIR", tmp_path)

    from src.api.database import init_db
    init_db()


@pytest.fixture()
def upload_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Use a temporary upload directory for each test."""
    upload_path = tmp_path / "uploads"
    upload_path.mkdir()
    monkeypatch.setattr("src.api.routers.invoices.UPLOAD_DIR", upload_path)
    return upload_path


@pytest.fixture()
def client(upload_dir: Path) -> TestClient:
    """FastAPI test client with isolated DB and upload dir."""
    from src.api.main import app
    return TestClient(app)


@pytest.fixture()
def sample_pdf(tmp_path: Path) -> Path:
    """Create a minimal valid PDF file for testing."""
    pdf_path = tmp_path / "test_invoice.pdf"
    # Minimal valid PDF
    pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [] /Count 0 >>
endobj
xref
0 3
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
trailer
<< /Size 3 /Root 1 0 R >>
startxref
109
%%EOF"""
    pdf_path.write_bytes(pdf_content)
    return pdf_path
