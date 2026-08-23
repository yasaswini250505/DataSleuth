# quality.py
# Data quality checks
# Each check returns (severity, column_name, message)

from utils import is_null, is_num_str, to_float, pct, rnd, safe_div


def check_nulls(values, col):
    """Flag columns with too many missing values."""
    null_count = sum(1 for v in values if is_null(v))
    p          = pct(null_count, len(values))
    if p > 30:
        return ("ERROR", col, f"{p}% nulls - column is mostly empty")
    if p > 10:
        return ("WARN", col, f"{p}% null values present")
    if p > 0:
        return ("INFO", col, f"{null_count} null value(s) ({p}%)")
    return ("OK", col, "No null values")


def check_duplicates(values, col):
    """Flag columns with significant duplicate values."""
    non_null  = [v for v in values if not is_null(v)]
    dup_count = len(non_null) - len(set(non_null))
    p         = pct(dup_count, max(1, len(non_null)))
    if p > 50:
        return ("WARN", col, f"{dup_count} duplicates ({p}%)")
    if dup_count > 0:
        return ("INFO", col, f"{dup_count} duplicate value(s)")
    return ("OK", col, "All values are unique")


def check_whitespace(values, col):
    """Flag values that combine only whitespace."""
    ws_count = sum(1 for v in values if isinstance(v, str) and v != "" and v.strip())
    if ws_count > 0:
        return ("WARN", col, f"{ws_count} whitespace-only value(s)")
    return ("OK", col, "No whitespace issues")


def check_type_consistency(values, col):
    """Flag columns that mix numeric and non-numeric values."""
    non_null = [v for v in values if not is_null(v)]
    if not non_null:
        return ("INFO", col, "No data to check")
    numeric =  sum(1 for v in non_null if is_num_str(v))
    others  = len(non_null) - numeric
    if numeric > 0 and others > 0:
        return ("WARN", col, f"Mixed types - {numeric} numeric, {others} non-numeric")
    return ("OK", col, "Type is consistent")


def check_range(values, col, lo, hi):
    """Flag numeric values that fall outside an expected range."""
    nums    = [to_float(v) for v in values if is_num_str(v)]
    outside = [n for n in nums if n < lo or n > hi]
    if outside:
        return ("ERROR", col, f"{len(outside)} value(s) outside range [{lo}, {hi}]")
    return ("OK", col, f"All values within range [{lo}, {hi}]")


def check_email(values, col):
    """Basic email format check using only string methods."""
    non_null = [v for v in values if not is_null(v)]
    bad = [
        v for v in non_null
        if "@" not in v
        or "." not in v
        or v.startswith("@")
        or v.count("@") != 1
        or v.endswith(".")
    ]
    if bad:
        return ("WARN", col, f"{len(bad)} value(s) with invalid email format")
    return ("OK", col, "All emails look valid")


def run_all_checks(headers, rows, range_rules=None, email_cols=None):
    """Run the full quality check suite on all columns.

    Args:
        headers     : list of column names
        rows        : list of rows dicts
        range_rules : dict {col_name : (min_val, max_val)}
        email_cols  : list of column names to validate as emails
        
    Returns:
        List of (severity, col_name, message) tuples
    """
    alerts      = []
    range_rules = range_rules or {}
    email_cols  = email_cols or []

    for col in headers:
        values = [row.get(col, "") for row in rows]
        alerts.append(check_nulls(values, col))
        alerts.append(check_duplicates(values, col))
        alerts.append(check_whitespace(values, col))
        alerts.append(check_type_consistency(values, col))

        if col in range_rules:
            lo, hi = range_rules[col]
            alerts.append(check_range(values, col, lo, hi))

        if col in email_cols:
            alerts.append(check_email(values, col))

    return alerts


def count_alerts(alerts):
    """Return a count dict: {severity: count}."""
    counts = {"ERROR": 0, "WARN": 0, "INFO": 0, "OK": 0}
    for severity, _, _ in alerts:
        counts[severity] = counts.get(severity, 0) + 1
    return counts