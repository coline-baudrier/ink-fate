from backend.app.core.story_arc_engine import build_story_arcs_context


def test_build_story_arcs_context_empty_message():
    assert build_story_arcs_context({}) == "No active story arcs defined."


def test_build_story_arcs_context_formats_active_arc():
    context = build_story_arcs_context(
        {
            "story_arcs": [
                {
                    "id": "dean_elina_slow_burn",
                    "title": "Dean and Elina slow-burn tension",
                    "status": "active",
                    "phase": "initial_tension",
                    "participants": [
                        "dean",
                        "elina",
                    ],
                    "dramatic_questions": [
                        "Will Elina reject Dean's challenge?",
                    ],
                    "available_beats": [
                        "playful_challenge",
                        "missed_connection",
                    ],
                    "blocked_beats": [
                        "official_couple",
                    ],
                    "progress_signals": [
                        "Dean makes a concrete effort.",
                    ],
                }
            ]
        }
    )

    assert "- Arc: dean_elina_slow_burn" in context
    assert "Current phase: initial_tension" in context
    assert "Participants: dean; elina" in context
    assert "Available beats: playful_challenge; missed_connection" in context
    assert "Blocked beats: official_couple" in context


def test_build_story_arcs_context_ignores_inactive_arc():
    context = build_story_arcs_context(
        {
            "story_arcs": [
                {
                    "id": "resolved_arc",
                    "status": "complete",
                    "available_beats": [
                        "unused",
                    ],
                }
            ]
        }
    )

    assert context == "No active story arcs defined."


def test_build_story_arcs_context_ignores_invalid_values():
    context = build_story_arcs_context(
        {
            "story_arcs": [
                {
                    "id": "valid_arc",
                    "participants": "not-a-list",
                    "available_beats": [
                        "valid_beat",
                        123,
                        "",
                    ],
                },
                "invalid",
            ]
        }
    )

    assert "valid_arc" in context
    assert "not-a-list" not in context
    assert "valid_beat" in context
    assert "123" not in context
