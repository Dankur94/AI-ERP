"""
Match API endpoints.

Modul 3: Compare two invoices, store and retrieve match results.
L3: All endpoints scoped by tenant_id.
"""

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from src.api.database import (
    DEFAULT_TENANT,
    delete_match,
    get_all_matches,
    get_invoice,
    get_match,
    insert_match,
    insert_match_details,
)
from src.api.models import (
    MatchCreate,
    MatchDetail,
    MatchListItem,
    MatchResponse,
)
from src.api.services.matching import compare_invoices

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/matches", tags=["matches"])


def _get_tenant_id() -> str:
    """Get current tenant ID. L3: default for Stufe 1."""
    return DEFAULT_TENANT


@router.post("", response_model=MatchResponse, status_code=201)
async def create_match(body: MatchCreate) -> MatchResponse:
    """Compare two invoices and store the match result.

    Both invoices must exist and belong to the current tenant.
    """
    tenant_id = _get_tenant_id()

    if body.invoice_a_id == body.invoice_b_id:
        raise HTTPException(status_code=400, detail="Cannot match an invoice with itself")

    # Fetch both invoices (with line items for comparison)
    invoice_a = get_invoice(body.invoice_a_id, tenant_id=tenant_id)
    if invoice_a is None:
        raise HTTPException(status_code=404, detail="Invoice A not found")

    invoice_b = get_invoice(body.invoice_b_id, tenant_id=tenant_id)
    if invoice_b is None:
        raise HTTPException(status_code=404, detail="Invoice B not found")

    # Compare
    status, total_diff, details = compare_invoices(invoice_a, invoice_b)

    match_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    # Set match_id on all details
    for d in details:
        d["match_id"] = match_id

    # Determine notes
    mismatches = [d for d in details if d["status"] != "match"]
    notes = None
    if mismatches:
        fields = [d["field_name"] for d in mismatches]
        notes = f"{len(mismatches)} discrepancies: {', '.join(fields[:5])}"
        if len(fields) > 5:
            notes += f" (+{len(fields) - 5} more)"

    # Store
    insert_match(
        match_id=match_id,
        tenant_id=tenant_id,
        invoice_a_id=body.invoice_a_id,
        invoice_b_id=body.invoice_b_id,
        status=status,
        total_diff=total_diff,
        notes=notes,
        created_at=now,
    )
    insert_match_details(details)

    logger.info(
        "Match created: %s — %s (%d details)",
        match_id, status, len(details),
    )

    return MatchResponse(
        id=match_id,
        tenant_id=tenant_id,
        invoice_a_id=body.invoice_a_id,
        invoice_b_id=body.invoice_b_id,
        status=status,
        total_diff=total_diff,
        notes=notes,
        created_at=now,
        details=[MatchDetail(**d) for d in details],
    )


@router.get("", response_model=list[MatchListItem])
async def list_matches() -> list[MatchListItem]:
    """List all matches for the current tenant."""
    tenant_id = _get_tenant_id()
    rows = get_all_matches(tenant_id=tenant_id)
    return [MatchListItem(**row) for row in rows]


@router.get("/{match_id}", response_model=MatchResponse)
async def get_single_match(match_id: str) -> MatchResponse:
    """Get a match with all comparison details."""
    tenant_id = _get_tenant_id()
    match = get_match(match_id, tenant_id=tenant_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")

    raw_details = match.pop("details", [])
    details = [MatchDetail(**d) for d in raw_details]  # type: ignore[arg-type]

    return MatchResponse(**match, details=details)  # type: ignore[arg-type]


@router.delete("/{match_id}", status_code=204)
async def remove_match(match_id: str) -> None:
    """Delete a match and its details."""
    tenant_id = _get_tenant_id()
    deleted = delete_match(match_id, tenant_id=tenant_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Match not found")
