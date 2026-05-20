#!/usr/bin/env python3
"""Generate dialogue content for the rolling 7-day Strava report.

This script refreshes curated_strava.json for the latest rolling 7-day window and writes
weekly_dialogue.json containing both summary texts and display stats.
"""

import json
import random
from datetime import datetime
from pathlib import Path

from filter_strava import filter_strava_data, parse_activity_date


HAYES_SLOGANS = [
    "Ingen unnskyldninger. Bare oppmøte, trykk og fremdrift.",
    "Disiplin først. Resultater etterpå.",
    "Svette i dag er styrke i morgen.",
    "Hold linja. Fullfør økta. Gjenta.",
    "Tempo bygger moral. Vaner bygger lag.",
    "Ingen glans uten innsats. Ingen innsats uten plan.",
    "Trykk på. Still opp. Lever igjen i morgen.",
]

TEACHER_SLOGANS = [
    "Små steg, ofte nok, blir store endringer over tid.",
    "Det viktigste er ikke perfekt innsats, men jevn innsats.",
    "Gode vaner vokser best når de får tid og støtte.",
    "Hver økt teller, og hver økt gjør neste økt litt lettere.",
    "Når flere heier på hverandre, blir terskelen lavere for alle.",
    "Mestring bygges i det stille, én gjennomført dag av gangen.",
    "Rytme slår skippertak når målet er varig framgang.",
]


def load_json(path):
    with open(path, "r", encoding="utf-8") as file_handle:
        return json.load(file_handle)


def save_json(path, payload):
    with open(path, "w", encoding="utf-8") as file_handle:
        json.dump(payload, file_handle, indent=2, ensure_ascii=False)


def with_random_slogan(base_text, slogans):
    """Append one random closing slogan to the generated summary."""
    return f"{base_text} {random.choice(slogans)}"


def format_week_label(activities):
    dates = [parse_activity_date(item.get("activity_date")) for item in activities]
    valid_dates = [item.date() for item in dates if item is not None]
    if not valid_dates:
        return "Ingen datert aktivitet"

    start_date = min(valid_dates).isoformat()
    end_date = max(valid_dates).isoformat()
    return f"{start_date} til {end_date}"


def build_stats(activities):
    participants = {}
    activity_types = {}
    total_distance_meters = 0.0
    total_moving_seconds = 0.0

    for activity in activities:
        athlete_name = activity.get("athlete", {}).get("firstname") or "Ukjent"
        participants[athlete_name] = participants.get(athlete_name, 0) + 1

        activity_type = activity.get("sport_type") or activity.get("type") or "Annet"
        activity_types[activity_type] = activity_types.get(activity_type, 0) + 1

        total_distance_meters += float(activity.get("distance") or 0)
        total_moving_seconds += float(activity.get("moving_time") or 0)

    top_participants = [
        f"{name} ({count})"
        for name, count in sorted(
            participants.items(),
            key=lambda item: (-item[1], item[0].lower()),
        )[:5]
    ]
    type_mix = [
        {"type": name, "count": count}
        for name, count in sorted(
            activity_types.items(),
            key=lambda item: (-item[1], item[0].lower()),
        )
    ]

    return {
        "activities": len(activities),
        "participants": len(participants),
        "distance_km": round(total_distance_meters / 1000, 1),
        "moving_hours": round(total_moving_seconds / 3600, 1),
        "top_participants": top_participants,
        "activity_type_mix": type_mix,
    }


def build_hayes_text(stats):
    if not stats["activities"]:
        return with_random_slogan(
            "Hør her: de siste 7 dagene inneholder null registrerte aktiviteter. "
            "Det betyr ingen rytme, ingen oppfølging og ingen fremdrift. "
            "Neste uke trenger en enkel plan med faste dager, tydelig oppmøte "
            "og null tvil om hvem som stiller.",
            HAYES_SLOGANS,
        )

    top_participants = ", ".join(stats["top_participants"]) or "ingen tydelige bidragsytere"
    leading_types = ", ".join(
        f"{entry['type']} ({entry['count']})" for entry in stats["activity_type_mix"][:3]
    ) or "ingen tydelig aktivitetsmiks"

    if stats["participants"] and (stats["activities"] / stats["participants"]) < 2:
        discipline_line = (
            "Det er for lav frekvens per person. Disiplin handler ikke om toppdager, "
            "det handler om å stille jevnt."
        )
    else:
        discipline_line = (
            "Oppmøtet er brukbart, men standarden må holdes oppe uten slark og hull i uka."
        )

    return with_random_slogan(
        f"Hør her: {stats['activities']} aktiviteter fra {stats['participants']} personer de siste 7 dagene. "
        f"{discipline_line} Totalen landet på {stats['distance_km']:.1f} km og "
        f"{stats['moving_hours']:.1f} timer. Toppen nå er {top_participants}. "
        f"Aktivitetsmiksen viser {leading_types}. Det er godkjent innsats, men ikke ferdig arbeid. "
        "Neste uke trenger klarere planer, flere repeterte økter og mindre tilfeldig drift.",
        HAYES_SLOGANS,
    )


def build_teacher_text(stats):
    if not stats["activities"]:
        return with_random_slogan(
            "De siste 7 dagene mangler registrerte aktiviteter, og det kan brukes konstruktivt. "
            "Start med en liten terskel: avtal to eller tre korte økter som er lette å gjennomføre. "
            "Det viktigste nå er å komme i gang igjen med en vane som varer.",
            TEACHER_SLOGANS,
        )

    top_participants = ", ".join(stats["top_participants"]) or "hele gruppen"
    leading_types = ", ".join(
        f"{entry['type']} ({entry['count']})" for entry in stats["activity_type_mix"][:3]
    ) or "variert aktivitet"

    return with_random_slogan(
        f"De siste 7 dagene viser {stats['activities']} aktiviteter fordelt på {stats['participants']} personer. "
        f"Til sammen ble det {stats['distance_km']:.1f} km og {stats['moving_hours']:.1f} timer bevegelse. "
        f"Det gir et fint bilde av stabil innsats, spesielt fra {top_participants}. "
        f"Aktivitetsmiksen med {leading_types} viser variasjon og flere innganger til mestring. "
        "Neste steg er å bevare rytmen, dele gode vaner og gjøre det enkelt for flere å bli med jevnlig.",
        TEACHER_SLOGANS,
    )


def generate_dialogue_payload(curated_file):
    activities = load_json(curated_file)
    stats = build_stats(activities)
    return {
        "week_label": format_week_label(activities),
        "generated_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "stats": stats,
        "hayes": build_hayes_text(stats),
        "teacher": build_teacher_text(stats),
    }


def main():
    base_dir = Path(__file__).resolve().parent
    master_history_file = base_dir / "master_history.json"
    curated_file = base_dir / "curated_strava.json"
    dialogue_file = base_dir / "weekly_dialogue.json"

    filter_strava_data(str(master_history_file), str(curated_file))
    payload = generate_dialogue_payload(curated_file)
    save_json(dialogue_file, payload)

    print(f"Wrote {dialogue_file}")
    print(f"Week: {payload['week_label']}")
    print(f"Activities: {payload['stats']['activities']}")


if __name__ == "__main__":
    main()