from backend.app.core.time_engine import advance_time


def build_world():
    return {
        "timeline": {
            "current_date": "2026-09-01",
            "current_time": "10:00",
            "current_day": 1,
        }
    }


def test_advance_time_adds_minutes():
    world = build_world()

    updated_world = advance_time(
        world,
        15,
    )

    assert updated_world["timeline"]["current_time"] == "10:15"
    assert updated_world["timeline"]["current_day"] == 1


def test_advance_time_wraps_after_midnight():
    world = build_world()
    world["timeline"]["current_time"] = "23:50"

    updated_world = advance_time(
        world,
        20,
    )

    assert updated_world["timeline"]["current_time"] == "00:10"
    assert updated_world["timeline"]["current_day"] == 2


def test_advance_time_can_skip_multiple_days():
    world = build_world()

    updated_world = advance_time(
        world,
        60 * 24 * 2 + 30,
    )

    assert updated_world["timeline"]["current_time"] == "10:30"
    assert updated_world["timeline"]["current_day"] == 3
