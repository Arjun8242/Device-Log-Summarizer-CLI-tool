import json
import sys

import matplotlib.pyplot as plt

INPUT_FILE = "output.json"
OUTPUT_FILE = "chart.png"


def load_data(path):
    """Load the JSON results; print an error and exit with code 1 on failure."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: '{path}' not found. Run summarize.py first.", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"Error: '{path}' is not valid JSON: {exc}", file=sys.stderr)
        sys.exit(1)

    if not data:
        print(f"Error: '{path}' contains no devices, nothing to plot.", file=sys.stderr)
        sys.exit(1)

    # Every entry must be an object with a device_id and a numeric avg_temperature.
    for i, entry in enumerate(data):
        valid = (
            isinstance(entry, dict)
            and "device_id" in entry
            and isinstance(entry.get("avg_temperature"), (int, float))
        )
        if not valid:
            print(
                f"Error: entry {i} in '{path}' needs 'device_id' and a numeric "
                "'avg_temperature'.",
                file=sys.stderr,
            )
            sys.exit(1)
    return data


def main():
    data = load_data(INPUT_FILE)

    devices = [d["device_id"] for d in data]
    temps = [d["avg_temperature"] for d in data]

    plt.bar(devices, temps)
    plt.title("Average Temperature per Device")
    plt.xlabel("Device")
    plt.ylabel("Average Temperature (°C)")
    plt.savefig(OUTPUT_FILE)


if __name__ == "__main__":
    main()