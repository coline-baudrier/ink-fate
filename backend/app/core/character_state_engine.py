from typing import Any, Dict

from app.core.contact_engine import apply_contact_updates
from app.core.memory_engine import (
    apply_memory_updates,
    increase_memory_age,
    prune_memories,
)
from app.core.relationship_engine import apply_relationship_updates


def apply_npc_knowledge_updates(
    scene_result: Dict[str, Any],
    characters: Dict[str, Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """Met à jour ce que chaque PNJ sait du personnage joueur après une scène."""

    updates = scene_result.get("npc_knowledge_updates", {})
    if not isinstance(updates, dict):
        return characters

    for char_id, learned in updates.items():
        if not isinstance(learned, dict):
            continue
        if char_id not in characters:
            continue
        char = characters[char_id]
        if "player_knowledge" not in char:
            char["player_knowledge"] = {"knows_name": False, "known_name": None}
        pk = char["player_knowledge"]
        if "knows_name" in learned:
            pk["knows_name"] = bool(learned["knows_name"])
        if "known_name" in learned:
            pk["known_name"] = learned["known_name"] if isinstance(learned["known_name"], str) else None

    return characters


def update_characters_after_scene(
    scene_result: Dict[str, Any],
    characters: Dict[str, Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """Applique aux personnages les effets persistants d'une scène."""

    characters = apply_relationship_updates(
        scene_result,
        characters,
    )

    characters = apply_contact_updates(
        scene_result,
        characters,
    )

    characters = apply_memory_updates(
        scene_result,
        characters,
    )

    characters = apply_npc_knowledge_updates(
        scene_result,
        characters,
    )

    characters = increase_memory_age(
        characters,
    )

    characters = prune_memories(
        characters,
    )

    return characters
