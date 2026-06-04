from backend.app.core.json_loader import load_json, save_json
from backend.app.core.runtime_save import (
    build_runtime_save_path,
    clear_runtime_save,
    get_runtime_characters_path,
    get_runtime_world_path,
    load_runtime_characters,
    load_runtime_world,
    normalize_save_id,
    save_runtime_state,
)


def build_world(current_time="10:00"):
    return {
        "universe": {
            "id": "off-campus",
            "name": "Off Campus",
        },
        "timeline": {
            "current_date": "2026-09-01",
            "current_time": current_time,
            "current_day": 1,
        },
        "player_character": "elina",
        "characters": [
            "elina",
            "dean",
        ],
        "locations": [],
        "active_scene": {
            "location": "campus",
            "participants": [
                "elina",
            ],
        },
    }


def build_characters(dean_phone_known=False):
    return {
        "elina": {
            "id": "elina",
            "contacts": {},
        },
        "dean": {
            "id": "dean",
            "contacts": {
                "elina": {
                    "phone_number_known": dean_phone_known,
                }
            },
        },
    }


def write_character_files(characters_path, characters):
    for character_id, character in characters.items():
        save_json(
            characters_path / f"{character_id}.json",
            character,
        )


def test_build_runtime_save_path_uses_data_saves():
    path = build_runtime_save_path(
        project_root="project",
        universe_id="off-campus",
        save_id="slot-1",
    )

    assert str(path).endswith("project\\data\\saves\\off-campus\\slot-1")


def test_normalize_save_id_falls_back_to_default():
    assert normalize_save_id("") == "default"
    assert normalize_save_id(None) == "default"


def test_normalize_save_id_removes_path_segments():
    assert normalize_save_id("../slot one") == "slot-one"


def test_load_runtime_world_falls_back_to_canon(tmp_path):
    canon_world_path = tmp_path / "universes" / "off-campus" / "world.json"
    runtime_path = tmp_path / "saves" / "off-campus" / "default"
    save_json(
        canon_world_path,
        build_world("10:00"),
    )

    world = load_runtime_world(
        canon_world_path,
        runtime_path,
    )

    assert world["timeline"]["current_time"] == "10:00"


def test_load_runtime_world_prefers_runtime_save(tmp_path):
    canon_world_path = tmp_path / "universes" / "off-campus" / "world.json"
    runtime_path = tmp_path / "saves" / "off-campus" / "default"
    save_json(
        canon_world_path,
        build_world("10:00"),
    )
    save_json(
        get_runtime_world_path(runtime_path),
        build_world("10:45"),
    )

    world = load_runtime_world(
        canon_world_path,
        runtime_path,
    )

    assert world["timeline"]["current_time"] == "10:45"


def test_save_runtime_state_does_not_modify_canon_files(tmp_path):
    canon_path = tmp_path / "universes" / "off-campus"
    runtime_path = tmp_path / "saves" / "off-campus" / "default"
    canon_world_path = canon_path / "world.json"
    canon_characters_path = canon_path / "characters"

    save_json(
        canon_world_path,
        build_world("10:00"),
    )
    write_character_files(
        canon_characters_path,
        build_characters(dean_phone_known=False),
    )

    save_runtime_state(
        runtime_path,
        build_world("10:45"),
        build_characters(dean_phone_known=True),
    )

    canon_world = load_json(canon_world_path)
    canon_dean = load_json(canon_characters_path / "dean.json")
    runtime_world = load_json(get_runtime_world_path(runtime_path))
    runtime_dean = load_json(
        get_runtime_characters_path(runtime_path) / "dean.json"
    )

    assert canon_world["timeline"]["current_time"] == "10:00"
    assert canon_dean["contacts"]["elina"]["phone_number_known"] is False
    assert runtime_world["timeline"]["current_time"] == "10:45"
    assert runtime_dean["contacts"]["elina"]["phone_number_known"] is True


def test_load_runtime_characters_prefers_runtime_characters(tmp_path):
    canon_characters_path = tmp_path / "universes" / "off-campus" / "characters"
    runtime_path = tmp_path / "saves" / "off-campus" / "default"

    write_character_files(
        canon_characters_path,
        build_characters(dean_phone_known=False),
    )
    write_character_files(
        get_runtime_characters_path(runtime_path),
        build_characters(dean_phone_known=True),
    )

    characters = load_runtime_characters(
        canon_characters_path,
        [
            "elina",
            "dean",
        ],
        runtime_path,
    )

    assert characters["dean"]["contacts"]["elina"]["phone_number_known"] is True


def test_clear_runtime_save_removes_runtime_only(tmp_path):
    canon_world_path = tmp_path / "universes" / "off-campus" / "world.json"
    runtime_path = tmp_path / "saves" / "off-campus" / "default"
    save_json(
        canon_world_path,
        build_world("10:00"),
    )
    save_json(
        get_runtime_world_path(runtime_path),
        build_world("10:45"),
    )

    clear_runtime_save(runtime_path)

    assert canon_world_path.exists()
    assert not runtime_path.exists()
