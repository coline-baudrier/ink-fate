"""Gestion simple du world state.

Le world state contient l'heure, la scene active et les informations globales
de l'univers. Ce module regroupe les petites operations qui modifient ou
rafraichissent cet etat.
"""

from pathlib import Path
from typing import Any, Dict

from app.core.json_loader import save_json
from app.core.scene_context import build_scene_context
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

    new_location = world_updates.get(
        "new_location",
        "",
    )

    character_movements = world_updates.get(
        "character_movements",
        {},
    )

    if new_location and new_location in valid_location_ids:
        player_character = world["player_character"]

        world["active_scene"]["location"] = new_location
        world["character_locations"][player_character] = new_location

    if isinstance(character_movements, dict):
        for character_id, location_id in character_movements.items():
            if character_id not in world["character_locations"]:
                continue

            if location_id not in valid_location_ids:
                continue

            world["character_locations"][character_id] = location_id

    world["active_scene"]["participants"] = resolve_scene_participants(world)

    return world