from backend.app.core.prompt_builder import (
    build_event_log_context,
    build_structured_scene_prompt,
)


def build_world():
    return {
        "universe": {
            "name": "Off Campus",
        },
        "timeline": {
            "current_date": "2026-09-01",
            "current_time": "10:15",
            "current_day": 1,
        },
        "player_character": "elina",
        "locations": [
            {
                "id": "campus",
                "name": "Campus",
                "description": "Campus description.",
            }
        ],
        "characters": [
            "elina",
            "dean",
        ],
        "event_log": [
            {
                "day": 1,
                "date": "2026-09-01",
                "time": "10:05",
                "type": "arrival",
                "participants": [
                    "elina",
                ],
                "summary": "Elina arrives on campus.",
            }
        ],
    }


def build_scene_context():
    return {
        "location": {
            "id": "campus",
            "name": "Campus",
            "description": "Campus description.",
        },
        "date": "2026-09-01",
        "time": "10:15",
        "participants": [
            {
                "id": "elina",
                "identity": {
                    "first_name": "Elina",
                    "last_name": "Maxwell",
                },
                "memories": [],
            },
            {
                "id": "dean",
                "identity": {
                    "first_name": "Dean",
                    "last_name": "Di Laurentis",
                },
                "memories": [],
            },
        ],
    }


def test_build_event_log_context_returns_empty_message():
    context = build_event_log_context(
        {
            "event_log": [],
        }
    )

    assert context == "No important events recorded yet."


def test_build_event_log_context_formats_recent_events():
    world = build_world()

    context = build_event_log_context(world)

    assert "Day 1, 10:05, arrival (elina)" in context
    assert "Elina arrives on campus." in context


def test_build_event_log_context_keeps_only_recent_events():
    world = {
        "event_log": [
            {
                "day": 1,
                "time": f"10:0{index}",
                "type": "event",
                "participants": [],
                "summary": f"Event {index}",
            }
            for index in range(6)
        ]
    }

    context = build_event_log_context(
        world,
        max_events=3,
    )

    assert "Event 2" not in context
    assert "Event 3" in context
    assert "Event 4" in context
    assert "Event 5" in context


def test_structured_prompt_includes_recent_events_section():
    prompt = build_structured_scene_prompt(
        build_world(),
        build_scene_context(),
    )

    assert "RECENT EVENTS" in prompt
    assert "Elina arrives on campus." in prompt
