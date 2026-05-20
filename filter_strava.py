#!/usr/bin/env python3
"""Create curated Strava data for the latest rolling 7-day window.

The script keeps activities from the last 7 days ending on the newest dated
activity found in the data and writes them to curated_strava.json.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path


def parse_activity_date(value):
    """Parse Strava ISO datetime values with optional trailing Z."""
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def get_last_seven_days_range(reference_date):
    """Return start/end dates for the latest rolling 7-day window."""
    window_end = reference_date
    window_start = reference_date - timedelta(days=6)
    return window_start, window_end


def filter_strava_data(input_file, output_file):
    """Filter master history into the latest rolling 7-day window."""
    try:
        print(f"Reading {input_file}...")
        with open(input_file, "r", encoding="utf-8") as f:
            master_data = json.load(f)

        print(f"Total entries in master_history: {len(master_data)}")

        dated_entries = []
        for entry in master_data:
            parsed_date = parse_activity_date(entry.get("activity_date"))
            if parsed_date is not None:
                dated_entries.append((entry, parsed_date))

        print(f"Entries with valid activity_date: {len(dated_entries)}")
        if not dated_entries:
            print("No dated activities found. Writing empty curated file.")
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2, ensure_ascii=False)
            return 0, len(master_data)

        newest_activity_date = max(parsed_date.date() for _, parsed_date in dated_entries)
        week_start, week_end = get_last_seven_days_range(newest_activity_date)

        curated_data = []
        for entry, parsed_date in dated_entries:
            activity_day = parsed_date.date()
            if week_start <= activity_day <= week_end:
                curated_data.append(entry)

        print(f"Selected 7-day window: {week_start.isoformat()} to {week_end.isoformat()}")
        print(f"Entries in selected window: {len(curated_data)}")

        print(f"Writing {output_file}...")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(curated_data, f, indent=2, ensure_ascii=False)

        print(f"✓ Successfully created {output_file}")
        print(f"✓ Filtered {len(curated_data)} entries from {len(master_data)} total entries")

        return len(curated_data), len(master_data)

    except FileNotFoundError as e:
        print(f"✗ Error: File not found - {e}")
        return 0, 0
    except json.JSONDecodeError as e:
        print(f"✗ Error: Invalid JSON - {e}")
        return 0, 0
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return 0, 0

if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent
    input_path = base_dir / "master_history.json"
    output_path = base_dir / "curated_strava.json"

    filter_strava_data(str(input_path), str(output_path))
