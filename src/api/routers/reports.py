"""
Report API endpoints.

Modul 4: Summary statistics and CSV export.
L3: All endpoints scoped by tenant_id.
L4: CSV for Stufe 1, PDF/Excel later.
"""

import csv
import io
import logging
from typing import Optional

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from src.api.database import (
    DEFAULT_TENANT,
    get_invoice_summary,
    get_invoices_for_export,
)
from src.api.models import ReportSummary

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reports", tags=["reports"])


def _get_tenant_id() -> str:
    """Get current tenant ID. L3: default for Stufe 1."""
    return DEFAULT_TENANT


@router.get("/summary", response_model=ReportSummary)
async def summary(
    date_from: Optional[str] = Query(None, description="Filter from date (ISO)"),
    date_to: Optional[str] = Query(None, description="Filter to date (ISO)"),
) -> ReportSummary:
    """Get invoice summary statistics.

    Returns total count, total amount, breakdowns by status/supplier/currency.
    """
    tenant_id = _get_tenant_id()
    data = get_invoice_summary(
        tenant_id=tenant_id,
        date_from=date_from,
        date_to=date_to,
    )
    return ReportSummary(**data)  # type: ignore[arg-type]


@router.get("/export/csv")
async def export_csv(
    date_from: Optional[str] = Query(None, description="Filter from date (ISO)"),
    date_to: Optional[str] = Query(None, description="Filter to date (ISO)"),
) -> StreamingResponse:
    """Export invoices as CSV file.

    L4: CSV for Stufe 1. PDF/Excel export in later stages.
    """
    tenant_id = _get_tenant_id()
    invoices = get_invoices_for_export(
        tenant_id=tenant_id,
        date_from=date_from,
        date_to=date_to,
    )

    # Build CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "Invoice ID", "Filename", "Supplier", "Invoice Number",
        "Invoice Date", "Currency", "Total Amount", "Payment Due",
        "Status", "Created At",
    ])

    # Data rows
    for inv in invoices:
        writer.writerow([
            inv.get("id", ""),
            inv.get("filename", ""),
            inv.get("supplier", ""),
            inv.get("invoice_number", ""),
            inv.get("invoice_date", ""),
            inv.get("currency", ""),
            inv.get("total_amount", ""),
            inv.get("payment_due", ""),
            inv.get("status", ""),
            inv.get("created_at", ""),
        ])

    output.seek(0)

    logger.info("CSV export: %d invoices", len(invoices))

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=invoices_export.csv",
        },
    )
