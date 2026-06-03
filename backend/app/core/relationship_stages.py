"""Lecture narrative des relations entre personnages."""

from typing import Any, Dict


RELATIONSHIP_DIMENSIONS = {
    "friendship": {
        "label": "friendship",
        "low": "distant",
        "mid": "friendly",
        "high": "close friend",
    },
    "trust": {
        "label": "trust",
        "low": "guarded",
        "mid": "some trust",
        "high": "trusted",
    },
    "respect": {
        "label": "respect",
        "low": "low respect",
        "mid": "respectful",
        "high": "high respect",
    },
    "attachment": {
        "label": "attachment",
        "low": "detached",
        "mid": "attached",
        "high": "deeply attached",
    },
    "jealousy": {
        "label": "jealousy",
        "low": "not jealous",
        "mid": "jealous",
        "high": "very jealous",
    },
    "attraction": {
        "label": "attraction",
        "low": "low attraction",
        "mid": "attracted",
        "high": "strong attraction",
    },
}


def get_dimension_stage(
    dimension: str,
    value: int,
) -> str:
    """Retourne un palier narratif pour une dimension relationnelle."""

    config = RELATIONSHIP_DIMENSIONS.get(
        dimension,
        {
            "low": "low",
            "mid": "medium",
            "high": "high",
        },
    )

    if value <= 10:
        return config["low"]

    if value <= 35:
        return f"emerging {config['label']}" if "label" in config else config["mid"]

    if value <= 65:
        return config["mid"]

    if value <= 85:
        return f"strong {config['label']}" if "label" in config else config["high"]

    return config["high"]


def build_relationship_context(
    scene_context: Dict[str, Any],
    max_relationships_per_character: int = 5,
) -> str:
    """Construit le contexte relationnel des participants actifs."""

    lines = []

    for character in scene_context["participants"]:
        character_id = character["id"]

        relationships = character.get(
            "relationships",
            {},
        )

        if not isinstance(relationships, dict):
            continue

        relationship_lines = []

        for target_id, relationship in relationships.items():
            if not isinstance(relationship, dict):
                continue

            dimension_lines = []
            total_score = 0

            for dimension in RELATIONSHIP_DIMENSIONS:
                value = relationship.get(
                    dimension,
                    0,
                )

                if not isinstance(value, int):
                    value = 0

                total_score += value

                stage = get_dimension_stage(
                    dimension,
                    value,
                )

                dimension_lines.append(
                    f"  - {dimension}: {value}/100 ({stage})"
                )

            relationship_text = [
                f"- {character_id} -> {target_id}:"
            ]

            relationship_text.extend(dimension_lines)

            relationship_lines.append(
                (
                    total_score,
                    "\n".join(relationship_text),
                )
            )

        relationship_lines.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        for _, line in relationship_lines[
            :max_relationships_per_character
        ]:
            lines.append(line)

    if not lines:
        return "No significant relationships yet."

    return "\n".join(lines)