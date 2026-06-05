"""Construction du contexte de scene.

Le LLM n'a pas besoin de tout le monde complet a chaque appel.
Ce module extrait seulement le lieu, la date, l'heure et les personnages presents.
"""

from typing import Any, Dict, List


def build_scene_context(
    world: Dict[str, Any],
    characters: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """Construit le contexte utile pour generer la scene active."""

    active_scene = world["active_scene"]

    participant_ids = active_scene["participants"]
    location_id = active_scene["location"]

    # On retrouve le lieu complet a partir de son id, par exemple "campus".
    location = next(
        location
        for location in world["locations"]
        if location["id"] == location_id
    )

    character_positions: Dict[str, str] = world.get("character_positions", {})
    character_activities: Dict[str, str] = world.get("character_activities", {})

    participants: List[Dict[str, Any]] = []

    for character_id in participant_ids:
        # On remplace l'id du personnage par son dictionnaire complet.
        character = dict(characters[character_id])
        position = character_positions.get(character_id, "")
        if position:
            character["_position_in_location"] = position
        activity = character_activities.get(character_id, "")
        if activity:
            character["_current_activity"] = activity
        participants.append(character)

    scene_context = {
        "location": location,
        "date": world["timeline"]["current_date"],
        "time": world["timeline"]["current_time"],
        "participants": participants,
    }

    return scene_context
