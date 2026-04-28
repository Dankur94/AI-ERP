"""
Invoice matching service.

Modul 3: Compares two invoices field-by-field and line-item-by-line-item.
Returns comparison details with match/mismatch status.
"""

import uuid
from typing import Any, Optional


def compare_invoices(
    invoice_a: dict[str, Any],
    invoice_b: dict[str, Any],
) -> tuple[str, Optional[float], list[dict[str, Any]]]:
    """Compare two invoices and return match results.

    Args:
        invoice_a: First invoice dict (with line_items).
        invoice_b: Second invoice dict (with line_items).

    Returns:
        Tuple of (status, total_diff, details_list).
        status: "matched" or "discrepancy"
        total_diff: Difference in total_amount (a - b), None if both null.
        details_list: List of dicts for match_details table.
    """
    details: list[dict[str, Any]] = []
    has_mismatch = False
    match_id_placeholder = ""  # Will be set by caller

    # Compare header fields
    header_fields = [
        ("supplier", str),
        ("invoice_number", str),
        ("invoice_date", str),
        ("currency", str),
        ("total_amount", float),
        ("payment_due", str),
    ]

    for field_name, _ in header_fields:
        val_a = invoice_a.get(field_name)
        val_b = invoice_b.get(field_name)

        str_a = _to_str(val_a)
        str_b = _to_str(val_b)

        if val_a is None and val_b is None:
            field_status = "match"
        elif val_a is None:
            field_status = "missing_a"
            has_mismatch = True
        elif val_b is None:
            field_status = "missing_b"
            has_mismatch = True
        elif str_a == str_b:
            field_status = "match"
        else:
            field_status = "mismatch"
            has_mismatch = True

        details.append({
            "id": str(uuid.uuid4()),
            "match_id": match_id_placeholder,
            "field_name": field_name,
            "value_a": str_a,
            "value_b": str_b,
            "status": field_status,
        })

    # Compare line items
    items_a = invoice_a.get("line_items", [])
    items_b = invoice_b.get("line_items", [])

    matched_b: set[int] = set()

    for i, item_a in enumerate(items_a):
        best_match_idx = _find_best_match(item_a, items_b, matched_b)

        if best_match_idx is not None:
            matched_b.add(best_match_idx)
            item_b = items_b[best_match_idx]

            # Compare each line item field
            for lf in ["description", "quantity", "unit_price", "amount"]:
                va = _to_str(item_a.get(lf))
                vb = _to_str(item_b.get(lf))
                ls = "match" if va == vb else "mismatch"
                if ls == "mismatch":
                    has_mismatch = True
                details.append({
                    "id": str(uuid.uuid4()),
                    "match_id": match_id_placeholder,
                    "field_name": f"line_item_{i + 1}.{lf}",
                    "value_a": va,
                    "value_b": vb,
                    "status": ls,
                })
        else:
            # Line item in A but not in B
            has_mismatch = True
            details.append({
                "id": str(uuid.uuid4()),
                "match_id": match_id_placeholder,
                "field_name": f"line_item_{i + 1}",
                "value_a": _to_str(item_a.get("description")),
                "value_b": None,
                "status": "missing_b",
            })

    # Line items in B but not matched
    for j, item_b in enumerate(items_b):
        if j not in matched_b:
            has_mismatch = True
            details.append({
                "id": str(uuid.uuid4()),
                "match_id": match_id_placeholder,
                "field_name": f"line_item_extra_{j + 1}",
                "value_a": None,
                "value_b": _to_str(item_b.get("description")),
                "status": "missing_a",
            })

    # Calculate total difference
    total_a = invoice_a.get("total_amount")
    total_b = invoice_b.get("total_amount")
    total_diff: Optional[float] = None
    if total_a is not None and total_b is not None:
        total_diff = round(float(total_a) - float(total_b), 2)

    status = "discrepancy" if has_mismatch else "matched"

    return status, total_diff, details


def _to_str(value: Any) -> Optional[str]:
    """Convert a value to string for comparison, None stays None."""
    if value is None:
        return None
    return str(value)


def _find_best_match(
    item: dict[str, Any],
    candidates: list[dict[str, Any]],
    already_matched: set[int],
) -> Optional[int]:
    """Find the best matching line item by description.

    Simple exact match for Stufe 1. Fuzzy matching can be added later (L4).
    """
    desc = (item.get("description") or "").strip().lower()

    for i, candidate in enumerate(candidates):
        if i in already_matched:
            continue
        c_desc = (candidate.get("description") or "").strip().lower()
        if desc == c_desc:
            return i

    # Fallback: partial match
    for i, candidate in enumerate(candidates):
        if i in already_matched:
            continue
        c_desc = (candidate.get("description") or "").strip().lower()
        if desc and c_desc and (desc in c_desc or c_desc in desc):
            return i

    return None
