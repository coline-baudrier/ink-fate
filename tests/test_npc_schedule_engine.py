from backend.app.core.npc_schedule_engine import (
    apply_npc_schedule_movements,
    get_current_schedule_entry,
    time_to_minutes,
    update_npc_locations_from_schedule,
)


def build_world():
    return {
        "timeline": {
            "current_time": "11:15",
        },
        "player_character": "elina",
        "locations": [
            {"id": "campus"},
            {"id": "hockey_house"},
            {"id": "library"},
        ],
        "character_locations": {
            "elina": "campus",
            "dean": "campus",
        },
    }


def test_time_to_minutes_valid_time():
    assert time_to_minutes("10:15") == 615


def test_time_to_minutes_invalid_time():
    assert time_to_minutes("99:99") is None
    assert time_to_minutes("bad") is None


def test_get_current_schedule_entry_returns_latest_applicable_entry():
    character = {
        "schedule": [
            {
                "time": "10:00",
                "location": "campus",
            },
            {
                "time": "11:00",
                "location": "hockey_house",
            },
            {
                "time": "14:00",
                "location": "library",
            },
        ]
    }

    entry = get_current_schedule_entry(
        character,
        "11:15",
    )

    assert entry == {
        "time": "11:00",
        "location": "hockey_house",
    }


def test_get_current_schedule_entry_returns_none_without_valid_entry():
    character = {
        "schedule": [
            {
                "time": "14:00",
                "location": "library",
            }
        ]
    }

    entry = get_current_schedule_entry(
        character,
        "11:15",
    )

    assert entry is None


def test_update_npc_locations_from_schedule_moves_npc():
    world = build_world()

    characters = {
        "elina": {},
        "dean": {
            "schedule": [
                {
                    "time": "11:00",
                    "location": "hockey_house",
                }
            ]
        },
    }

    updated_world = update_npc_locations_from_schedule(
        world,
        characters,
    )

    assert updated_world["character_locations"]["dean"] == "hockey_house"


def test_update_npc_locations_from_schedule_does_not_move_player():
    world = build_world()

    characters = {
        "elina": {
            "schedule": [
                {
                    "time": "11:00",
                    "location": "library",
                }
            ]
        }
    }

    updated_world = update_npc_locations_from_schedule(
        world,
        characters,
    )

    assert updated_world["character_locations"]["elina"] == "campus"


def test_update_npc_locations_from_schedule_ignores_invalid_location():
    world = build_world()

    characters = {
        "dean": {
            "schedule": [
                {
                    "time": "11:00",
                    "location": "moon",
                }
            ]
        }
    }

    updated_world = update_npc_locations_from_schedule(
        world,
        characters,
    )

    assert updated_world["character_locations"]["dean"] == "campus"


def test_update_npc_locations_from_schedule_ignores_locked_character():
    world = build_world()

    characters = {
        "dean": {
            "schedule": [
                {
                    "time": "11:00",
                    "location": "hockey_house",
                }
            ]
        }
    }

    updated_world = update_npc_locations_from_schedule(
        world,
        characters,
        ignored_character_ids={
            "dean",
        },
    )

    assert updated_world["character_locations"]["dean"] == "campus"


def test_apply_npc_schedule_movements_returns_movements():
    world = build_world()

    characters = {
        "dean": {
            "schedule": [
                {
                    "time": "11:00",
                    "location": "hockey_house",
                    "activity": "hanging out",
                }
            ]
        }
    }

    updated_world, movements = apply_npc_schedule_movements(
        world,
        characters,
    )

    assert updated_world["character_locations"]["dean"] == "hockey_house"
    assert movements == [
        {
            "character": "dean",
            "from": "campus",
            "to": "hockey_house",
            "activity": "hanging out",
        }
    ]


def test_apply_npc_schedule_movements_ignores_same_location():
    world = build_world()

    characters = {
        "dean": {
            "schedule": [
                {
                    "time": "11:00",
                    "location": "campus",
                }
            ]
        }
    }

    _, movements = apply_npc_schedule_movements(
        world,
        characters,
    )

    assert movements == []
