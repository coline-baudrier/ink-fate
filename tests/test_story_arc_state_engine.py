from backend.app.core.story_arc_state_engine import (
    apply_story_arc_state_after_scene,
    apply_story_arc_state_from_messages,
    build_story_arc_state_context,
)


def build_world():
    return {
        "timeline": {
            "current_day": 1,
        },
    }


def build_scenario():
    return {
        "story_arcs": [
            {
                "id": "dean_elina_slow_burn",
                "title": "Dean and Elina slow-burn tension",
                "status": "active",
                "phase": "initial_tension",
                "participants": [
                    "dean",
                    "elina",
                    "beau",
                ],
            }
        ]
    }


def test_apply_story_arc_state_after_scene_detects_playful_challenge():
    world = apply_story_arc_state_after_scene(
        build_world(),
        build_scenario(),
        {
            "scene": {
                "participants": [
                    "dean",
                    "elina",
                ],
            },
            "events": [
                {
                    "type": "challenge",
                    "participants": [
                        "dean",
                        "elina",
                    ],
                    "summary": "Dean lance un defi patinoire a Elina.",
                }
            ],
            "dialogues": [],
            "memory_updates": [],
        },
    )

    state = world["arc_state"]["dean_elina_slow_burn"]

    assert state["phase"] == "initial_tension"
    assert state["signals"] == [
        "playful_challenge_seen",
    ]
    assert state["played_beats"] == [
        "playful_challenge",
    ]
    assert state["last_updated_day"] == 1


def test_apply_story_arc_state_after_scene_detects_boundary_once():
    world = build_world()
    scenario = build_scenario()
    scene_result = {
        "scene": {
            "participants": [
                "beau",
                "elina",
            ],
        },
        "narration": [
            "Elina pose une limite et part seule sans eux.",
        ],
        "events": [],
        "dialogues": [],
        "memory_updates": [],
    }

    world = apply_story_arc_state_after_scene(
        world,
        scenario,
        scene_result,
    )
    world = apply_story_arc_state_after_scene(
        world,
        scenario,
        scene_result,
    )

    state = world["arc_state"]["dean_elina_slow_burn"]

    assert state["signals"] == [
        "boundary_set_by_player",
    ]
    assert state["played_beats"] == [
        "boundary_set_by_player",
    ]


def test_apply_story_arc_state_from_messages_detects_text_followup():
    world = apply_story_arc_state_from_messages(
        build_world(),
        [
            {
                "from": "dean",
                "to": "elina",
                "trigger": "skating_lesson_followup",
                "content": "Demain matin. Patinoire. 7h.",
            }
        ],
        build_scenario(),
    )

    state = world["arc_state"]["dean_elina_slow_burn"]

    assert state["signals"] == [
        "text_followup_seen",
        "playful_challenge_seen",
    ]
    assert state["played_beats"] == [
        "text_followup",
        "playful_challenge",
    ]


def test_apply_story_arc_state_from_messages_uses_existing_arc_state_fallback():
    world = build_world()
    world["arc_state"] = {
        "dean_elina_slow_burn": {
            "phase": "initial_tension",
            "played_beats": [],
            "signals": [],
        }
    }

    world = apply_story_arc_state_from_messages(
        world,
        [
            {
                "from": "elina",
                "to": "dean",
                "trigger": "player_reply",
                "content": "Ok pour 7h.",
            }
        ],
    )

    assert world["arc_state"]["dean_elina_slow_burn"]["signals"] == [
        "text_followup_seen",
    ]


def test_build_story_arc_state_context_formats_state():
    world = {
        "arc_state": {
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
    }

    context = build_story_arc_state_context(
        world,
        build_scenario(),
    )

    assert "Arc state: dean_elina_slow_burn" in context
    assert "Title: Dean and Elina slow-burn tension" in context
    assert "Runtime phase: initial_tension" in context
    assert "Played beats: playful_challenge; text_followup" in context
    assert "Observed signals: playful_challenge_seen; text_followup_seen" in context


def test_build_story_arc_state_context_empty_message():
    assert build_story_arc_state_context({}) == "No observed arc state yet."
