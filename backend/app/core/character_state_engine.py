from typing import Any, Dict

from app.core.contact_engine import apply_contact_updates
from app.core.memory_engine import (
    apply_memory_updates,
    increase_memory_age,
)
from app.core.relationship_engine import apply_relationship_updates


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

    characters = increase_memory_age(
        characters,
    )

    return characters
