from backend.app.core.event_log_engine import update_event_log_after_scene


def build_world():
    return {
        "timeline": {
            "current_day": 1,
            "current_date": "2026-09-01",
            "current_time": "10:15",
        },
        "event_log": [],
    }


def test_update_event_log_adds_event():
    world = build_world()

    scene_result = {
        "narration": [
            "Elina arrive au dortoir avec sa valise."
        ],
        "events": [
            {
                "type": "location_change",
                "participants": ["elina"],
                "summary": "Elina rejoint le dortoir.",
            }
        ],
    }

    updated_world = update_event_log_after_scene(
        world,
        scene_result,
    )

    assert len(updated_world["event_log"]) == 1

    event = updated_world["event_log"][0]

    assert event["day"] == 1
    assert event["date"] == "2026-09-01"
    assert event["time"] == "10:15"
    assert event["type"] == "location_change"
    assert event["participants"] == ["elina"]
    assert event["summary"] == "Elina rejoint le dortoir."


def test_update_event_log_ignores_invalid_events():
    world = build_world()

    scene_result = {
        "events": [
            "invalid",
            {
                "type": "",
                "participants": ["elina"],
            },
        ],
    }

    updated_world = update_event_log_after_scene(
        world,
        scene_result,
    )

    assert updated_world["event_log"] == []


def test_update_event_log_creates_event_log_if_missing():
    world = {
        "timeline": {
            "current_day": 1,
            "current_date": "2026-09-01",
            "current_time": "10:15",
        }
    }

    scene_result = {
        "events": [
            {
                "type": "arrival",
                "participants": ["elina"],
            }
        ],
        "narration": [
            "Elina arrive sur le campus."
        ],
    }

    updated_world = update_event_log_after_scene(
        world,
        scene_result,
    )

    assert len(updated_world["event_log"]) == 1
    assert updated_world["event_log"][0]["summary"] == (
        "Elina arrive sur le campus."
    )


def test_update_event_log_trims_to_max_size():
    world = {
        "timeline": {
            "current_day": 1,
            "current_date": "2026-09-01",
            "current_time": "10:15",
        },
        "event_log": [
            {
                "day": 1,
                "date": "2026-09-01",
                "time": "09:00",
                "type": "old_event",
                "participants": ["elina"],
                "summary": f"Old event {i}",
            }
            for i in range(100)
        ],
    }

    scene_result = {
        "events": [
            {
                "type": "new_event",
                "participants": ["elina"],
                "summary": "Brand new event.",
            }
        ],
    }

    updated_world = update_event_log_after_scene(world, scene_result)

    assert len(updated_world["event_log"]) == 100
    assert updated_world["event_log"][-1]["summary"] == "Brand new event."
    assert updated_world["event_log"][0]["summary"] == "Old event 1"