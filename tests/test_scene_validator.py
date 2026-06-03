from backend.app.core.scene_validator import (
    validate_scene,
    validate_world_updates,
)


def build_world():
    return {
        "timeline": {
            "current_date": "2026-09-01",
            "current_time": "10:15",
            "current_day": 1,
        },
        "locations": [
            {"id": "campus", "name": "Campus"},
            {"id": "dormitory", "name": "Dormitory"},
            {"id": "library", "name": "Library"},
        ],
        "characters": [
            "elina",
            "beau",
            "dean",
        ],
        "active_scene": {
            "location": "campus",
            "participants": [
                "elina",
                "beau",
            ],
        },
    }


def test_validate_scene_keeps_valid_scene():
    world = build_world()

    scene_result = {
        "scene": {
            "location": "dormitory",
            "time": "11:30",
            "participants": [
                "elina",
                "dean",
            ],
        }
    }

    validated = validate_scene(
        scene_result,
        world,
    )

    assert validated["scene"] == {
        "location": "dormitory",
        "time": "11:30",
        "participants": [
            "elina",
            "dean",
        ],
    }


def test_validate_scene_replaces_invalid_location_and_time():
    world = build_world()

    scene_result = {
        "scene": {
            "location": "moon",
            "time": "99:99",
            "participants": [
                "elina",
            ],
        }
    }

    validated = validate_scene(
        scene_result,
        world,
    )

    assert validated["scene"]["location"] == "campus"
    assert validated["scene"]["time"] == "10:15"


def test_validate_scene_removes_invalid_participants():
    world = build_world()

    scene_result = {
        "scene": {
            "location": "campus",
            "time": "10:20",
            "participants": [
                "elina",
                "unknown",
            ],
        }
    }

    validated = validate_scene(
        scene_result,
        world,
    )

    assert validated["scene"]["participants"] == ["elina"]


def test_validate_scene_uses_active_scene_when_scene_is_missing():
    world = build_world()

    validated = validate_scene(
        {},
        world,
    )

    assert validated["scene"] == {
        "location": "campus",
        "time": "10:15",
        "participants": [
            "elina",
            "beau",
        ],
    }


def test_validate_world_updates_keeps_valid_new_location():
    world = build_world()

    scene_result = {
        "world_updates": {
            "new_location": "dormitory",
            "time_advance_minutes": 5,
            "character_movements": {},
        }
    }

    validated = validate_world_updates(
        scene_result,
        world,
    )

    assert validated["world_updates"]["new_location"] == "dormitory"


def test_validate_world_updates_removes_invalid_new_location():
    world = build_world()

    scene_result = {
        "world_updates": {
            "new_location": "moon",
            "time_advance_minutes": 5,
            "character_movements": {},
        }
    }

    validated = validate_world_updates(
        scene_result,
        world,
    )

    assert validated["world_updates"]["new_location"] == ""


def test_validate_world_updates_clamps_negative_time():
    world = build_world()

    scene_result = {
        "world_updates": {
            "new_location": "",
            "time_advance_minutes": -10,
            "character_movements": {},
        }
    }

    validated = validate_world_updates(
        scene_result,
        world,
    )

    assert validated["world_updates"]["time_advance_minutes"] == 0


def test_validate_world_updates_clamps_large_time():
    world = build_world()

    scene_result = {
        "world_updates": {
            "new_location": "",
            "time_advance_minutes": 999,
            "character_movements": {},
        }
    }

    validated = validate_world_updates(
        scene_result,
        world,
    )

    assert validated["world_updates"]["time_advance_minutes"] == 180


def test_validate_world_updates_cleans_character_movements():
    world = build_world()

    scene_result = {
        "world_updates": {
            "new_location": "",
            "time_advance_minutes": 5,
            "character_movements": {
                "beau": "dormitory",
                "unknown": "library",
                "dean": "moon",
            },
        }
    }

    validated = validate_world_updates(
        scene_result,
        world,
    )

    assert validated["world_updates"]["character_movements"] == {
        "beau": "dormitory",
    }
