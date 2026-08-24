# reporter.py
# Builds the formatted text report from all analysis results.
# Pure string formatting

from utils import bar_chart, fmt, rnd


def section(title, width=62):
    """Return a section header line."""
    return [f"\n{title}", "-" * width]


def header_box(title, meta_dict, width=62):
    """Return a boxed header block."""
    lines = [
        "=" * width,
        title.center(width),
        "=" * width,
    ]
    for key, val in meta_dict.items():
        line = f"  {key:<16} : {val}"
        lines.append(line)
    lines.append("=" * width)
    return lines


def format_overview(ov):
    """Format the dataset overview section."""
    lines = section("DATASET OVERVIEW")
    lines.append(f"  Rows              : {fmt(ov['rows'])}")
    lines.append(f"  Columns           : {ov['columns']}")
    lines.append(f"  Total cells       : {fmt(ov['total_cells'])}")
    lines.append(f"  Total nulls       : {fmt(ov['total_nulls'])}")
    flag = "  [!]" if ov["null_pct"] > 5 else ""
    lines.append(f"  Overall null pct  : {ov['null_pct']}%{flag}")
    lines.append(f"\n  Column type breakdown:")
    for dtype, count in sorted(ov["dtype_counts"].items()):
        lines.append(f"    {dtype:<20} : {count}")
    if ov["pk_candidates"]:
        lines.append(f"\n Primary key candidates : {ov['pk_candidates']}")
    if ov["constant_cols"]:
        lines.append(f"  Constant columns      : {ov['constant_cols']}  [!]")
    return lines


def format_column(col_name, stats):
    """Format one column profile block."""
    dtype     = stats.get("dtype", "unknown")
    null_flag = "  [!]" if stats.get("null_pct", 0) > 0 else ""

    lines = [
        f"\n   Column : {col_name}",
        f"     {'-' * 44}",
        f"     type       : {dtype}",
        f"     nulls      : {stats.get('null_count', 0)}"
        f" ({stats.get('null_pct', 0)}%){null_flag}",
        f"     unique     : {stats.get('unique', 0)}"
        f" ({stats.get('unique_pct', 0)}%)",
    ]

    if dtype in ("integer", "float"):
        lines.append(f"    min / max  : {stats.get('min')} / {stats.get('max')}")
        lines.append(f"    mean       : {stats.get('mean')}")
        lines.append(f"    median     : {stats.get('median')}")
        lines.append(f"    std dev    : {stats.get('std_dev')}")
        lines.append(f"    Q1 / Q3    : {stats.get('q1')} / {stats.get('q3')}")
        oc = stats.get("outlier_count", 0)
        if oc > 0:
            lines.append(f"    outliers   : {oc} ({stats.get('outlier_pct')}%) [!]")
            lines.append(f"    outlier eg : {stats.get('outlier_sample', []) [:3]}")

    elif dtype == "text":
        lines.append(
            f" length        : "
            f"{stats.get('min_length')} - {stats.get('max_length')} "
            f"(avg {stats.get('avg_length')})"
        )
        top = stats.get("top_values", [])
        if top:
            max_cnt = top[0][1]
            lines.append("    top values :")
            for val, cnt in top[:4]:
                bar = bar_chart(cnt, max_cnt, width=10)
                lines.append(f"      {str(val)[:22]:<24} {bar} ({cnt})")

    elif dtype == "boolean":
        tc = stats.get("true_count", 0)
        fc = stats.get("false_count", 0)
        tp = stats.get("true_pct", 0)
        lines.append(f"    true       : {tc} ({tp}%)")
        lines.append(f"    false      : {fc} ({round(100 - tp, 1)}%)")

    return lines


def format_alerts(alerts):
    """Format quality alert section."""
    lines = section("DATA QUALITY ALERTS")
    ICONS = {
        "ERROR" : "[ERROR]",
        "WARN"  : "[WARN] ",
        "INFO"  : "[INFO] ",
        "OK"    : "[OK] ",
    }
    for severity in ("ERROR", "WARN", "INFO", "OK"):
        for sev, col, msg in alerts:
            if sev == severity:
                lines.append(f"   {ICONS.get(sev, '?')}  [{col}]  {msg}")
    return lines


def format_correlations(corr_result):
    """Format top correlation pairs section."""
    lines = section("TOP CORRELATIONS (Pearson r)")
    if not corr_result:
        lines.append("  No numeric column pairs to compare.")
        return lines

    sorted_corr = sorted(
        corr_result.items(),
        key=lambda x: abs(x[1]["r"]),
        reverse=True
    )

    for (ca, cb), data in sorted_corr[:5]:
        r   = data["r"]
        lbl = data["label"]
        bar = bar_chart(abs(r), 1.0, width=12)
        lines.append(f"  {ca}  <->  {cb}")
        lines.append(f"    r = {r:>7}   {bar}   {lbl}")

    return lines


def format_quality_summary(counts):
    """Format the final quality score block."""
    total  = sum(counts.values())
    passed = counts.get("OK", 0)
    score  = round(passed / max(1, total) * 100, 1)
    grade  = (
        "Excellent" if score >= 90 else
        "Good"      if score >= 75 else
        "Fair"      if score >=50 else
        "Needs Work"
    )
    lines = section("QUALITY SUMMARY")
    lines.append(f"  [ERROR]  : {counts.get('ERROR', 0)}")
    lines.append(f"  [WARN]   : {counts.get('WARN',  0)}")
    lines.append(f"  [INFO]   : {counts.get('INFO',  0)}")
    lines.append(f"  [OK]     : {counts.get('OK',    0)}")
    lines.append(f"\n  Quality score : {score}% - {grade}")
    return lines


def build_report(dataset_name, overview, profiles, alerts, alert_counts, correlations):
    """Assemble the complete report as a single string."""
    lines = header_box(
        "DataSleuth  -  Data Quality Report",
        {
            "Dataset" : dataset_name,
            "Rows"    : fmt(overview["rows"]),
            "Columns" : overview["columns"],
        }
    )
    lines.extend(format_overview(overview))
    lines.extend(section("COLUMN PROFILES"))
    for col_name, stats in profiles.items():
        lines.extend(format_column(col_name, stats))
    lines.extend(format_alerts(alerts))
    lines.extend(format_correlations(correlations))
    lines.extend(format_quality_summary(alert_counts))
    return "\n".join(lines)