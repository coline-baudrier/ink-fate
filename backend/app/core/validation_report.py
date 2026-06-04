"""Rapport lisible des nettoyages de validation SceneResult."""

from typing import Any, Dict, List
import copy


LIST_FIELDS = [
    "dialogues",
    "actions",
    "events",
    "relationship_updates",
    "contact_updates",
    "memory_updates",
    "narration",
]


def build_validation_report(
    original_scene_result: Dict[str, Any],
    validated_scene_result: Dict[str, Any],
) -> List[str]:
    """Compare avant/apres validation et retourne un rapport compact."""

    original = copy.deepcopy(original_scene_result)
    validated = copy.deepcopy(validated_scene_result)
    report = []

    report.extend(
        build_list_change_report(
            original,
            validated,
        )
    )
    report.extend(
        build_scene_change_report(
            original,
            validated,
        )
    )
    report.extend(
        build_world_update_change_report(
            original,
            validated,
        )
    )

    if not report:
        return [
            "Validation report: no cleanup needed.",
        ]

    return report


def build_list_change_report(
    original: Dict[str, Any],
    validated: Dict[str, Any],
) -> List[str]:
    """Rapporte les listes filtrees ou limitees."""

    report = []

    for field_name in LIST_FIELDS:
        original_count = count_list_items(
            original.get(field_name)
        )
        validated_count = count_list_items(
            validated.get(field_name)
        )

        if original_count > validated_count:
            removed_count = original_count - validated_count
            report.append(
                f"Validation report: {removed_count} {field_name} item(s) removed or trimmed."
            )

    return report


def build_scene_change_report(
    original: Dict[str, Any],
    validated: Dict[str, Any],
) -> List[str]:
    """Rapporte les corrections du bloc scene."""

    report = []
    original_scene = original.get(
        "scene",
        {},
    )
    validated_scene = validated.get(
        "scene",
        {},
    )

    if not isinstance(original_scene, dict):
        original_scene = {}

    if not isinstance(validated_scene, dict):
        validated_scene = {}

    for key in [
        "location",
        "time",
        "participants",
    ]:
        if original_scene.get(key) != validated_scene.get(key):
            report.append(
                f"Validation report: scene.{key} normalized."
            )

    return report


def build_world_update_change_report(
    original: Dict[str, Any],
    validated: Dict[str, Any],
) -> List[str]:
    """Rapporte les corrections du bloc world_updates."""

    report = []
    original_updates = original.get(
        "world_updates",
        {},
    )
    validated_updates = validated.get(
        "world_updates",
        {},
    )

    if not isinstance(original_updates, dict):
        original_updates = {}

    if not isinstance(validated_updates, dict):
        validated_updates = {}

    for key in [
        "new_location",
        "time_advance_minutes",
        "character_movements",
    ]:
        if original_updates.get(key) != validated_updates.get(key):
            report.append(
                f"Validation report: world_updates.{key} normalized."
            )

    return report


def count_list_items(value: Any) -> int:
    """Compte les elements si la valeur est une liste."""

    if isinstance(value, list):
        return len(value)

    return 0
