"""
SQLite database module for invoice storage.

Uses sqlite3 directly — no ORM overhead for Stufe 1.
Database file: src/api/data/invoices.db

L3: All queries filter by tenant_id for customer isolation.
"""

import logging
import sqlite3
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

DB_DIR: Path = Path(__file__).parent / "data"
DB_PATH: Path = DB_DIR / "invoices.db"

# L3: Default tenant for Stufe 1 (single customer).
# In Stufe 2+, tenant_id comes from auth token.
DEFAULT_TENANT: str = "default"


def get_connection() -> sqlite3.Connection:
    """Create and return a database connection with row_factory enabled."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    """Create tables if they do not exist."""
    conn = get_connection()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS invoices (
                id              TEXT PRIMARY KEY,
                tenant_id       TEXT NOT NULL DEFAULT 'default',
                filename        TEXT NOT NULL,
                upload_date     TEXT NOT NULL,
                supplier        TEXT,
                invoice_number  TEXT,
                invoice_date    TEXT,
                currency        TEXT,
                total_amount    REAL,
                payment_due     TEXT,
                supplier_confidence        REAL,
                invoice_number_confidence  REAL,
                invoice_date_confidence    REAL,
                currency_confidence        REAL,
                total_amount_confidence    REAL,
                payment_due_confidence     REAL,
                status          TEXT NOT NULL DEFAULT 'extracted',
                created_at      TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS line_items (
                id          TEXT PRIMARY KEY,
                invoice_id  TEXT NOT NULL,
                description TEXT,
                quantity    REAL,
                unit_price  REAL,
                amount      REAL,
                FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS matches (
                id              TEXT PRIMARY KEY,
                tenant_id       TEXT NOT NULL DEFAULT 'default',
                invoice_a_id    TEXT NOT NULL,
                invoice_b_id    TEXT NOT NULL,
                status          TEXT NOT NULL DEFAULT 'pending',
                total_diff      REAL,
                notes           TEXT,
                created_at      TEXT NOT NULL,
                FOREIGN KEY (invoice_a_id) REFERENCES invoices(id),
                FOREIGN KEY (invoice_b_id) REFERENCES invoices(id)
            );

            CREATE TABLE IF NOT EXISTS match_details (
                id          TEXT PRIMARY KEY,
                match_id    TEXT NOT NULL,
                field_name  TEXT NOT NULL,
                value_a     TEXT,
                value_b     TEXT,
                status      TEXT NOT NULL DEFAULT 'match',
                FOREIGN KEY (match_id) REFERENCES matches(id) ON DELETE CASCADE
            );
        """)
        # L3: Migration — add tenant_id to existing databases
        _migrate_tenant_id(conn)
        conn.commit()
        logger.info("Database tables initialized at %s", DB_PATH)
    finally:
        conn.close()


def _migrate_tenant_id(conn: sqlite3.Connection) -> None:
    """Add tenant_id column if missing (migration for existing DBs)."""
    cursor = conn.execute("PRAGMA table_info(invoices)")
    columns = [row[1] for row in cursor.fetchall()]
    if "tenant_id" not in columns:
        conn.execute(
            "ALTER TABLE invoices ADD COLUMN tenant_id TEXT NOT NULL DEFAULT 'default'"
        )
        logger.info("Migration: added tenant_id column to invoices table")


def insert_invoice(
    invoice_id: str,
    filename: str,
    upload_date: str,
    supplier: Optional[str],
    invoice_number: Optional[str],
    invoice_date: Optional[str],
    currency: Optional[str],
    total_amount: Optional[float],
    payment_due: Optional[str],
    status: str,
    created_at: str,
    tenant_id: str = DEFAULT_TENANT,
    supplier_confidence: Optional[float] = None,
    invoice_number_confidence: Optional[float] = None,
    invoice_date_confidence: Optional[float] = None,
    currency_confidence: Optional[float] = None,
    total_amount_confidence: Optional[float] = None,
    payment_due_confidence: Optional[float] = None,
) -> None:
    """Insert a new invoice record."""
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO invoices
                (id, tenant_id, filename, upload_date, supplier, invoice_number,
                 invoice_date, currency, total_amount, payment_due,
                 supplier_confidence, invoice_number_confidence,
                 invoice_date_confidence, currency_confidence,
                 total_amount_confidence, payment_due_confidence,
                 status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                invoice_id, tenant_id, filename, upload_date, supplier,
                invoice_number, invoice_date, currency, total_amount,
                payment_due, supplier_confidence, invoice_number_confidence,
                invoice_date_confidence, currency_confidence,
                total_amount_confidence, payment_due_confidence,
                status, created_at,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def insert_line_items(items: list[dict[str, object]]) -> None:
    """Insert multiple line items in a single transaction.

    Each dict must contain: id, invoice_id, description, quantity,
    unit_price, amount.
    """
    if not items:
        return
    conn = get_connection()
    try:
        conn.executemany(
            """
            INSERT INTO line_items (id, invoice_id, description, quantity, unit_price, amount)
            VALUES (:id, :invoice_id, :description, :quantity, :unit_price, :amount)
            """,
            items,
        )
        conn.commit()
    finally:
        conn.close()


def get_invoice(invoice_id: str, tenant_id: str = DEFAULT_TENANT) -> Optional[dict[str, object]]:
    """Fetch a single invoice by id, including its line items.

    L3: Filters by tenant_id to prevent cross-tenant access.
    """
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM invoices WHERE id = ? AND tenant_id = ?",
            (invoice_id, tenant_id),
        ).fetchone()
        if row is None:
            return None

        invoice = dict(row)

        items = conn.execute(
            "SELECT * FROM line_items WHERE invoice_id = ? ORDER BY rowid",
            (invoice_id,),
        ).fetchall()
        invoice["line_items"] = [dict(item) for item in items]

        return invoice
    finally:
        conn.close()


def get_all_invoices(tenant_id: str = DEFAULT_TENANT) -> list[dict[str, object]]:
    """Fetch all invoices (without line items) ordered by created_at desc.

    L3: Filters by tenant_id.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM invoices WHERE tenant_id = ? ORDER BY created_at DESC",
            (tenant_id,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def update_invoice(
    invoice_id: str,
    tenant_id: str = DEFAULT_TENANT,
    supplier: Optional[str] = None,
    invoice_number: Optional[str] = None,
    invoice_date: Optional[str] = None,
    currency: Optional[str] = None,
    total_amount: Optional[float] = None,
    payment_due: Optional[str] = None,
    status: Optional[str] = None,
) -> bool:
    """Update an existing invoice. Only non-None fields are updated.

    L3: Filters by tenant_id to prevent cross-tenant updates.
    Returns True if a row was updated, False otherwise.
    """
    fields: list[str] = []
    values: list[object] = []

    update_map: dict[str, object] = {
        "supplier": supplier,
        "invoice_number": invoice_number,
        "invoice_date": invoice_date,
        "currency": currency,
        "total_amount": total_amount,
        "payment_due": payment_due,
        "status": status,
    }

    for field_name, value in update_map.items():
        if value is not None:
            fields.append(f"{field_name} = ?")
            values.append(value)

    if not fields:
        return False

    values.append(invoice_id)
    values.append(tenant_id)

    conn = get_connection()
    try:
        result = conn.execute(
            f"UPDATE invoices SET {', '.join(fields)} WHERE id = ? AND tenant_id = ?",  # noqa: S608
            values,
        )
        conn.commit()
        return result.rowcount > 0
    finally:
        conn.close()


# --- Modul 2: Search & Filter ---


def search_invoices(
    tenant_id: str = DEFAULT_TENANT,
    query: Optional[str] = None,
    supplier: Optional[str] = None,
    status: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    currency: Optional[str] = None,
) -> list[dict[str, object]]:
    """Search invoices with optional filters.

    L3: Always filters by tenant_id.

    Args:
        tenant_id: Customer isolation key.
        query: Free-text search across supplier, invoice_number, filename.
        supplier: Filter by supplier name (partial match).
        status: Filter by exact status.
        date_from: Invoice date >= this value (ISO format).
        date_to: Invoice date <= this value (ISO format).
        currency: Filter by exact currency code.

    Returns:
        List of matching invoices ordered by created_at desc.
    """
    conditions: list[str] = ["tenant_id = ?"]
    params: list[object] = [tenant_id]

    if query:
        conditions.append(
            "(supplier LIKE ? OR invoice_number LIKE ? OR filename LIKE ?)"
        )
        like_val = f"%{query}%"
        params.extend([like_val, like_val, like_val])

    if supplier:
        conditions.append("supplier LIKE ?")
        params.append(f"%{supplier}%")

    if status:
        conditions.append("status = ?")
        params.append(status)

    if date_from:
        conditions.append("invoice_date >= ?")
        params.append(date_from)

    if date_to:
        conditions.append("invoice_date <= ?")
        params.append(date_to)

    if currency:
        conditions.append("currency = ?")
        params.append(currency)

    where_clause = " AND ".join(conditions)

    conn = get_connection()
    try:
        rows = conn.execute(
            f"SELECT * FROM invoices WHERE {where_clause} ORDER BY created_at DESC",  # noqa: S608
            params,
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


# --- Modul 3: Matching ---


def insert_match(
    match_id: str,
    tenant_id: str,
    invoice_a_id: str,
    invoice_b_id: str,
    status: str,
    total_diff: Optional[float],
    notes: Optional[str],
    created_at: str,
) -> None:
    """Insert a new match record."""
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO matches (id, tenant_id, invoice_a_id, invoice_b_id,
                                 status, total_diff, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (match_id, tenant_id, invoice_a_id, invoice_b_id,
             status, total_diff, notes, created_at),
        )
        conn.commit()
    finally:
        conn.close()


def insert_match_details(details: list[dict[str, object]]) -> None:
    """Insert match detail records."""
    if not details:
        return
    conn = get_connection()
    try:
        conn.executemany(
            """
            INSERT INTO match_details (id, match_id, field_name, value_a, value_b, status)
            VALUES (:id, :match_id, :field_name, :value_a, :value_b, :status)
            """,
            details,
        )
        conn.commit()
    finally:
        conn.close()


def get_match(match_id: str, tenant_id: str = DEFAULT_TENANT) -> Optional[dict[str, object]]:
    """Fetch a match with its details.

    L3: Filters by tenant_id.
    """
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM matches WHERE id = ? AND tenant_id = ?",
            (match_id, tenant_id),
        ).fetchone()
        if row is None:
            return None

        match = dict(row)

        details = conn.execute(
            "SELECT * FROM match_details WHERE match_id = ? ORDER BY rowid",
            (match_id,),
        ).fetchall()
        match["details"] = [dict(d) for d in details]

        return match
    finally:
        conn.close()


def get_all_matches(tenant_id: str = DEFAULT_TENANT) -> list[dict[str, object]]:
    """Fetch all matches for a tenant.

    L3: Filters by tenant_id.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT m.*,
                   a.supplier AS supplier_a, a.invoice_number AS invoice_number_a,
                   b.supplier AS supplier_b, b.invoice_number AS invoice_number_b
            FROM matches m
            JOIN invoices a ON m.invoice_a_id = a.id
            JOIN invoices b ON m.invoice_b_id = b.id
            WHERE m.tenant_id = ?
            ORDER BY m.created_at DESC
            """,
            (tenant_id,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def delete_match(match_id: str, tenant_id: str = DEFAULT_TENANT) -> bool:
    """Delete a match and its details (CASCADE).

    L3: Filters by tenant_id.
    """
    conn = get_connection()
    try:
        result = conn.execute(
            "DELETE FROM matches WHERE id = ? AND tenant_id = ?",
            (match_id, tenant_id),
        )
        conn.commit()
        return result.rowcount > 0
    finally:
        conn.close()


# --- Modul 4: Reports ---


def get_invoice_summary(
    tenant_id: str = DEFAULT_TENANT,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> dict[str, object]:
    """Generate summary statistics for invoices.

    L3: Scoped to tenant.

    Returns dict with:
        total_count, total_amount, by_status, by_supplier, by_currency.
    """
    conn = get_connection()
    try:
        conditions: list[str] = ["tenant_id = ?"]
        params: list[object] = [tenant_id]

        if date_from:
            conditions.append("invoice_date >= ?")
            params.append(date_from)
        if date_to:
            conditions.append("invoice_date <= ?")
            params.append(date_to)

        where = " AND ".join(conditions)

        # Total count and amount
        row = conn.execute(
            f"SELECT COUNT(*) as cnt, COALESCE(SUM(total_amount), 0) as total FROM invoices WHERE {where}",  # noqa: S608
            params,
        ).fetchone()
        total_count = row[0]
        total_amount = row[1]

        # By status
        status_rows = conn.execute(
            f"SELECT status, COUNT(*) as cnt, COALESCE(SUM(total_amount), 0) as total FROM invoices WHERE {where} GROUP BY status",  # noqa: S608
            params,
        ).fetchall()
        by_status = [{"status": r[0], "count": r[1], "total": r[2]} for r in status_rows]

        # By supplier (top 20)
        supplier_rows = conn.execute(
            f"SELECT supplier, COUNT(*) as cnt, COALESCE(SUM(total_amount), 0) as total FROM invoices WHERE {where} AND supplier IS NOT NULL GROUP BY supplier ORDER BY total DESC LIMIT 20",  # noqa: S608
            params,
        ).fetchall()
        by_supplier = [{"supplier": r[0], "count": r[1], "total": r[2]} for r in supplier_rows]

        # By currency
        currency_rows = conn.execute(
            f"SELECT currency, COUNT(*) as cnt, COALESCE(SUM(total_amount), 0) as total FROM invoices WHERE {where} AND currency IS NOT NULL GROUP BY currency ORDER BY total DESC",  # noqa: S608
            params,
        ).fetchall()
        by_currency = [{"currency": r[0], "count": r[1], "total": r[2]} for r in currency_rows]

        return {
            "total_count": total_count,
            "total_amount": total_amount,
            "by_status": by_status,
            "by_supplier": by_supplier,
            "by_currency": by_currency,
        }
    finally:
        conn.close()


def get_invoices_for_export(
    tenant_id: str = DEFAULT_TENANT,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> list[dict[str, object]]:
    """Fetch all invoice data for CSV export.

    L3: Scoped to tenant.
    """
    conditions: list[str] = ["tenant_id = ?"]
    params: list[object] = [tenant_id]

    if date_from:
        conditions.append("invoice_date >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("invoice_date <= ?")
        params.append(date_to)

    where = " AND ".join(conditions)

    conn = get_connection()
    try:
        rows = conn.execute(
            f"SELECT id, filename, supplier, invoice_number, invoice_date, currency, total_amount, payment_due, status, created_at FROM invoices WHERE {where} ORDER BY invoice_date DESC",  # noqa: S608
            params,
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


# --- Modul 5: Alerts ---


def get_overdue_invoices(
    tenant_id: str = DEFAULT_TENANT,
    today: Optional[str] = None,
) -> list[dict[str, object]]:
    """Fetch invoices where payment is overdue.

    An invoice is overdue when:
    - payment_due < today
    - status is NOT 'confirmed'

    L3: Scoped to tenant.
    No new tables — computed from existing invoice data.
    """
    if today is None:
        from datetime import date
        today = date.today().isoformat()

    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT * FROM invoices
            WHERE tenant_id = ?
              AND payment_due IS NOT NULL
              AND payment_due < ?
              AND status != 'confirmed'
            ORDER BY payment_due ASC
            """,
            (tenant_id, today),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
