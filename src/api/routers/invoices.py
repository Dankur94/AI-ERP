"""
Invoice API endpoints.

Handles upload, listing, search, retrieval, correction, and PDF serving.

L3: All endpoints use tenant_id for customer isolation.
    In Stufe 1, tenant_id defaults to "default".
    In Stufe 2+, it comes from auth middleware.
"""

import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse

from src.api.database import (
    DEFAULT_TENANT,
    get_all_invoices,
    get_invoice,
    insert_invoice,
    insert_line_items,
    search_invoices,
    update_invoice,
)
from src.api.models import (
    InvoiceCreate,
    InvoiceListItem,
    InvoiceResponse,
    LineItem,
)
from src.api.services.extraction import extract_invoice, extraction_result_to_flat

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/invoices", tags=["invoices"])

UPLOAD_DIR: Path = Path(__file__).parent.parent / "storage" / "uploads"


def _get_tenant_id() -> str:
    """Get current tenant ID.

    L3: Stufe 1 uses a default tenant. In Stufe 2+, this will
    read from auth token / request header.
    """
    return DEFAULT_TENANT


@router.post("/upload", response_model=InvoiceResponse, status_code=201)
async def upload_invoice(file: UploadFile) -> InvoiceResponse:
    """Accept a PDF file, run extraction, save to DB, return result."""
    filename = (file.filename or "").lower()
    is_pdf = (
        file.content_type in ("application/pdf", "application/octet-stream")
        or filename.endswith(".pdf")
    )
    if not is_pdf:
        raise HTTPException(
            status_code=400,
            detail=f"Only PDF files are accepted. Got: {file.content_type}",
        )

    tenant_id = _get_tenant_id()
    invoice_id: str = str(uuid.uuid4())
    now: str = datetime.now(timezone.utc).isoformat()

    # Save uploaded file
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    file_path: Path = UPLOAD_DIR / f"{invoice_id}.pdf"
    content: bytes = await file.read()
    file_path.write_bytes(content)
    logger.info("Saved upload to %s (%d bytes)", file_path, len(content))

    # Run extraction
    extraction = extract_invoice(str(file_path))
    flat = extraction_result_to_flat(extraction)

    # Save invoice to DB
    insert_invoice(
        invoice_id=invoice_id,
        tenant_id=tenant_id,
        filename=file.filename or "unknown.pdf",
        upload_date=now,
        supplier=flat["supplier"],
        invoice_number=flat["invoice_number"],
        invoice_date=flat["invoice_date"],
        currency=flat["currency"],
        total_amount=flat["total_amount"],
        payment_due=flat["payment_due"],
        status="extracted",
        created_at=now,
        supplier_confidence=flat["supplier_confidence"],
        invoice_number_confidence=flat["invoice_number_confidence"],
        invoice_date_confidence=flat["invoice_date_confidence"],
        currency_confidence=flat["currency_confidence"],
        total_amount_confidence=flat["total_amount_confidence"],
        payment_due_confidence=flat["payment_due_confidence"],
    )

    # Save line items
    line_item_records: list[dict[str, object]] = []
    for item in extraction.line_items:
        line_item_records.append({
            "id": str(uuid.uuid4()),
            "invoice_id": invoice_id,
            "description": item.description,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "amount": item.amount,
        })
    insert_line_items(line_item_records)

    # Build response
    return InvoiceResponse(
        id=invoice_id,
        tenant_id=tenant_id,
        filename=file.filename or "unknown.pdf",
        upload_date=now,
        supplier=flat["supplier"],
        invoice_number=flat["invoice_number"],
        invoice_date=flat["invoice_date"],
        currency=flat["currency"],
        total_amount=flat["total_amount"],
        payment_due=flat["payment_due"],
        supplier_confidence=flat["supplier_confidence"],
        invoice_number_confidence=flat["invoice_number_confidence"],
        invoice_date_confidence=flat["invoice_date_confidence"],
        currency_confidence=flat["currency_confidence"],
        total_amount_confidence=flat["total_amount_confidence"],
        payment_due_confidence=flat["payment_due_confidence"],
        status="extracted",
        created_at=now,
        line_items=[
            LineItem(**record)  # type: ignore[arg-type]
            for record in line_item_records
        ],
    )


@router.get("", response_model=list[InvoiceListItem])
async def list_invoices() -> list[InvoiceListItem]:
    """List all invoices ordered by creation date (newest first)."""
    tenant_id = _get_tenant_id()
    rows = get_all_invoices(tenant_id=tenant_id)
    return [InvoiceListItem(**row) for row in rows]


@router.get("/search", response_model=list[InvoiceListItem])
async def search(
    q: Optional[str] = Query(None, description="Free-text search across supplier, invoice number, filename"),
    supplier: Optional[str] = Query(None, description="Filter by supplier name (partial match)"),
    status: Optional[str] = Query(None, description="Filter by status: extracted, corrected, confirmed"),
    date_from: Optional[str] = Query(None, description="Invoice date from (ISO format, e.g. 2026-01-01)"),
    date_to: Optional[str] = Query(None, description="Invoice date to (ISO format, e.g. 2026-12-31)"),
    currency: Optional[str] = Query(None, description="Filter by currency code (e.g. USD, HKD)"),
) -> list[InvoiceListItem]:
    """Search and filter invoices.

    Modul 2: Provides full-text search and structured filtering.
    L3: Results are scoped to the current tenant.
    """
    tenant_id = _get_tenant_id()
    rows = search_invoices(
        tenant_id=tenant_id,
        query=q,
        supplier=supplier,
        status=status,
        date_from=date_from,
        date_to=date_to,
        currency=currency,
    )
    return [InvoiceListItem(**row) for row in rows]


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_single_invoice(invoice_id: str) -> InvoiceResponse:
    """Get a single invoice with all its line items."""
    tenant_id = _get_tenant_id()
    invoice = get_invoice(invoice_id, tenant_id=tenant_id)
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")

    raw_items = invoice.pop("line_items", [])
    items: list[LineItem] = [LineItem(**item) for item in raw_items]  # type: ignore[arg-type]

    return InvoiceResponse(**invoice, line_items=items)  # type: ignore[arg-type]


@router.put("/{invoice_id}", response_model=InvoiceResponse)
async def update_single_invoice(
    invoice_id: str,
    body: InvoiceCreate,
) -> InvoiceResponse:
    """Update (correct) an invoice's extracted fields.

    Only non-null fields in the request body are updated.
    If no explicit status is given, the status is set to 'corrected'.
    """
    tenant_id = _get_tenant_id()
    existing = get_invoice(invoice_id, tenant_id=tenant_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Invoice not found")

    update_data = body.model_dump(exclude_none=True)

    # Default to 'corrected' status when user edits fields
    if "status" not in update_data:
        update_data["status"] = "corrected"

    updated: bool = update_invoice(invoice_id=invoice_id, tenant_id=tenant_id, **update_data)
    if not updated and update_data:
        raise HTTPException(status_code=500, detail="Update failed")

    # Re-fetch to return the current state
    refreshed = get_invoice(invoice_id, tenant_id=tenant_id)
    if refreshed is None:
        raise HTTPException(status_code=404, detail="Invoice not found after update")

    raw_items = refreshed.pop("line_items", [])
    items: list[LineItem] = [LineItem(**item) for item in raw_items]  # type: ignore[arg-type]

    return InvoiceResponse(**refreshed, line_items=items)  # type: ignore[arg-type]


@router.get("/{invoice_id}/pdf")
async def get_invoice_pdf(invoice_id: str) -> FileResponse:
    """Serve the original uploaded PDF file for inline display."""
    # L3: Verify the invoice belongs to the current tenant
    tenant_id = _get_tenant_id()
    invoice = get_invoice(invoice_id, tenant_id=tenant_id)
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")

    file_path: Path = UPLOAD_DIR / f"{invoice_id}.pdf"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="PDF file not found")

    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        headers={"Content-Disposition": "inline"},
    )
