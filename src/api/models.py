"""
Pydantic models for the invoice extraction API.

Defines request/response schemas with strict type hints.
"""

from typing import Optional

from pydantic import BaseModel, Field


class LineItem(BaseModel):
    """A single line item on an invoice."""

    id: str
    invoice_id: str
    description: str
    quantity: float
    unit_price: float
    amount: float


class LineItemCreate(BaseModel):
    """Line item data as returned from extraction (no ids yet)."""

    description: str
    quantity: float
    unit_price: float
    amount: float


class FieldConfidence(BaseModel):
    """Confidence score for an extracted field."""

    value: Optional[str | float] = None
    confidence: float = Field(ge=0.0, le=1.0)


class ExtractionResult(BaseModel):
    """Result returned by the extraction service (mock or real)."""

    supplier: FieldConfidence
    invoice_number: FieldConfidence
    invoice_date: FieldConfidence
    currency: FieldConfidence
    total_amount: FieldConfidence
    payment_due: FieldConfidence
    line_items: list[LineItemCreate]


class InvoiceCreate(BaseModel):
    """Fields accepted when manually creating/correcting an invoice."""

    supplier: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    currency: Optional[str] = None
    total_amount: Optional[float] = None
    payment_due: Optional[str] = None
    status: Optional[str] = None


class InvoiceResponse(BaseModel):
    """Full invoice returned to the client."""

    id: str
    tenant_id: str
    filename: str
    upload_date: str
    supplier: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    currency: Optional[str] = None
    total_amount: Optional[float] = None
    payment_due: Optional[str] = None
    supplier_confidence: Optional[float] = None
    invoice_number_confidence: Optional[float] = None
    invoice_date_confidence: Optional[float] = None
    currency_confidence: Optional[float] = None
    total_amount_confidence: Optional[float] = None
    payment_due_confidence: Optional[float] = None
    status: str
    created_at: str
    line_items: list[LineItem] = []


class InvoiceListItem(BaseModel):
    """Abbreviated invoice record for list endpoints (no line items)."""

    id: str
    tenant_id: str
    filename: str
    upload_date: str
    supplier: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    currency: Optional[str] = None
    total_amount: Optional[float] = None
    payment_due: Optional[str] = None
    status: str
    created_at: str


# --- Modul 3: Matching ---


class MatchCreate(BaseModel):
    """Request to create a match between two invoices."""

    invoice_a_id: str
    invoice_b_id: str


class MatchDetail(BaseModel):
    """A single field comparison result."""

    id: str
    match_id: str
    field_name: str
    value_a: Optional[str] = None
    value_b: Optional[str] = None
    status: str  # match, mismatch, missing_a, missing_b


class MatchResponse(BaseModel):
    """Full match result with comparison details."""

    id: str
    tenant_id: str
    invoice_a_id: str
    invoice_b_id: str
    status: str  # matched, discrepancy
    total_diff: Optional[float] = None
    notes: Optional[str] = None
    created_at: str
    details: list[MatchDetail] = []


class MatchListItem(BaseModel):
    """Abbreviated match for list endpoints."""

    id: str
    tenant_id: str
    invoice_a_id: str
    invoice_b_id: str
    supplier_a: Optional[str] = None
    invoice_number_a: Optional[str] = None
    supplier_b: Optional[str] = None
    invoice_number_b: Optional[str] = None
    status: str
    total_diff: Optional[float] = None
    created_at: str


# --- Modul 4: Reports ---


class StatusSummary(BaseModel):
    """Invoice count and total grouped by status."""

    status: str
    count: int
    total: float


class SupplierSummary(BaseModel):
    """Invoice count and total grouped by supplier."""

    supplier: str
    count: int
    total: float


class CurrencySummary(BaseModel):
    """Invoice count and total grouped by currency."""

    currency: str
    count: int
    total: float


class ReportSummary(BaseModel):
    """Summary report with aggregate statistics."""

    total_count: int
    total_amount: float
    by_status: list[StatusSummary]
    by_supplier: list[SupplierSummary]
    by_currency: list[CurrencySummary]


# --- Modul 5: Alerts ---


class AlertResponse(BaseModel):
    """Active alerts for the current tenant."""

    overdue: list["InvoiceListItem"]
    total_count: int
