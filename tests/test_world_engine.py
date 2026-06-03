from backend.app.core.world_engine import (
    apply_world_updates,
    update_world_after_scene,
)


def build_world():
    return {
        "timeline": {
            "current_date": "2026-09-01",
            "current_time": "10:00",
            "current_day": 1,
        },
        "player_character": "elina",
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
                "dean",
            ],
        },
        "character_locations": {
            "elina": "campus",
            "beau": "campus",
            "dean": "campus",
        },
    }


def test_apply_world_updates_moves_player_to_valid_location():
    world = build_world()

    scene_result = {
        "world_updates": {
            "new_location": "dormitory",
            "character_movements": {},
        }
    }

    updated_world = apply_world_updates(
        world,
        scene_result,
    )

    assert updated_world["active_scene"]["location"] == "dormitory"
    assert updated_world["character_locations"]["elina"] == "dormitory"
    assert updated_world["active_scene"]["participants"] == ["elina"]


def test_apply_world_updates_ignores_invalid_player_location():
    world = build_world()

    scene_result = {
        "world_updates": {
            "new_location": "moon",
            "character_movements": {},
        }
    }

    updated_world = apply_world_updates(
        world,
        scene_result,
    )

    assert updated_world["active_scene"]["location"] == "campus"
    assert updated_world["character_locations"]["elina"] == "campus"


def test_apply_world_updates_moves_npc_to_valid_location():
    world = build_world()

    scene_result = {
        "world_updates": {
            "new_location": "dormitory",
            "character_movements": {
                "beau": "dormitory",
            },
        }
    }

    updated_world = apply_world_updates(
        world,
        scene_result,
    )

    assert updated_world["character_locations"]["elina"] == "dormitory"
    assert updated_world["character_locations"]["beau"] == "dormitory"
    assert updated_world["character_locations"]["dean"] == "campus"
    assert updated_world["active_scene"]["participants"] == [
        "elina",
        "beau",
    ]


def test_apply_world_updates_ignores_invalid_npc_location():
    world = build_world()

    scene_result = {
        "world_updates": {
            "new_location": "",
            "character_movements": {
                "beau": "moon",
            },
        }
    }

    updated_world = apply_world_updates(
        world,
        scene_result,
    )

    assert updated_world["character_locations"]["beau"] == "campus"


def test_update_world_after_scene_uses_time_advance_minutes():
    world = build_world()

    scene_result = {
        "world_updates": {
            "time_advance_minutes": 20,
        }
    }

    updated_world = update_world_after_scene(
        world,
        scene_result,
    )

    assert updated_world["timeline"]["current_time"] == "10:20"


def test_update_world_after_scene_advances_day_after_midnight():
    world = build_world()
    world["timeline"]["current_time"] = "23:50"

    scene_result = {
        "world_updates": {
            "time_advance_minutes": 20,
        }
    }

    updated_world = update_world_after_scene(
        world,
        scene_result,
    )

    assert updated_world["timeline"]["current_time"] == "00:10"
    assert updated_world["timeline"]["current_day"] == 2
