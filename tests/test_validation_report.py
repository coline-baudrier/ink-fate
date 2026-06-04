from backend.app.core.scene_pipeline import (
    validate_scene_result_with_report,
)


def build_world():
    return {
        "timeline": {
            "current_date": "2026-09-01",
            "current_time": "10:15",
            "current_day": 1,
        },
        "player_character": "elina",
        "locations": [
            {"id": "campus", "name": "Campus"},
        ],
        "characters": [
            "elina",
            "dean",
        ],
        "active_scene": {
            "location": "campus",
            "participants": [
                "elina",
            ],
        },
    }


def test_validate_scene_result_with_report_reports_cleanup():
    scene_result = {
        "scene": {
            "location": "moon",
            "time": "99:99",
            "participants": [
                "dean",
            ],
        },
        "dialogues": [
            {
                "speaker": "elina",
                "text": "Invalid player dialogue.",
            },
            {
                "speaker": "dean",
                "text": "Valid.",
            },
        ],
        "world_updates": {
            "new_location": "moon",
            "time_advance_minutes": 999,
            "character_movements": {},
        },
    }

    validated, report = validate_scene_result_with_report(
        scene_result,
        build_world(),
    )

    assert validated["scene"]["location"] == "campus"
    assert validated["scene"]["time"] == "10:15"
    assert validated["dialogues"] == [
        {
            "speaker": "dean",
            "text": "Valid.",
        }
    ]
    assert any("dialogues" in line for line in report)
    assert any("scene.location" in line for line in report)
    assert any("world_updates.new_location" in line for line in report)


def test_validate_scene_result_with_report_reports_no_cleanup():
    scene_result = {
        "scene": {
            "location": "campus",
            "time": "10:15",
            "participants": [
                "elina",
            ],
        },
        "dialogues": [],
        "world_updates": {
            "new_location": "",
            "time_advance_minutes": 0,
            "character_movements": {},
        },
    }

    _, report = validate_scene_result_with_report(
        scene_result,
        build_world(),
    )

    assert report == [
        "Validation report: no cleanup needed.",
    ]
