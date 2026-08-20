# reader.py
# Parses CSV-formatted string data into structured rows.
# No file I/O - caller passes the raw string content.
from utils import is_null

def parse_csv(raw_text, delimiter=",", has_header=True):
    """
    Parse a CSV string into headers and rows.
    
    Args:
        raw_text   : the full CSV content as a single string
        delimiter  : column separator character (default comma)
        has_header : True if first line contains column names

    Returns:
        headers (list) : column name strings
        rows    (list) : list of dicts {col_name: value_string}
        errors  (list) : descriptions of any parsing problems
    """
    headers = []
    rows    = []
    errors  = []

    if not raw_text or not raw_text.strip():
        return [], [], ["Input string is empty"]

    lines = [line for line in raw_text.strip().split("\n") if line.strip()]
    
    if has_header:
        header_parts = lines[0].split(delimiter)
        headers      = [h.strip().strip('"') for h in header_parts]
        data_lines   = lines[1:]
    else:
        first_parts = lines[0].split(delimiter)
        headers     = [f"col_{i}" for i in range(len(first_parts))]
        data_lines  = lines

    for line_num, line in enumerate(data_lines, start=2):
        parts  = line.split(delimiter)
        values = [v.strip().strip('"') for v in parts]

    if len(values) < len(headers):
        values += [""] * (len(headers) - len(values))
    elif len(values) > len(headers):
        values = values[:len(headers)]
        errors.append(f"Row {line_num}: extra columns trimmed")

    return headers, rows, errors

def get_col(rows, col_name):
    """Extract all values of one column as a list of strings."""
    return [row.get(col_name, "") for row in rows]

def preview(rows, n=5):
    """Return the first n rows as a quick peek."""
    return rows[:n]