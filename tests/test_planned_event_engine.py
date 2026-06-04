from backend.app.core.planned_event_engine import (
    SKATING_LESSON_PLANNED_EVENT_ID,
    append_planned_event,
    apply_planned_events_after_scene,
    build_planned_events_context,
    build_skating_lesson_planned_event,
)


def build_world():
    return {
        "timeline": {
            "current_day": 1,
            "current_date": "2026-09-01",
            "current_time": "10:30",
        },
        "locations": [
            {
                "id": "campus",
                "name": "Campus",
            },
            {
                "id": "ice_rink",
                "name": "Briar Ice Rink",
            },
        ],
        "planned_events": [],
    }


def test_build_skating_lesson_planned_event_uses_valid_location():
    planned_event = build_skating_lesson_planned_event(
        build_world(),
        "sms",
    )

    assert planned_event == {
        "id": SKATING_LESSON_PLANNED_EVENT_ID,
        "type": "planned_event",
        "trigger": "skating_lesson_planned_meeting",
        "status": "scheduled",
        "participants": [
            "dean",
            "elina",
        ],
        "day": 2,
        "time": "07:00",
        "summary": (
            "Dean and Elina agreed to meet at the rink for a skating lesson."
        ),
        "source": "sms",
        "location": "ice_rink",
    }


def test_build_skating_lesson_planned_event_omits_invalid_location():
    world = build_world()
    world["locations"] = [
        {
            "id": "campus",
            "name": "Campus",
        }
    ]

    planned_event = build_skating_lesson_planned_event(
        world,
        "scene",
    )

    assert "location" not in planned_event
    assert planned_event["source"] == "scene"


def test_append_planned_event_does_not_duplicate_id():
    world = build_world()
    planned_event = build_skating_lesson_planned_event(
        world,
        "sms",
    )

    world = append_planned_event(
        world,
        planned_event,
    )
    world = append_planned_event(
        world,
        planned_event,
    )

    assert world["planned_events"] == [
        planned_event,
    ]


def test_apply_planned_events_after_scene_detects_spoken_plan():
    world = build_world()
    scene_result = {
        "narration": [
            "Dean pointe vers la sortie du campus.",
        ],
        "dialogues": [
            {
                "speaker": "dean",
                "text": (
                    "Demain 7h a la patinoire, elina. "
                    "On verra si tu tiens debout."
                ),
            }
        ],
        "events": [
            {
                "type": "challenge",
                "participants": [
                    "dean",
                    "elina",
                ],
                "summary": (
                    "dean and elina agree on a skating lesson tomorrow at 7h."
                ),
            }
        ],
    }

    world = apply_planned_events_after_scene(
        world,
        scene_result,
    )

    assert world["planned_events"][0]["trigger"] == (
        "skating_lesson_planned_meeting"
    )
    assert world["planned_events"][0]["source"] == "scene"


def test_apply_planned_events_after_scene_ignores_vague_skating_context():
    world = build_world()
    scene_result = {
        "dialogues": [
            {
                "speaker": "dean",
                "text": "Un jour je te montrerai peut-etre la patinoire.",
            }
        ],
        "events": [],
        "memory_updates": [],
    }

    world = apply_planned_events_after_scene(
        world,
        scene_result,
    )

    assert world["planned_events"] == []


def test_build_planned_events_context_formats_scheduled_events():
    world = build_world()
    world = append_planned_event(
        world,
        build_skating_lesson_planned_event(
            world,
            "sms",
        ),
    )

    context = build_planned_events_context(world)

    assert "Day 2, 07:00, location ice_rink (dean, elina)" in context
    assert "skating lesson" in context


def test_build_planned_events_context_empty_message():
    assert build_planned_events_context({}) == "No planned events yet."
