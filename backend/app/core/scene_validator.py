"""Validation minimale d'un SceneResult.

Le LLM peut renvoyer une structure imparfaite. Ce module nettoie ce que le
moteur sait verifier avant d'appliquer des effets au monde.
"""

from typing import Any, Dict


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
    min_value: int = -5,
    max_value: int = 5,
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
            # Les valeurs relationnelles doivent etre des nombres entiers.
            if not isinstance(value, int):
                continue

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