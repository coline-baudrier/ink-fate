"""Application des changements relationnels.

Le SceneResult contient des deltas comme `attraction: +3`.
Ce module les applique aux personnages, puis limite les valeurs entre 0 et 100.
"""

from typing import Any, Dict


def apply_relationship_updates(
    scene_result: Dict[str, Any],
    characters: Dict[str, Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """Applique les changements relationnels aux personnages."""

    relationship_updates = scene_result.get(
        "relationship_updates",
        [],
    )

    for update in relationship_updates:
        source_id = update.get("source")
        target_id = update.get("target")

        changes = update.get("changes", {})

        source_character = characters.get(source_id)

        if not source_character:
            continue

        # Les relations sont stockees dans le personnage source.
        relationships = source_character.get(
            "relationships",
            {}
        )

        target_relationship = relationships.get(
            target_id
        )

        if not target_relationship:
            continue

        for stat_name, stat_delta in changes.items():
            current_value = target_relationship.get(
                stat_name,
                0,
            )

            target_relationship[stat_name] = clamp_value(
                current_value + stat_delta
            )

    return characters


def clamp_value(
    value: int,
    min_value: int = 0,
    max_value: int = 100,
) -> int:
    """Limite une valeur entre min_value et max_value."""

    return max(min_value, min(value, max_value))
