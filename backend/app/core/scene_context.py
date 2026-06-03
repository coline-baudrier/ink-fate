from typing import Any, Dict, List

def build_scene_context(
        world: Dict[str, Any],
        characters: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    
    # On construit le contexte de la scène active avec les informations utiles pour comprendre la scène en cours : lieu, date, heure, participants présents
    active_scene = world["active_scene"]

    participant_ids = active_scene["participants"]

    participants: List[Dict[str, Any]] = []

    location_id = active_scene["location"]

    location = next(
        location
        for location in world["locations"]
        if location["id"] == location_id
    )

    for character_id in participant_ids:
        character = characters[character_id]
        participants.append(character)

    scene_context = {
    "location": location,
    "date": world["timeline"]["current_date"],
    "time": world["timeline"]["current_time"],
    "participants": participants
    }

    return scene_context
