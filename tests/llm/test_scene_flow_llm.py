import copy
import os
from pathlib import Path

import pytest


if os.getenv("INK_FATE_RUN_LLM_TESTS") != "1":
    pytest.skip(
        "Set INK_FATE_RUN_LLM_TESTS=1 to run LLM tests.",
        allow_module_level=True,
    )

if not os.getenv("OPENAI_API_KEY"):
    pytest.skip(
        "OPENAI_API_KEY is required to run LLM tests.",
        allow_module_level=True,
    )


from backend.app.core.character_loader import load_characters
from backend.app.core.character_state_engine import (
    update_characters_after_scene,
)
from backend.app.core.json_loader import load_json
from backend.app.core.scene_context import build_scene_context
from backend.app.core.scene_pipeline import generate_scene


PROJECT_ROOT = Path(__file__).resolve().parents[2]
UNIVERSE_PATH = PROJECT_ROOT / "data" / "universes" / "off-campus"


def load_test_state():
    world = copy.deepcopy(
        load_json(UNIVERSE_PATH / "world.json")
    )
    scenario = copy.deepcopy(
        load_json(UNIVERSE_PATH / "scenario.json")
    )
    characters = load_characters(
        UNIVERSE_PATH / "characters",
        world["characters"],
    )

    world["timeline"]["current_time"] = "10:30"
    world["active_scene"] = {
        "location": "campus",
        "participants": [
            "elina",
            "beau",
            "dean",
        ],
    }
    world["character_locations"] = {
        "elina": "campus",
        "beau": "campus",
        "dean": "campus",
    }
    world.setdefault(
        "messages",
        [],
    )

    return world, scenario, characters


def assert_scene_result_shape(scene_result):
    assert isinstance(scene_result.get("narration"), list)
    assert isinstance(scene_result.get("dialogues"), list)
    assert isinstance(scene_result.get("world_updates"), dict)


def assert_no_player_dialogue(scene_result):
    for dialogue in scene_result.get("dialogues", []):
        assert dialogue.get("speaker") != "elina"


@pytest.mark.llm
def test_player_departure_to_dormitory_sets_new_location():
    world, scenario, characters = load_test_state()
    scene_context = build_scene_context(
        world,
        characters,
    )

    scene_result = generate_scene(
        world,
        scenario,
        scene_context,
        '"Salut les nazes" *j\'avance vers mon dortoir les laissant la*',
    )

    assert_scene_result_shape(scene_result)
    assert scene_result["world_updates"]["new_location"] == "dormitory"
    assert "elina" in scene_result["scene"]["participants"]
    assert_no_player_dialogue(scene_result)


@pytest.mark.llm
def test_phone_number_and_skating_context_can_grant_dean_access():
    world, scenario, characters = load_test_state()
    characters["dean"]["contacts"]["elina"]["phone_number_known"] = False
    scene_context = build_scene_context(
        world,
        characters,
    )

    scene_result = generate_scene(
        world,
        scenario,
        scene_context,
        (
            '"Je te donne mon numero. Tu me dois toujours cette seance '
            'a la patinoire."'
        ),
    )

    assert_scene_result_shape(scene_result)
    assert_no_player_dialogue(scene_result)

    characters = update_characters_after_scene(
        scene_result,
        characters,
    )
    dean_contact = characters["dean"]["contacts"]["elina"]

    direct_update = any(
        update.get("source") == "dean"
        and update.get("target") == "elina"
        and update.get("changes", {}).get("phone_number_known") is True
        for update in scene_result.get("contact_updates", [])
        if isinstance(update, dict)
    )

    assert (
        direct_update
        or dean_contact.get("phone_number_known") is True
    )


@pytest.mark.llm
def test_generated_scene_result_has_valid_core_json_shape():
    world, scenario, characters = load_test_state()
    scene_context = build_scene_context(
        world,
        characters,
    )

    scene_result = generate_scene(
        world,
        scenario,
        scene_context,
        "*J'observe Dean et Beau quelques secondes sans repondre.*",
    )

    assert_scene_result_shape(scene_result)
    assert_no_player_dialogue(scene_result)
