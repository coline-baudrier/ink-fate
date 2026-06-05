from backend.app.core.prompt_builder import (
    build_contact_intent_context,
    build_event_log_context,
    build_player_context,
    build_player_intent_context,
    build_scenario_context,
    build_scene_history_context,
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
                "contacts": {
                    "dean": {
                        "phone_number_known": False,
                        "phone_numbers_exchanged": False,
                        "instagram_connected": False,
                    }
                },
                "memories": [],
            },
            {
                "id": "dean",
                "identity": {
                    "first_name": "Dean",
                    "last_name": "Di Laurentis",
                },
                "contacts": {
                    "elina": {
                        "phone_number_known": False,
                        "phone_numbers_exchanged": False,
                        "instagram_connected": False,
                    }
                },
                "memories": [],
            },
        ],
    }


def build_scenario():
    return {
        "title": "Arrival at Briar",
        "premise": "Elina arrives at Briar University.",
        "tone": [
            "contemporary college romance",
            "natural modern dialogue",
        ],
        "canon_rules": [
            "Beau is Elina's older brother.",
        ],
        "character_dynamics": [
            "Dean should answer Elina directly.",
        ],
        "narrative_limits": [
            "Do not invent another university name.",
        ],
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
                "available_beats": [
                    "playful_challenge",
                    "missed_connection",
                ],
                "blocked_beats": [
                    "official_couple",
                ],
            }
        ],
    }


def test_build_scene_history_context_returns_empty_when_none():
    assert build_scene_history_context(None) == "No previous scene yet."


def test_build_scene_history_context_returns_empty_when_empty_list():
    assert build_scene_history_context([]) == "No previous scene yet."


def test_build_scene_history_context_formats_turns():
    turns = [
        {"player_input": None, "scene_text": "Opening scene text."},
        {"player_input": "Je lui parle.", "scene_text": "Dean répond."},
    ]

    context = build_scene_history_context(turns)

    assert "Opening scene text." in context
    assert "Player: Je lui parle." in context
    assert "Dean répond." in context


def test_build_scene_history_context_limits_to_max_prompt():
    turns = [
        {"player_input": f"Action {i}", "scene_text": f"Scene {i}"}
        for i in range(10)
    ]

    context = build_scene_history_context(turns)

    assert "Scene 9" in context
    assert "Scene 8" in context
    assert "Scene 0" not in context


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
        build_scenario(),
        build_scene_context(),
    )

    assert "RECENT EVENTS" in prompt
    assert "Elina arrives on campus." in prompt


def test_structured_prompt_includes_planned_events_section():
    world = build_world()
    world["planned_events"] = [
        {
            "id": "planned_skating_lesson_dean_elina_day2_0700",
            "type": "planned_event",
            "status": "scheduled",
            "participants": [
                "dean",
                "elina",
            ],
            "day": 2,
            "time": "07:00",
            "location": "ice_rink",
            "summary": (
                "Dean and Elina agreed to meet at the rink for a "
                "skating lesson."
            ),
        }
    ]

    prompt = build_structured_scene_prompt(
        world,
        build_scenario(),
        build_scene_context(),
    )

    assert "PLANNED EVENTS" in prompt
    assert "Day 2, 07:00, location ice_rink (dean, elina)" in prompt
    assert "skating lesson" in prompt


def test_build_scenario_context_formats_scenario_rules():
    context = build_scenario_context(build_scenario())

    assert "Title: Arrival at Briar" in context
    assert "Premise: Elina arrives at Briar University." in context
    assert "- contemporary college romance" in context
    assert "- Beau is Elina's older brother." in context
    assert "- Dean should answer Elina directly." in context
    assert "- Do not invent another university name." in context


def test_build_scenario_context_ignores_invalid_sections():
    scenario = {
        "title": "Arrival at Briar",
        "premise": "Elina arrives at Briar University.",
        "tone": "not-a-list",
        "canon_rules": [
            "Valid rule.",
        ],
    }

    context = build_scenario_context(scenario)

    assert "Tone:" in context
    assert "- not-a-list" not in context
    assert "- Valid rule." in context


def test_structured_prompt_includes_scenario_context():
    prompt = build_structured_scene_prompt(
        build_world(),
        build_scenario(),
        build_scene_context(),
    )

    assert "SCENARIO CONTEXT" in prompt
    assert "Elina arrives at Briar University." in prompt
    assert "Beau is Elina's older brother." in prompt


def test_structured_prompt_includes_story_arcs():
    prompt = build_structured_scene_prompt(
        build_world(),
        build_scenario(),
        build_scene_context(),
    )

    assert "STORY ARCS" in prompt
    assert "dean_elina_slow_burn" in prompt
    assert "Available beats: playful_challenge; missed_connection" in prompt
    assert "Blocked beats: official_couple" in prompt
    assert "Available beats are opportunities, not obligations." in prompt
    assert "Never force a couple outcome" in prompt


def test_structured_prompt_includes_observed_arc_state():
    world = build_world()
    world["arc_state"] = {
        "dean_elina_slow_burn": {
            "phase": "initial_tension",
            "played_beats": [
                "playful_challenge",
                "text_followup",
            ],
            "signals": [
                "playful_challenge_seen",
                "text_followup_seen",
            ],
        }
    }

    prompt = build_structured_scene_prompt(
        world,
        build_scenario(),
        build_scene_context(),
    )

    assert "OBSERVED ARC STATE" in prompt
    assert "Arc state: dean_elina_slow_burn" in prompt
    assert "Played beats: playful_challenge; text_followup" in prompt
    assert "Avoid repeating the same beat" in prompt


def test_structured_prompt_includes_runtime_directives():
    world = build_world()
    world["runtime_directives"] = [
        {
            "type": "rule",
            "content": "Dean doit rester plus subtil.",
            "scope": "session",
        }
    ]

    prompt = build_structured_scene_prompt(
        world,
        build_scenario(),
        build_scene_context(),
    )

    assert "RUNTIME GM DIRECTIVES" in prompt
    assert "- rule (session): Dean doit rester plus subtil." in prompt
    assert "cannot override" in prompt


def test_structured_prompt_includes_contact_access_rules():
    prompt = build_structured_scene_prompt(
        build_world(),
        build_scenario(),
        build_scene_context(),
    )

    assert "CONTACT ACCESS" in prompt
    assert "elina -> dean" in prompt
    assert "contact_updates" in prompt
    assert "phone_number_known true" in prompt
    assert "through a third party" in prompt


def test_build_player_context_treats_empty_input_as_waiting():
    context = build_player_context("   ")

    assert "wait and observe briefly" in context
    assert "current active location" in context
    assert "opening scene" not in context


def test_structured_prompt_includes_player_movement_rules():
    prompt = build_structured_scene_prompt(
        build_world(),
        build_scenario(),
        build_scene_context(),
        "",
    )

    assert "If the player clearly leaves" in prompt
    assert "the next active scene follows the player character" in prompt
    assert "Do not continue NPC-only scenes" in prompt


def test_structured_prompt_limits_scene_to_active_participants():
    prompt = build_structured_scene_prompt(
        build_world(),
        build_scenario(),
        build_scene_context(),
        "",
    )

    assert "Only the character IDs listed above are physically present" in prompt
    assert "Do not describe absent NPCs as nearby" in prompt
    assert "scene.participants and dialogues.speaker must stay limited" in prompt
    assert "Do not describe the player character as feeling" in prompt


def test_build_player_intent_context_reports_no_movement():
    context = build_player_intent_context({})

    assert context == "No explicit player movement detected."


def test_build_player_intent_context_reports_detected_movement():
    context = build_player_intent_context(
        {
            "player_intent_hints": {
                "detected_movement": "dormitory",
            }
        }
    )

    assert (
        "The player input clearly indicates movement to location: dormitory."
        in context
    )
    assert (
        'must set world_updates.new_location to "dormitory"'
        in context
    )


def test_build_player_intent_context_reports_npcs_left_behind():
    context = build_player_intent_context(
        {
            "player_intent_hints": {
                "detected_movement": "dormitory",
                "leaves_npcs_behind": True,
            }
        }
    )

    assert "The player explicitly leaves the NPCs behind." in context
    assert "Do not move NPCs with the player" in context
    assert "usually without the NPCs left behind" in context
    assert "at most one brief departure reaction" in context


def test_build_contact_intent_context_reports_no_contact_intent():
    context = build_contact_intent_context({})

    assert context == "No explicit player contact intent detected."


def test_build_contact_intent_context_reports_phone_recipient():
    context = build_contact_intent_context(
        {
            "contact_intent_hints": {
                "phone_number_given_to": "dean",
            }
        }
    )

    assert "The player explicitly gives their phone number to: dean." in context
    assert 'source "dean", target "elina"' in context
    assert "source is the character who gains access" in context
