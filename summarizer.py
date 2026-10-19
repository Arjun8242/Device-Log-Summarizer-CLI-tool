"""Device Log Summarizer CLI."""

import argparse
import csv
import json
import math
import sys
from collections import defaultdict

VALID_STATUSES = {"ACTIVE", "WARNING", "ERROR"}
REQUIRED_COLUMNS = {"device_id", "status", "temperature"}
MAX_AVG_TEMP = 80.0


def parse_args():
    parser = argparse.ArgumentParser(description="Summarize device telemetry CSV.")
    parser.add_argument("--input", default="device_telemetry.csv", help="input CSV path")
    parser.add_argument("--output", default="output.json", help="output JSON path")
    return parser.parse_args()


def parse_row(row):
    """Return (device_id, status, temperature) or None if the row is invalid."""
    device_id = (row.get("device_id") or "").strip()
    status = (row.get("status") or "").strip().upper()
    raw_temp = (row.get("temperature") or "").strip()

    if not device_id or status not in VALID_STATUSES:
        return None
    try:
        temperature = float(raw_temp)
    except ValueError:
        return None
    if not math.isfinite(temperature):  # reject nan / inf
        return None
    return device_id, status, temperature


def aggregate(path):
    """Read the CSV and return (per-device stats, number of skipped rows)."""
    stats = defaultdict(lambda: {"total": 0, "temp_sum": 0.0, "errors": 0})
    skipped = 0

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("input file is empty")
        missing = REQUIRED_COLUMNS - {name.strip() for name in reader.fieldnames}
        if missing:
            raise ValueError(f"missing required column(s): {', '.join(sorted(missing))}")

        for row in reader:
            parsed = parse_row(row)
            if parsed is None:
                skipped += 1
                continue
            device_id, status, temperature = parsed
            entry = stats[device_id]
            entry["total"] += 1
            entry["temp_sum"] += temperature
            if status == "ERROR":
                entry["errors"] += 1

    return stats, skipped


def build_results(stats):
    """Compute averages and drop devices with avg temperature above the threshold."""
    results = []
    for device_id in sorted(stats):
        entry = stats[device_id]
        avg = entry["temp_sum"] / entry["total"]
        if avg > MAX_AVG_TEMP:  # strictly greater: exactly 80.0 is kept
            continue
        results.append({
            "device_id": device_id,
            "total_records": entry["total"],
            "avg_temperature": round(avg, 2),
            "error_count": entry["errors"],
        })
    return results


def print_table(results):
    header = f"{'Device':<12}{'Records':>9}{'Avg Temp':>11}{'Errors':>9}"
    print(header)
    print("-" * len(header))
    for r in results:
        print(f"{r['device_id']:<12}{r['total_records']:>9}"
              f"{r['avg_temperature']:>11.2f}{r['error_count']:>9}")


def main():
    args = parse_args()

    try:
        stats, skipped = aggregate(args.input)
    except FileNotFoundError:
        print(f"Error: input file '{args.input}' not found.", file=sys.stderr)
        return 1
    except (ValueError, UnicodeDecodeError, OSError) as exc:
        print(f"Error: could not read '{args.input}': {exc}", file=sys.stderr)
        return 1

    results = build_results(stats)

    try:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
    except OSError as exc:
        print(f"Error: could not write '{args.output}': {exc}", file=sys.stderr)
        return 1

    if results:
        print_table(results)
    else:
        print("No devices to report (no valid rows, or all devices exceeded "
              f"{MAX_AVG_TEMP} avg temperature).")
    print(f"\nSkipped {skipped} invalid row(s). Results written to {args.output}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())