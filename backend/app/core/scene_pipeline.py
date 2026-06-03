from typing import Any, Dict

from app.core.openai_client import generate_text
from app.core.prompt_builder import build_structured_scene_prompt
from app.core.scene_result_parser import parse_scene_result
from app.core.scene_validator import (
    clamp_memory_importance,
    clamp_relationship_updates,
    remove_invalid_actions,
    remove_invalid_dialogues,
    remove_invalid_events,
    remove_invalid_memory_updates,
    remove_invalid_relationship_updates,
    remove_player_dialogues,
)


def generate_scene(
    world: Dict[str, Any],
    scene_context: Dict[str, Any],
    player_input: str | None = None,
    scene_history: str | None = None,
) -> Dict[str, Any]:
    """Genere, parse et valide une scene produite par le LLM."""

    prompt = build_structured_scene_prompt(
        world,
        scene_context,
        player_input,
        scene_history,
    )

    scene_response = generate_text(prompt)
    scene_result = parse_scene_result(scene_response)

    return validate_scene_result(
        scene_result,
        world,
    )


def validate_scene_result(
    scene_result: Dict[str, Any],
    world: Dict[str, Any],
) -> Dict[str, Any]:
    """Applique tous les filtres de validation au SceneResult."""

    valid_character_ids = world["characters"]

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

    scene_result = remove_invalid_memory_updates(
        scene_result,
        valid_character_ids,
    )

    scene_result = remove_player_dialogues(
        scene_result,
        world["player_character"],
    )

    scene_result = clamp_relationship_updates(scene_result)
    scene_result = clamp_memory_importance(scene_result)

    return scene_result