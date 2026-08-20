# utils.py
# Shared helper functions used across all modules.
# Imports: math only 
import math

def is_null(value):
    """Return True if a value presents missing/null data."""
    if value is None:
        return True
    return str(value).strip().lower() in ("", "null", "none", "na", "n/a", "nan", "-")
    
def is_num_str(value):
    """Return True if a string can be converted to a number."""
    v = str(value).strip().lstrip("-")
    if not v:
        return False
    if v.count(".") > 1:
        return False
    return v.replace(".", "").isdigit()

def to_float(value):
    """Convert string to float. Returns None if conversion is not possible."""
    if not is_num_str(value):
        return None
    return float(str(value).strip())

def safe_div(a, b, default=0.0):
    """Divide a by b. Returns default when b is zero."""
    if b == 0:
        return default
    return a / b
    
def rnd(value, dp=2):
    """Round a simple text bar: filled and empty blocks."""
    if max_val == 0:
        return "░" * width
    filled = int(safe_div(value, max_val) * width)
    filled = max(0, min(filled, width))
    return "█" * filled + "░" * (width - filled)

def fmt(n, dp=2):
    """Format a number with commas for readability."""
    if isinstance(n, int):
        return f"{n:,}"
    return f"{n:,.{dp}f}"