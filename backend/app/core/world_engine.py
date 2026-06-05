"""Gestion simple du world state.

Le world state contient l'heure, la scene active et les informations globales
de l'univers. Ce module regroupe les petites operations qui modifient ou
rafraichissent cet etat.
"""

from pathlib import Path
from typing import Any, Dict

from app.core.event_log_engine import update_event_log_after_scene
from app.core.json_loader import save_json
from app.core.npc_schedule_engine import apply_npc_schedule_movements
from app.core.planned_event_engine import apply_planned_events_after_scene
from app.core.scene_context import build_scene_context
from app.core.story_arc_state_engine import apply_story_arc_state_after_scene
from app.core.time_engine import advance_time


def update_world_after_scene(
    world: Dict[str, Any],
    scene_result: Dict[str, Any] | None = None,
    default_minutes: int = 5,
) -> Dict[str, Any]:
    """Applique l'avancement du temps apres une scene."""

    minutes = default_minutes

    if scene_result:
        world_updates = scene_result.get(
            "world_updates",
            {},
        )

        proposed_minutes = world_updates.get(
            "time_advance_minutes",
            0,
        )

        if isinstance(proposed_minutes, int) and proposed_minutes > 0:
            minutes = proposed_minutes

    world = advance_time(
        world,
        minutes,
    )

    return world


def save_world(
    world_path: Path,
    world: Dict[str, Any],
) -> None:
    """Sauvegarde le world state dans son fichier JSON."""

    save_json(
        world_path,
        world,
    )


def rebuild_scene_context(
    world: Dict[str, Any],
    characters: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """Reconstruit le contexte de scene apres modification du monde."""

    return build_scene_context(
        world,
        characters,
    )


def ensure_character_locations(world: Dict[str, Any]) -> None:
    """Initialise les positions des personnages si elles n'existent pas encore."""

    if "character_locations" in world:
        return

    current_location = world["active_scene"]["location"]

    world["character_locations"] = {}

    for character_id in world["characters"]:
        world["character_locations"][character_id] = current_location


def resolve_scene_participants(world: Dict[str, Any]) -> list[str]:
    """Recalcule les participants selon leur position actuelle."""

    active_location = world["active_scene"]["location"]
    player_character = world["player_character"]
    character_locations = world.get("character_locations", {})

    participants = []

    for character_id, location_id in character_locations.items():
        if location_id == active_location:
            participants.append(character_id)

    if player_character not in participants:
        participants.insert(0, player_character)

    return participants


def get_valid_location_ids(world: Dict[str, Any]) -> set[str]:
    """Retourne les IDs de lieux valides du monde."""

    return {
        location["id"]
        for location in world["locations"]
    }


def get_narratively_moved_character_ids(
    scene_result: Dict[str, Any],
) -> set[str]:
    """Retourne les PNJ explicitement deplaces par la scene."""

    world_updates = scene_result.get(
        "world_updates",
        {},
    )

    if not isinstance(world_updates, dict):
        return set()

    character_movements = world_updates.get(
        "character_movements",
        {},
    )

    if not isinstance(character_movements, dict):
        return set()

    return set(character_movements.keys())


def get_scene_participant_ids(scene_result: Dict[str, Any]) -> set[str]:
    """Retourne les participants indiques dans le SceneResult."""

    scene = scene_result.get(
        "scene",
        {},
    )

    if not isinstance(scene, dict):
        return set()

    participants = scene.get(
        "participants",
        [],
    )

    if not isinstance(participants, list):
        return set()

    return {
        participant
        for participant in participants
        if isinstance(participant, str)
    }


def get_scene_locked_character_ids(
    world: Dict[str, Any],
    scene_result: Dict[str, Any],
) -> set[str]:
    """Retourne les personnages que le schedule ne doit pas deplacer ce tour."""

    active_participants = world["active_scene"].get(
        "participants",
        [],
    )

    if not isinstance(active_participants, list):
        active_participants = []

    locked_character_ids = {
        character_id
        for character_id in active_participants
        if isinstance(character_id, str)
    }

    locked_character_ids.update(
        get_scene_participant_ids(scene_result)
    )

    locked_character_ids.update(
        get_narratively_moved_character_ids(scene_result)
    )

    return locked_character_ids


def get_scene_location(scene_result: Dict[str, Any]) -> str:
    """Retourne le lieu de la scene si le LLM en a fourni un."""

    scene = scene_result.get(
        "scene",
        {},
    )

    if not isinstance(scene, dict):
        return ""

    location = scene.get(
        "location",
        "",
    )

    if not isinstance(location, str):
        return ""

    return location


def add_npc_schedule_events(
    world: Dict[str, Any],
    movements: list[Dict[str, str]],
) -> Dict[str, Any]:
    """Ajoute un evenement discret pour les mouvements PNJ hors champ."""

    if not movements:
        return world

    if "event_log" not in world:
        world["event_log"] = []

    timeline = world["timeline"]

    for movement in movements:
        character_id = movement["character"]
        destination = movement["to"]
        activity = movement.get(
            "activity",
            "",
        )

        summary = f"{character_id} moves to {destination}."

        if activity:
            summary = f"{character_id} moves to {destination}: {activity}."

        world["event_log"].append(
            {
                "day": timeline["current_day"],
                "date": timeline["current_date"],
                "time": timeline["current_time"],
                "type": "npc_schedule_move",
                "participants": [
                    character_id,
                ],
                "summary": summary,
            }
        )

    return world


def apply_world_updates(
    world: Dict[str, Any],
    scene_result: Dict[str, Any],
) -> Dict[str, Any]:
    """Applique les changements de monde proposes par le SceneResult."""

    ensure_character_locations(world)

    valid_location_ids = get_valid_location_ids(world)

    world_updates = scene_result.get(
        "world_updates",
        {},
    )

    if not isinstance(world_updates, dict):
        world_updates = {}

    new_location = world_updates.get(
        "new_location",
        "",
    )

    if not isinstance(new_location, str):
        new_location = ""

    if new_location not in valid_location_ids:
        new_location = get_scene_location(scene_result)

    character_movements = world_updates.get(
        "character_movements",
        {},
    )

    player_character = world["player_character"]

    if new_location in valid_location_ids:
        world["active_scene"]["location"] = new_location
        world["character_locations"][player_character] = new_location

    if isinstance(character_movements, dict):
        for character_id, location_id in character_movements.items():
            if character_id == player_character:
                continue

            if character_id not in world["character_locations"]:
                continue

            if location_id not in valid_location_ids:
                continue

            world["character_locations"][character_id] = location_id

    character_position_updates = world_updates.get("character_position_updates", {})
    if isinstance(character_position_updates, dict):
        if "character_positions" not in world:
            world["character_positions"] = {}
        for character_id, position in character_position_updates.items():
            if isinstance(position, str):
                world["character_positions"][character_id] = position

    character_activity_updates = world_updates.get("character_activity_updates", {})
    if isinstance(character_activity_updates, dict):
        if "character_activities" not in world:
            world["character_activities"] = {}
        for character_id, activity in character_activity_updates.items():
            if isinstance(activity, str) and activity.strip():
                world["character_activities"][character_id] = activity.strip()

    # Active tasks progress
    task_updates_map = world_updates.get("task_updates", {})
    if isinstance(task_updates_map, dict) and task_updates_map:
        for task in world.get("active_tasks", []):
            if not isinstance(task, dict):
                continue
            tid = task.get("id", "")
            if tid in task_updates_map:
                upd = task_updates_map[tid]
                if isinstance(upd, dict):
                    if "progress" in upd and isinstance(upd["progress"], (int, float)):
                        task["progress"] = max(0, min(100, int(upd["progress"])))
                    if "note" in upd and isinstance(upd["note"], str):
                        task["note"] = upd["note"]
                    if "status" in upd and upd["status"] in ("active", "completed", "paused"):
                        task["status"] = upd["status"]

    # New scene props for current location
    new_props = world_updates.get("new_scene_props", [])
    if isinstance(new_props, list) and new_props:
        current_loc = world["active_scene"].get("location", "")
        if current_loc:
            if "scene_props" not in world:
                world["scene_props"] = {}
            existing = world["scene_props"].get(current_loc, [])
            for prop in new_props:
                if isinstance(prop, str) and prop.strip() and prop not in existing:
                    existing.append(prop.strip())
            world["scene_props"][current_loc] = existing

    world["active_scene"]["participants"] = resolve_scene_participants(world)

    return world


def update_world_after_turn(
    world: Dict[str, Any],
    characters: Dict[str, Dict[str, Any]],
    scene_result: Dict[str, Any],
    scenario: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Applique toutes les consequences monde d'un tour joueur."""

    locked_character_ids = get_scene_locked_character_ids(
        world,
        scene_result,
    )

    world = apply_world_updates(
        world,
        scene_result,
    )

    world = update_event_log_after_scene(
        world,
        scene_result,
    )

    world = apply_planned_events_after_scene(
        world,
        scene_result,
    )

    world = apply_story_arc_state_after_scene(
        world,
        scenario,
        scene_result,
    )

    world = update_world_after_scene(
        world,
        scene_result,
    )

    world, schedule_movements = apply_npc_schedule_movements(
        world,
        characters,
        ignored_character_ids=locked_character_ids,
    )

    world = add_npc_schedule_events(
        world,
        schedule_movements,
    )

    world["active_scene"]["participants"] = resolve_scene_participants(
        world,
    )

    world = sync_active_scene_with_player_location(
        world,
    )

    return world


def sync_active_scene_with_player_location(
    world: Dict[str, Any],
) -> Dict[str, Any]:
    """Synchronise la scene active avec la position du joueur."""

    ensure_character_locations(world)

    player_character = world["player_character"]

    player_location = world["character_locations"].get(
        player_character,
        world["active_scene"]["location"],
    )

    world["active_scene"]["location"] = player_location

    world["active_scene"]["participants"] = (
        resolve_scene_participants(world)
    )

    return world
