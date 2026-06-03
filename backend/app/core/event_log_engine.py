"""Gestion du journal d'evenements du monde."""

from typing import Any, Dict, List


def build_event_summary(
    event: Dict[str, Any],
    scene_result: Dict[str, Any],
) -> str:
    """Construit un resume court pour un evenement."""

    event_summary = event.get("summary", "")

    if isinstance(event_summary, str) and event_summary.strip():
        return event_summary.strip()

    narration = scene_result.get("narration", [])

    if isinstance(narration, list) and narration:
        first_line = narration[0]

        if isinstance(first_line, str):
            return first_line[:240]

    return "Un evenement important s'est produit."


def update_event_log_after_scene(
    world: Dict[str, Any],
    scene_result: Dict[str, Any],
) -> Dict[str, Any]:
    """Ajoute les evenements importants de la scene au journal du monde."""

    if "event_log" not in world:
        world["event_log"] = []

    events = scene_result.get("events", [])

    if not isinstance(events, list):
        return world

    timeline = world["timeline"]

    for event in events:
        if not isinstance(event, dict):
            continue

        event_type = event.get("type", "")

        if not isinstance(event_type, str):
            continue

        if not event_type.strip():
            continue

        participants = event.get("participants", [])

        if not isinstance(participants, list):
            participants = []

        log_entry = {
            "day": timeline["current_day"],
            "date": timeline["current_date"],
            "time": timeline["current_time"],
            "type": event_type,
            "participants": participants,
            "summary": build_event_summary(
                event,
                scene_result,
            ),
        }

        world["event_log"].append(log_entry)

    return world