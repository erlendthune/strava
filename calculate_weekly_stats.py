#!/usr/bin/env python3
"""Calculate accurate weekly activity stats from curated_strava.json.

Reads individual activities and calculates:
- Total activities
- Unique participants  
- Total distance (meters → km)
- Total moving time (seconds → hours)
- Top 5 participants by activity count
- Activity type mix (top 3)
- Week date range
"""

import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict


def parse_activity_date(value):
    """Parse Strava ISO datetime values."""
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized).date()
    except ValueError:
        return None


def calculate_stats(activities):
    """Calculate statistics from activity list."""
    if not activities:
        return {
            "activities": 0,
            "participants": 0,
            "distance_km": 0.0,
            "moving_hours": 0.0,
            "top_participants": [],
            "activity_type_mix": [],
            "week_label": "No data"
        }
    
    participants = defaultdict(int)
    activity_types = defaultdict(int)
    total_distance_meters = 0.0
    total_moving_seconds = 0.0
    dates = []
    
    for activity in activities:
        # Count participant
        athlete = activity.get("athlete", {})
        firstname = athlete.get("firstname", "Unknown")
        lastname = athlete.get("lastname", "")
        full_name = f"{firstname} {lastname[0] if lastname else 'X'}".strip()
        participants[full_name] += 1
        
        # Count activity type
        sport_type = activity.get("sport_type", "Unknown")
        activity_types[sport_type] += 1
        
        # Sum distance (in meters) and moving time (in seconds)
        total_distance_meters += float(activity.get("distance", 0))
        total_moving_seconds += float(activity.get("moving_time", 0))
        
        # Collect dates
        activity_date = parse_activity_date(activity.get("activity_date"))
        if activity_date:
            dates.append(activity_date)
    
    # Calculate top participants
    top_participants = [
        f"{name} ({count})"
        for name, count in sorted(
            participants.items(),
            key=lambda x: (-x[1], x[0])
        )[:5]
    ]
    
    # Calculate activity type mix
    activity_type_mix = [
        {"type": atype, "count": count}
        for atype, count in sorted(
            activity_types.items(),
            key=lambda x: (-x[1], x[0])
        )[:3]
    ]
    
    # Determine week range
    if dates:
        week_label = f"{min(dates).isoformat()} til {max(dates).isoformat()}"
    else:
        week_label = "No data"
    
    return {
        "activities": len(activities),
        "participants": len(participants),
        "distance_km": round(total_distance_meters / 1000, 1),
        "moving_hours": round(total_moving_seconds / 3600, 1),
        "top_participants": top_participants,
        "activity_type_mix": activity_type_mix,
        "week_label": week_label
    }


def main():
    base_dir = Path(__file__).resolve().parent
    input_file = base_dir / "curated_strava.json"
    
    try:
        print(f"Reading {input_file}...")
        with open(input_file, "r", encoding="utf-8") as f:
            activities = json.load(f)
        
        print(f"Processing {len(activities)} activities...")
        stats = calculate_stats(activities)
        
        print("\n✓ Calculated Stats:")
        print(f"  Activities: {stats['activities']}")
        print(f"  Participants: {stats['participants']}")
        print(f"  Distance: {stats['distance_km']} km")
        print(f"  Moving Time: {stats['moving_hours']} hours")
        print(f"  Week: {stats['week_label']}")
        print(f"  Top Participants: {', '.join(stats['top_participants'][:3])}")
        activity_types_str = ', '.join(f"{t['type']} ({t['count']})" for t in stats['activity_type_mix'])
        print(f"  Activity Types: {activity_types_str}")
        
        # Output stats as JSON to stdout for agent consumption
        print("\nJSON_OUTPUT:")
        print(json.dumps(stats, ensure_ascii=False, indent=2))
        
        return stats
    
    except FileNotFoundError:
        print(f"✗ Error: {input_file} not found")
        return None
    except json.JSONDecodeError as e:
        print(f"✗ Error: Invalid JSON - {e}")
        return None
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return None


if __name__ == "__main__":
    main()
