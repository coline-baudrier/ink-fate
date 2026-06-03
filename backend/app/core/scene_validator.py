"""Validation minimale d'un SceneResult.

Le LLM peut renvoyer une structure imparfaite. Ce module nettoie ce que le
moteur sait verifier avant d'appliquer des effets au monde.
"""

from typing import Any, Dict

RELATIONSHIP_DELTA_LIMITS = {
    "attraction": {
        "min": -2,
        "max": 2,
    },
    "respect": {
        "min": -3,
        "max": 3,
    },
    "friendship": {
        "min": -2,
        "max": 2,
    },
    "trust": {
        "min": -1,
        "max": 2,
    },
    "attachment": {
        "min": -1,
        "max": 1,
    },
    "jealousy": {
        "min": -2,
        "max": 2,
    },
}

MAX_NARRATION_PARAGRAPHS = 3
MAX_DIALOGUES = 3


def ensure_list(value: Any) -> list:
    """Retourne la valeur si c'est une liste, sinon une liste vide."""

    if isinstance(value, list):
        return value

    return []


def ensure_dict(value: Any) -> dict:
    """Retourne la valeur si c'est un dictionnaire, sinon un dict vide."""

    if isinstance(value, dict):
        return value

    return {}


def is_valid_time(value: Any) -> bool:
    """Verifie qu'une heure ressemble a HH:MM."""

    if not isinstance(value, str):
        return False

    parts = value.split(":")

    if len(parts) != 2:
        return False

    hours, minutes = parts

    if not hours.isdigit():
        return False

    if not minutes.isdigit():
        return False

    hour_value = int(hours)
    minute_value = int(minutes)

    return 0 <= hour_value <= 23 and 0 <= minute_value <= 59


def validate_scene(
    scene_result: Dict[str, Any],
    world: Dict[str, Any],
) -> Dict[str, Any]:
    """Nettoie les informations principales de la scene."""

    valid_location_ids = {
        location["id"]
        for location in world["locations"]
    }

    valid_character_ids = set(
        world["characters"]
    )

    active_scene = world["active_scene"]
    timeline = world["timeline"]
    scene = ensure_dict(
        scene_result.get(
            "scene",
            {},
        )
    )

    location = scene.get(
        "location",
        active_scene["location"],
    )

    if location not in valid_location_ids:
        location = active_scene["location"]

    time = scene.get(
        "time",
        timeline["current_time"],
    )

    if not is_valid_time(time):
        time = timeline["current_time"]

    participant_ids = ensure_list(
        scene.get(
            "participants",
            active_scene.get(
                "participants",
                [],
            ),
        )
    )

    valid_participants = []

    for character_id in participant_ids:
        if character_id in valid_character_ids:
            valid_participants.append(character_id)

    if not valid_participants:
        valid_participants = [
            character_id
            for character_id in active_scene.get(
                "participants",
                [],
            )
            if character_id in valid_character_ids
        ]

    scene_result["scene"] = {
        "location": location,
        "time": time,
        "participants": valid_participants,
    }

    return scene_result


def remove_player_dialogues(
    scene_result: Dict[str, Any],
    player_character_id: str,
) -> Dict[str, Any]:
    """Supprime les dialogues generes pour le personnage joueur."""

    filtered_dialogues = []

    # On force une liste pour eviter de planter si le LLM renvoie autre chose.
    dialogues = ensure_list(scene_result.get("dialogues", []))

    for dialogue in dialogues:
        if not isinstance(dialogue, dict):
            continue

        speaker = dialogue.get("speaker")

        if speaker == player_character_id:
            continue

        filtered_dialogues.append(dialogue)

    scene_result["dialogues"] = filtered_dialogues

    return scene_result


def remove_invalid_dialogues(
    scene_result: Dict[str, Any],
    valid_character_ids: list[str],
) -> Dict[str, Any]:
    """Supprime les dialogues dont le speaker n'est pas valide."""

    valid_dialogues = []

    dialogues = ensure_list(scene_result.get("dialogues", []))

    for dialogue in dialogues:
        if not isinstance(dialogue, dict):
            continue

        speaker = dialogue.get("speaker")

        if speaker not in valid_character_ids:
            continue

        valid_dialogues.append(dialogue)

    scene_result["dialogues"] = valid_dialogues

    return scene_result


def remove_invalid_actions(
    scene_result: Dict[str, Any],
    valid_character_ids: list[str],
) -> Dict[str, Any]:
    """Supprime les actions dont le personnage n'est pas valide."""

    valid_actions = []

    actions = ensure_list(scene_result.get("actions", []))

    for action in actions:
        if not isinstance(action, dict):
            continue

        character = action.get("character")

        if character not in valid_character_ids:
            continue

        valid_actions.append(action)

    scene_result["actions"] = valid_actions

    return scene_result


def remove_invalid_events(
    scene_result: Dict[str, Any],
    valid_character_ids: list[str],
) -> Dict[str, Any]:
    """Supprime les evenements ou participants invalides."""

    valid_events = []

    events = ensure_list(scene_result.get("events", []))

    for event in events:
        if not isinstance(event, dict):
            continue

        participants = ensure_list(event.get("participants", []))

        valid_participants = []

        for participant in participants:
            if participant in valid_character_ids:
                valid_participants.append(participant)

        if not valid_participants:
            continue

        # On garde l'evenement, mais seulement avec ses participants valides.
        event["participants"] = valid_participants
        valid_events.append(event)

    scene_result["events"] = valid_events

    return scene_result


def remove_invalid_relationship_updates(
    scene_result: Dict[str, Any],
    valid_character_ids: list[str],
) -> Dict[str, Any]:
    """Supprime les mises a jour relationnelles invalides."""

    valid_updates = []

    relationship_updates = ensure_list(
        scene_result.get("relationship_updates", [])
    )

    for update in relationship_updates:
        if not isinstance(update, dict):
            continue

        source = update.get("source")
        target = update.get("target")

        if source not in valid_character_ids:
            continue

        if target not in valid_character_ids:
            continue

        valid_updates.append(update)

    scene_result["relationship_updates"] = valid_updates

    return scene_result


def clamp_relationship_updates(
    scene_result: Dict[str, Any],
) -> Dict[str, Any]:
    """Valide et limite les changements relationnels."""

    relationship_updates = ensure_list(
        scene_result.get("relationship_updates", [])
    )

    for update in relationship_updates:
        if not isinstance(update, dict):
            continue

        changes = ensure_dict(update.get("changes", {}))
        valid_changes = {}

        for key, value in changes.items():
            if not isinstance(value, int):
                continue

            limits = RELATIONSHIP_DELTA_LIMITS.get(
                key,
                {
                    "min": -2,
                    "max": 2,
                },
            )

            min_value = limits["min"]
            max_value = limits["max"]

            if value < min_value:
                value = min_value

            if value > max_value:
                value = max_value

            valid_changes[key] = value

        update["changes"] = valid_changes

    scene_result["relationship_updates"] = relationship_updates

    return scene_result

def remove_invalid_memory_updates(
    scene_result: Dict[str, Any],
    valid_character_ids: list[str],
) -> Dict[str, Any]:
    """Supprime les souvenirs invalides."""

    valid_memories = []

    memory_updates = ensure_list(
        scene_result.get("memory_updates", [])
    )

    for memory in memory_updates:
        if not isinstance(memory, dict):
            continue

        owner = memory.get("owner")
        content = memory.get("content")

        if owner not in valid_character_ids:
            continue

        if not isinstance(content, str):
            continue

        if not content.strip():
            continue

        valid_memories.append(memory)

    scene_result["memory_updates"] = valid_memories

    return scene_result

def clamp_memory_importance(
    scene_result: Dict[str, Any],
    min_value: int = 1,
    max_value: int = 10,
) -> Dict[str, Any]:
    """Valide et limite l'importance des souvenirs."""

    memory_updates = ensure_list(
        scene_result.get("memory_updates", [])
    )

    for memory in memory_updates:
        if not isinstance(memory, dict):
            continue

        importance = memory.get("importance", min_value)

        if not isinstance(importance, int):
            importance = min_value

        if importance < min_value:
            importance = min_value

        if importance > max_value:
            importance = max_value

        memory["importance"] = importance

    scene_result["memory_updates"] = memory_updates

    return scene_result

def validate_world_updates(
    scene_result: Dict[str, Any],
    world: Dict[str, Any],
) -> Dict[str, Any]:
    """Nettoie les world_updates invalides."""

    valid_location_ids = {
        location["id"]
        for location in world["locations"]
    }

    valid_character_ids = set(
        world["characters"]
    )

    player_character_id = world.get(
        "player_character",
        "",
    )

    world_updates = ensure_dict(
        scene_result.get(
            "world_updates",
            {},
        )
    )

    new_location = world_updates.get(
        "new_location",
        "",
    )

    if new_location:
        if new_location not in valid_location_ids:
            world_updates["new_location"] = ""

    time_advance_minutes = world_updates.get(
        "time_advance_minutes",
        0,
    )

    if not isinstance(
        time_advance_minutes,
        int,
    ):
        time_advance_minutes = 0

    if time_advance_minutes < 0:
        time_advance_minutes = 0

    if time_advance_minutes > 180:
        time_advance_minutes = 180

    world_updates["time_advance_minutes"] = (
        time_advance_minutes
    )

    character_movements = ensure_dict(
        world_updates.get(
            "character_movements",
            {},
        )
    )

    cleaned_movements = {}

    for character_id, location_id in (
        character_movements.items()
    ):
        if character_id not in valid_character_ids:
            continue

        if character_id == player_character_id:
            continue

        if location_id not in valid_location_ids:
            continue

        cleaned_movements[
            character_id
        ] = location_id

    world_updates[
        "character_movements"
    ] = cleaned_movements

    scene_result[
        "world_updates"
    ] = world_updates

    return scene_result

def validate_scene_pacing(
    scene_result: Dict[str, Any],
) -> Dict[str, Any]:
    """Nettoie et limite une scene pour garder un rythme interactif."""

    narration = ensure_list(
        scene_result.get("narration", [])
    )

    dialogues = ensure_list(
        scene_result.get("dialogues", [])
    )

    valid_narration = []

    for paragraph in narration:
        if not isinstance(paragraph, str):
            continue

        paragraph = paragraph.strip()

        if not paragraph:
            continue

        valid_narration.append(paragraph)

    valid_dialogues = []

    for dialogue in dialogues:
        if not isinstance(dialogue, dict):
            continue

        speaker = dialogue.get("speaker")
        text = dialogue.get("text")

        if not isinstance(speaker, str):
            continue

        if not isinstance(text, str):
            continue

        speaker = speaker.strip()
        text = text.strip()

        if not speaker:
            continue

        if not text:
            continue

        dialogue["speaker"] = speaker
        dialogue["text"] = text
        valid_dialogues.append(dialogue)

    scene_result["narration"] = valid_narration[
        :MAX_NARRATION_PARAGRAPHS
    ]

    scene_result["dialogues"] = valid_dialogues[
        :MAX_DIALOGUES
    ]

    return scene_result
