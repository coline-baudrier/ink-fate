from typing import Any, Dict

from app.core.contact_intent_parser import (
    apply_contact_intent_hints,
    build_contact_intent_hints,
)
from app.core.openai_client import generate_text
from app.core.player_intent_parser import (
    apply_player_intent_hints,
    build_player_intent_hints,
)
from app.core.prompt_builder import build_structured_scene_prompt
from app.core.scene_result_parser import parse_scene_result
from app.core.scene_validator import (
    clamp_memory_importance,
    clamp_relationship_updates,
    remove_invalid_actions,
    remove_invalid_contact_updates,
    remove_invalid_dialogues,
    remove_invalid_events,
    remove_invalid_memory_updates,
    remove_invalid_relationship_updates,
    remove_player_dialogues,
    remove_dialogues_from_nonparticipants,
    remove_player_internal_state_from_narration,
    validate_scene,
    validate_world_updates,
    validate_scene_pacing,
)
from app.core.validation_report import build_validation_report


def generate_scene(
    world: Dict[str, Any],
    scenario: Dict[str, Any],
    scene_context: Dict[str, Any],
    player_input: str | None = None,
    scene_history: str | None = None,
) -> Dict[str, Any]:
    """Genere, parse et valide une scene produite par le LLM."""

    player_intent_hints = build_player_intent_hints(
        player_input,
        world,
    )
    contact_intent_hints = build_contact_intent_hints(
        player_input,
        world,
        scene_context,
    )
    hinted_scene_context = {
        **scene_context,
        "player_intent_hints": player_intent_hints,
        "contact_intent_hints": contact_intent_hints,
    }

    prompt = build_structured_scene_prompt(
        world,
        scenario,
        hinted_scene_context,
        player_input,
        scene_history,
    )

    scene_response = generate_text(prompt)
    scene_result = parse_scene_result(scene_response)
    scene_result = validate_scene_result(
        scene_result,
        world,
    )
    scene_result = apply_contact_intent_hints(
        scene_result,
        world,
        contact_intent_hints,
    )

    return apply_player_intent_hints(
        scene_result,
        world,
        player_intent_hints,
    )


def validate_scene_result(
    scene_result: Dict[str, Any],
    world: Dict[str, Any],
) -> Dict[str, Any]:
    """Applique tous les filtres de validation au SceneResult."""

    valid_character_ids = world["characters"]
    scene_result = validate_scene(
        scene_result,
        world,
    )

    scene_result = remove_invalid_dialogues(
        scene_result,
        valid_character_ids,
    )

    scene_result = remove_invalid_actions(
        scene_result,
        valid_character_ids,
    )

    scene_result = remove_invalid_events(
        scene_result,
        valid_character_ids,
    )

    scene_result = remove_invalid_relationship_updates(
        scene_result,
        valid_character_ids,
    )

    scene_result = remove_invalid_contact_updates(
        scene_result,
        valid_character_ids,
    )

    scene_result = remove_invalid_memory_updates(
        scene_result,
        valid_character_ids,
    )

    scene_result = remove_player_dialogues(
        scene_result,
        world["player_character"],
    )

    scene_result = remove_dialogues_from_nonparticipants(
        scene_result,
    )

    scene_result = remove_player_internal_state_from_narration(
        scene_result,
        world["player_character"],
    )

    scene_result = validate_scene_pacing(
        scene_result,
    )

    scene_result = clamp_relationship_updates(scene_result)
    scene_result = clamp_memory_importance(scene_result)

    scene_result = validate_world_updates(
        scene_result,
        world,
    )

    return scene_result


def validate_scene_result_with_report(
    scene_result: Dict[str, Any],
    world: Dict[str, Any],
) -> tuple[Dict[str, Any], list[str]]:
    """Valide un SceneResult et retourne aussi un rapport lisible."""

    original_scene_result = copy_scene_result(scene_result)
    validated_scene_result = validate_scene_result(
        scene_result,
        world,
    )
    report = build_validation_report(
        original_scene_result,
        validated_scene_result,
    )

    return validated_scene_result, report


def copy_scene_result(
    scene_result: Dict[str, Any],
) -> Dict[str, Any]:
    """Copie simple pour produire un rapport sans mutation de reference."""

    import copy

    return copy.deepcopy(scene_result)
