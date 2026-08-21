# stats.py
# Statistical calculations for DataSleuth.
# Implements: type detection, mean, median, mode, std dev, IQR, outliers.
import math
from utils import is_null, is_num_str, to_float, safe_div, rnd, pct

def detect_type(values):
    """
    Infer the data type of a column from its string values.

    Returns one of:
        'integer' - all non-null values are whole numbers
        'float'   - all non-null values are numbers with decimals
        'boolean' - all non-null values look like true/false/yes/no
        'text'    - mixed or non-numeric content
        'empty'   - no non-null values at all
    """
    non_null = [v for v in values if not is_null(v)]

    if not non_null:
        return "empty"

    bool_set = {"true", "false", "yes", "no", "1", "0", "t", "f", "y", "n"} 
    if all(v.strip().lower() in bool_set for v in non_null):
        return "boolean"

    return "text"

def numeric_stats(numbers):
    """
    Compute descriptive statistics for a list of numbers.

    Uses:
        Mean     = sum / count
        Median   = middle value of sorted list
        Mode     = most frequent value
        Variance = average squared distance from mean
        Std Dev  = square root of variance
        IQR      = Q3 - Q1 (inter-quartile range)
        Outliers = values below Q1-1.5*IQR or above Q3+1.5*IQR
    """
    if not numbers:
        return {}

    n        = len(numbers)
    total    = sum(numbers)
    mean     = total / n
    sorted_n = sorted(numbers)

    mid    =  n // 2
    median = (sorted_n[mid] if n % 2 != 0 else (sorted_n[mid - 1] + sorted_n[mid]) / 2)

    variance = sum((x - mean) ** 2 for x in numbers) / n
    std_dev  = math.sqrt(variance)

    q1_idx   = n // 4
    q3_idx   = (3 * n) // 4
    q1       = sorted_n[q1_idx]
    q3       = sorted_n[q3_idx]
    iqr      = q3 - q1
    lo_fence = q1 - 1.5 * iqr
    hi_fence = q3 + 1.5 * iqr
    outliers = [x for x in numbers if x < lo_fence or x > hi_fence]

    freq = {}
    for x in numbers:
        freq[x] = freq.get(x, 0) + 1
    mode = max(freq, key=freq.get)

    return {
        "count" : n,
        "sum" : rnd(total, 4),
        "mean" : rnd(mean, 4),
        "median" : rnd(median, 4),
        "mode" : mode,
        "std_dev" : rnd(std_dev, 4),
        "min" : sorted_n[0],
        "max" : sorted_n[-1],
        "range" : sorted_n[-1] - sorted_n[0],
        "q1" : q1,
        "q3" : q3,
        "iqr" : rnd(iqr, 4),
        "outlier_count" : len(outliers),
        "outlier_pct" : pct(len(outliers), n),
        "outlier_sample": outliers[:3],
    }

def text_stats(values):
    """Compute stats for a text/string column."""
    if not values:
        return {}

    lengths = [len(v) for v in values]
    freq    = {}
    for v in values:
        freq[v] = freq.get(v, 0) + 1

    top5 = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "count"      : len(values),
        "min_length" : min(lengths),
        "max_length" : max(lengths),
        "avg_length" : rnd(sum(lengths) / len(lengths), 1),
        "unique"     : len(freq),
        "top_values" : top5,
    }

def column_stats(values):
    """
    Master function - compute all stats for one column.
    Calls numeric_stats or text_stats based on detected dtype.
    """
    non_null   = [v for v in values if not is_null(v)]
    null_count = len(values) - len(non_null)
    unique     = set(non_null)

    base = {
        "dtype"      : dtype,
        "total"      : len(values),
        "non_null"   : len(non_null),
        "null_count" : null_count,
        "null_pct"   : pct(null_count, len(values)),
        "unique"     : len(unique_set),
        "unique_pct" : pct(len(unique_set), max(1, len(non_null))),
    }

    if dtype in ("integer", "float"):
        nums = [to_float(v) for v in non_null if is_num_str(v)]
        base.update(numeric_stats(nums))

    elif dtype == "text":
        base.update(text_stats(non_null))

    elif dtype == "boolean":
        true_set   = {"true", "yes", "1", "t", "y"}
        true_count = sum(1 for v in non_null if v.strip().lower() in true_set)
        base["true_count"]  = true_count
        base["false_count"] = len(non_null) - true_count
        base["true_pct"]    = pct(true_count, len(non_null))

    return base