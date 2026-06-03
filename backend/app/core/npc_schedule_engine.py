"""Gestion simple des plannings PNJ."""

from typing import Any, Dict


def time_to_minutes(time_value: str) -> int | None:
    """Convertit une heure HH:MM en minutes depuis minuit."""

    if not isinstance(time_value, str):
        return None

    parts = time_value.split(":")

    if len(parts) != 2:
        return None

    try:
        hours = int(parts[0])
        minutes = int(parts[1])
    except ValueError:
        return None

    if hours < 0 or hours > 23:
        return None

    if minutes < 0 or minutes > 59:
        return None

    return hours * 60 + minutes


def get_current_schedule_entry(
    character: Dict[str, Any],
    current_time: str,
) -> Dict[str, Any] | None:
    """Retourne la derniere entree de planning applicable a l'heure courante."""

    current_minutes = time_to_minutes(current_time)

    if current_minutes is None:
        return None

    schedule = character.get("schedule", [])

    if not isinstance(schedule, list):
        return None

    selected_entry = None
    selected_minutes = -1

    for entry in schedule:
        if not isinstance(entry, dict):
            continue

        entry_time = entry.get("time", "")
        entry_minutes = time_to_minutes(entry_time)

        if entry_minutes is None:
            continue

        if entry_minutes <= current_minutes and entry_minutes > selected_minutes:
            selected_entry = entry
            selected_minutes = entry_minutes

    return selected_entry


def update_npc_locations_from_schedule(
    world: Dict[str, Any],
    characters: Dict[str, Dict[str, Any]],
    ignored_character_ids: set[str] | None = None,
) -> Dict[str, Any]:
    """Met a jour les positions des PNJ selon leur planning."""

    world, _ = apply_npc_schedule_movements(
        world,
        characters,
        ignored_character_ids,
    )

    return world


def apply_npc_schedule_movements(
    world: Dict[str, Any],
    characters: Dict[str, Dict[str, Any]],
    ignored_character_ids: set[str] | None = None,
) -> tuple[Dict[str, Any], list[Dict[str, str]]]:
    """Applique les plannings PNJ et retourne les mouvements effectues."""

    if ignored_character_ids is None:
        ignored_character_ids = set()

    if "character_locations" not in world:
        world["character_locations"] = {}

    current_time = world["timeline"]["current_time"]
    player_character = world["player_character"]

    valid_location_ids = {
        location["id"]
        for location in world["locations"]
    }

    movements = []

    for character_id, character in characters.items():
        if character_id == player_character:
            continue

        if character_id in ignored_character_ids:
            continue

        schedule_entry = get_current_schedule_entry(
            character,
            current_time,
        )

        if not schedule_entry:
            continue

        location_id = schedule_entry.get("location", "")

        if location_id not in valid_location_ids:
            continue

        previous_location = world["character_locations"].get(
            character_id,
            "",
        )

        if previous_location == location_id:
            continue

        world["character_locations"][character_id] = location_id

        movements.append(
            {
                "character": character_id,
                "from": previous_location,
                "to": location_id,
                "activity": schedule_entry.get(
                    "activity",
                    "",
                ),
            }
        )

    return world, movements
