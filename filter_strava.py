#!/usr/bin/env python3
"""
Filter Strava master_history.json to only include entries with non-null activity_date.
Creates curated_strava.json with only recent dated activities.
"""

import json
from datetime import datetime

def filter_strava_data(input_file, output_file):
    """
    Read master_history.json and filter for entries where activity_date is NOT null.
    
    Args:
        input_file: Path to master_history.json
        output_file: Path to save curated_strava.json
    """
    try:
        # Read the master history
        print(f"Reading {input_file}...")
        with open(input_file, 'r', encoding='utf-8') as f:
            master_data = json.load(f)
        
        print(f"Total entries in master_history: {len(master_data)}")
        
        # Filter entries where activity_date is NOT null
        curated_data = [entry for entry in master_data if entry.get('activity_date') is not None]
        
        print(f"Entries with non-null activity_date: {len(curated_data)}")
        
        # Get date range
        if curated_data:
            dates = [e['activity_date'] for e in curated_data if e.get('activity_date')]
            min_date = min(dates)
            max_date = max(dates)
            print(f"Date range: {min_date} to {max_date}")
        
        # Save to curated file
        print(f"Writing {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(curated_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Successfully created {output_file}")
        print(f"✓ Filtered {len(curated_data)} entries from {len(master_data)} total")
        
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
    input_path = "c:/git/strava/master_history.json"
    output_path = "c:/git/strava/curated_strava.json"
    
    filter_strava_data(input_path, output_path)
