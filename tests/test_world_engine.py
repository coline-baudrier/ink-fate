from backend.app.core.world_engine import (
    apply_world_updates,
    update_world_after_scene,
    update_world_after_turn,
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


def test_apply_world_updates_uses_scene_location_when_new_location_is_empty():
    world = build_world()

    scene_result = {
        "scene": {
            "location": "dormitory",
        },
        "world_updates": {
            "new_location": "",
            "character_movements": {},
        },
    }

    updated_world = apply_world_updates(
        world,
        scene_result,
    )

    assert updated_world["active_scene"]["location"] == "dormitory"
    assert updated_world["character_locations"]["elina"] == "dormitory"
    assert updated_world["active_scene"]["participants"] == ["elina"]


def test_apply_world_updates_keeps_new_location_priority_over_scene_location():
    world = build_world()

    scene_result = {
        "scene": {
            "location": "library",
        },
        "world_updates": {
            "new_location": "dormitory",
            "character_movements": {},
        },
    }

    updated_world = apply_world_updates(
        world,
        scene_result,
    )

    assert updated_world["active_scene"]["location"] == "dormitory"
    assert updated_world["character_locations"]["elina"] == "dormitory"


def test_apply_world_updates_falls_back_to_scene_location_after_invalid_new_location():
    world = build_world()

    scene_result = {
        "scene": {
            "location": "library",
        },
        "world_updates": {
            "new_location": "moon",
            "character_movements": {},
        },
    }

    updated_world = apply_world_updates(
        world,
        scene_result,
    )

    assert updated_world["active_scene"]["location"] == "library"
    assert updated_world["character_locations"]["elina"] == "library"


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


def test_apply_world_updates_ignores_player_in_character_movements():
    world = build_world()

    scene_result = {
        "world_updates": {
            "new_location": "dormitory",
            "character_movements": {
                "elina": "campus",
                "beau": "dormitory",
            },
        }
    }

    updated_world = apply_world_updates(
        world,
        scene_result,
    )

    assert updated_world["active_scene"]["location"] == "dormitory"
    assert updated_world["character_locations"]["elina"] == "dormitory"
    assert updated_world["character_locations"]["beau"] == "dormitory"


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


def test_update_world_after_turn_applies_world_consequences():
    world = build_world()
    world["active_scene"]["participants"] = [
        "elina",
        "beau",
    ]

    characters = {
        "elina": {},
        "beau": {},
        "dean": {
            "schedule": [
                {
                    "time": "10:20",
                    "location": "library",
                }
            ]
        },
    }

    scene_result = {
        "events": [
            {
                "type": "test_event",
                "participants": [
                    "elina",
                ],
                "summary": "Something happened.",
            }
        ],
        "world_updates": {
            "time_advance_minutes": 20,
            "new_location": "dormitory",
            "character_movements": {},
        },
    }

    updated_world = update_world_after_turn(
        world,
        characters,
        scene_result,
    )

    assert updated_world["timeline"]["current_time"] == "10:20"
    assert updated_world["active_scene"]["location"] == "dormitory"
    assert updated_world["character_locations"]["elina"] == "dormitory"
    assert updated_world["character_locations"]["dean"] == "library"
    assert updated_world["event_log"][0]["type"] == "test_event"
    assert updated_world["event_log"][1]["type"] == "npc_schedule_move"
    assert updated_world["event_log"][1]["participants"] == ["dean"]


def test_update_world_after_turn_keeps_active_participant_in_scene():
    world = build_world()

    characters = {
        "elina": {},
        "dean": {
            "schedule": [
                {
                    "time": "10:20",
                    "location": "library",
                }
            ]
        },
    }

    scene_result = {
        "scene": {
            "location": "campus",
            "time": "10:20",
            "participants": [
                "elina",
                "dean",
            ],
        },
        "world_updates": {
            "time_advance_minutes": 20,
            "new_location": "",
            "character_movements": {},
        },
    }

    updated_world = update_world_after_turn(
        world,
        characters,
        scene_result,
    )

    assert updated_world["character_locations"]["dean"] == "campus"
    assert updated_world["event_log"] == []
    assert updated_world["active_scene"]["participants"] == [
        "elina",
        "beau",
        "dean",
    ]


def test_update_world_after_turn_moves_npc_outside_scene_by_schedule():
    world = build_world()
    world["active_scene"]["participants"] = [
        "elina",
        "beau",
    ]

    characters = {
        "elina": {},
        "beau": {},
        "dean": {
            "schedule": [
                {
                    "time": "10:20",
                    "location": "library",
                }
            ]
        },
    }

    scene_result = {
        "scene": {
            "location": "campus",
            "time": "10:20",
            "participants": [
                "elina",
                "beau",
            ],
        },
        "world_updates": {
            "time_advance_minutes": 20,
            "new_location": "",
            "character_movements": {},
        },
    }

    updated_world = update_world_after_turn(
        world,
        characters,
        scene_result,
    )

    assert updated_world["character_locations"]["dean"] == "library"
    assert updated_world["event_log"][0]["type"] == "npc_schedule_move"
    assert updated_world["event_log"][0]["participants"] == ["dean"]


def test_update_world_after_turn_keeps_scene_location_for_player_move():
    world = build_world()

    characters = {
        "elina": {},
        "beau": {},
        "dean": {},
    }

    scene_result = {
        "scene": {
            "location": "dormitory",
            "time": "10:05",
            "participants": [
                "elina",
            ],
        },
        "world_updates": {
            "time_advance_minutes": 5,
            "new_location": "",
            "character_movements": {},
        },
    }

    updated_world = update_world_after_turn(
        world,
        characters,
        scene_result,
    )

    assert updated_world["active_scene"]["location"] == "dormitory"
    assert updated_world["character_locations"]["elina"] == "dormitory"
    assert updated_world["active_scene"]["participants"] == ["elina"]


def test_update_world_after_turn_does_not_override_narrative_npc_move():
    world = build_world()

    characters = {
        "elina": {},
        "dean": {
            "schedule": [
                {
                    "time": "10:20",
                    "location": "library",
                }
            ]
        },
    }

    scene_result = {
        "world_updates": {
            "time_advance_minutes": 20,
            "new_location": "dormitory",
            "character_movements": {
                "dean": "dormitory",
            },
        },
    }

    updated_world = update_world_after_turn(
        world,
        characters,
        scene_result,
    )

    assert updated_world["character_locations"]["dean"] == "dormitory"
    assert updated_world["active_scene"]["participants"] == [
        "elina",
        "dean",
    ]

    assert updated_world["event_log"] == []
