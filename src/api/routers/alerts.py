"""
Alert API endpoints.

Modul 5: Overdue payment alerts.
No new tables, no rule engine — computed from existing invoice data.
More alert types added on customer demand (L7: Produkt folgt den Daten).
"""

import logging

from fastapi import APIRouter

from src.api.database import DEFAULT_TENANT, get_overdue_invoices
from src.api.models import AlertResponse, InvoiceListItem

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


def _get_tenant_id() -> str:
    """Get current tenant ID. L3: default for Stufe 1."""
    return DEFAULT_TENANT


@router.get("", response_model=AlertResponse)
async def get_alerts() -> AlertResponse:
    """Get all active alerts for the current tenant.

    Currently returns overdue invoices. More alert types
    will be added based on customer feedback (L7).
    """
    tenant_id = _get_tenant_id()
    overdue_rows = get_overdue_invoices(tenant_id=tenant_id)
    overdue = [InvoiceListItem(**row) for row in overdue_rows]

    return AlertResponse(
        overdue=overdue,
        total_count=len(overdue),
    )
