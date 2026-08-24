# main.py - DataSleuth entry point

from reader   import parse_csv, preview
from profiler import profile_dataset, dataset_overview, find_correlations
from quality  import run_all_checks, count_alerts
from reporter import build_report


# ── Sample data embedded as a string ──────────────────────────────────────────
# In a real projrct : get this string from an API response, user paste, or
# any other source, Replace SAMPLE_DATA with any CSV-formatted string.
SAMPLE_DATA = """customer_id,name,age,city,score,revenue,email,active
1001,Alice Johnson,28,Hyderabad,92,4500.00,alice@gmail.com,true
1002,Bob Smith,35,Mumbai,78,2300.50,bob@yahoo.com,true
1003,Carol White,22,Delhi,85,3100.00,carol@hotmail.com,false
1004,Dave Brown,41,Hyderabad,90,5200.75,dave@gmail.com,true
1005,Eve Davis,29,Bangalore,67,1800.00,eve@gmail.com,true
1006,Frank Wilson,38,Mumbai,82,2900.00,frank_wilson,false
1007,,31,Chennai,74,2100.00,gary@test.com,true
1008,Hank Miller,55,Delhi,95,6800.50,hank@company.com,true
1009,Iris Taylor,26,Hyderabad,88,3700.00,iris@gmail.com,true
1010,Jack Moore,33,Mumbai,71,2400.00,jack@yahoo.com,true
1011,Kate Anderson,45,Bangalore,93,5500.00,kate@gmail.com,true
1012,Leo Thomas,-5,Delhi,60,1500.00,leo@test.com,false
1013,Mia Jackson,28,Chennai,76,2600.00,mia@gmail.com,true
1014,Ned Harris,39,Mumbai,84,3200.50,ned@company.com,true
1015,Olivia Martin,31,Hyderabad,91,4800.00,olivia@gmail.com,true"""


def run_datasleuth(
    csv_string   = SAMPLE_DATA,
    dataset_name = "Customer Dataset",
    range_rules  = None,
    email_cols   = None,
):
    """
    Full DataSleuth pipeline.
    Steps:
    1. Parse — convert CSV string to list of dicts
    2. Profile — compute stats for every column
    3. Overview — high-level dataset summary
    4. Quality — run all checks, collect alerts
    5. Correlate — find numeric column relationships
    6. Report — assemble and print the final report
    """
    print(f"\nDataSleuth  |  Profiling: '{dataset_name}'")
    print("-" * 50)

    # Step 1 — Parse
    headers, rows, parse_errors = parse_csv(csv_string)
    if parse_errors:
        for err in parse_errors:
            print(f"  [parse] {err}")
    print(f"  Parsed    : {len(rows)} rows  x  {len(headers)} columns")
    print(f"  Columns   : {headers}")

    # Step 2 — Profile overview
    profiles = profile_dataset(headers, rows)

    # Step 3 — Dataset Overview
    overview = dataset_overview(headers, rows, profiles)

    # Step 4 — Quality checks
    alerts       = run_all_checks(headers, rows, range_rules, email_cols)
    alerts_count = count_alerts(alerts)

    # Step 5 — Correlations
    correlations = find_correlations(headers, rows, profiles)

    # Step 6 — Build and print report
    report = build_report(
        dataset_name = dataset_name,
        overview     = overview,
        profiles     = profiles,
        alerts       = alerts,
        alert_counts = alert_counts,
        correlations = correlations,
    )
    print(report)
    return report

if __name__ == "__main__":
    run_datasleuth(
        range_rules = {
            "age"   : (0, 150),
            "score" : (0, 100),
        },
        email_cols = ["email"],
    )