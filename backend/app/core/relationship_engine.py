"""Application des changements relationnels.

Le SceneResult contient des deltas comme `attraction: +3`.
Ce module les applique aux personnages, puis limite les valeurs entre 0 et 100.
"""

from typing import Any, Dict

# Dimensions qui se dégradent passivement si non entretenues.
# trust, respect, attachment restent stables (pas de decay).
DAILY_DECAY = {
    "attraction": 1,
    "friendship": 1,
    "jealousy": 1,
}

# Plancher minimal du decay : évite de tomber à 0 pour une vieille relation.
DECAY_FLOOR = 5


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


def apply_daily_relationship_decay(
    characters: Dict[str, Dict[str, Any]],
    days: int = 1,
) -> Dict[str, Dict[str, Any]]:
    """Applique une légère décroissance passive aux relations non entretenues."""

    for character in characters.values():
        relationships = character.get("relationships", {})

        if not isinstance(relationships, dict):
            continue

        for relationship in relationships.values():
            if not isinstance(relationship, dict):
                continue

            for dimension, decay_per_day in DAILY_DECAY.items():
                current = relationship.get(dimension)

                if not isinstance(current, int):
                    continue

                floor = 0 if dimension == "jealousy" else DECAY_FLOOR
                total_decay = decay_per_day * days
                relationship[dimension] = max(floor, current - total_decay)

    return characters


def clamp_value(
    value: int,
    min_value: int = 0,
    max_value: int = 100,
) -> int:
    """Limite une valeur entre min_value et max_value."""

    return max(min_value, min(value, max_value))
