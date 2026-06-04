from backend.app.core.character_state_engine import (
    update_characters_after_scene,
)
from backend.app.core.contact_intent_parser import (
    apply_contact_intent_hints,
    build_contact_intent_hints,
)
from backend.app.core.message_engine import (
    append_pending_messages,
    generate_pending_messages,
)
from backend.app.core.player_intent_parser import (
    apply_player_intent_hints,
    build_player_intent_hints,
)
from backend.app.core.prompt_builder import build_player_context
from backend.app.core.scene_pipeline import validate_scene_result
from backend.app.core.world_engine import update_world_after_turn


def build_world():
    return {
        "timeline": {
            "current_day": 1,
            "current_date": "2026-09-01",
            "current_time": "10:30",
        },
        "player_character": "elina",
        "locations": [
            {"id": "campus", "name": "Campus"},
            {"id": "dormitory", "name": "Dormitory"},
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
        "event_log": [],
        "messages": [],
    }


def build_characters():
    return {
        "elina": {
            "contacts": {
                "dean": {
                    "phone_number_known": False,
                    "phone_numbers_exchanged": False,
                    "instagram_connected": False,
                }
            },
            "memories": [],
        },
        "beau": {
            "contacts": {},
            "memories": [],
        },
        "dean": {
            "contacts": {
                "elina": {
                    "phone_number_known": False,
                    "phone_numbers_exchanged": False,
                    "instagram_connected": False,
                }
            },
            "memories": [],
        },
    }


def build_scene_context():
    return {
        "participants": [
            {
                "id": "elina",
                "identity": {
                    "first_name": "Elina",
                },
            },
            {
                "id": "beau",
                "identity": {
                    "first_name": "Beau",
                },
            },
            {
                "id": "dean",
                "identity": {
                    "first_name": "Dean",
                },
            },
        ]
    }


def test_dean_skating_number_departure_message_and_empty_input_flow():
    world = build_world()
    characters = build_characters()
    player_input = (
        '"Je te donne mon numero pour la patinoire." '
        '*J avance vers mon dortoir les laissant la*'
    )
    scene_context = build_scene_context()

    scene_result = {
        "scene": {
            "location": "campus",
            "time": "10:30",
            "participants": [
                "elina",
                "beau",
                "dean",
            ],
        },
        "narration": [
            "Elina donne son numero a Dean pour la patinoire et part.",
        ],
        "dialogues": [
            {
                "speaker": "dean",
                "text": "Je te recontacte pour le defi sur la patinoire.",
            }
        ],
        "actions": [],
        "events": [
            {
                "type": "skating_challenge",
                "participants": [
                    "dean",
                    "elina",
                ],
                "summary": "Dean gets Elina's number for the skating lesson.",
            }
        ],
        "relationship_updates": [],
        "contact_updates": [
            {
                "source": "elina",
                "target": "dean",
                "changes": {
                    "phone_number_known": True,
                },
            }
        ],
        "memory_updates": [
            {
                "owner": "dean",
                "type": "memory",
                "content": "Dean can text Elina about the patinoire lesson.",
                "importance": 8,
                "age": 0,
                "tags": [
                    "patinoire",
                ],
            }
        ],
        "world_updates": {
            "new_location": "",
            "time_advance_minutes": 0,
            "character_movements": {
                "beau": "dormitory",
                "dean": "campus",
            },
        },
    }

    scene_result = validate_scene_result(
        scene_result,
        world,
    )
    scene_result = apply_contact_intent_hints(
        scene_result,
        world,
        build_contact_intent_hints(
            player_input,
            world,
            scene_context,
        ),
    )
    scene_result = apply_player_intent_hints(
        scene_result,
        world,
        build_player_intent_hints(
            player_input,
            world,
        ),
    )

    characters = update_characters_after_scene(
        scene_result,
        characters,
    )
    world = update_world_after_turn(
        world,
        characters,
        scene_result,
    )
    messages = generate_pending_messages(
        world,
        characters,
        scene_result,
        None,
        {
            "player_input": player_input,
        },
    )
    world = append_pending_messages(
        world,
        messages,
    )
    duplicate_messages = generate_pending_messages(
        world,
        characters,
        scene_result,
        None,
        {
            "player_input": player_input,
        },
    )

    empty_input_context = build_player_context("")

    assert world["character_locations"]["elina"] == "dormitory"
    assert world["character_locations"]["dean"] == "campus"
    assert world["character_locations"]["beau"] == "campus"
    assert (
        characters["dean"]["contacts"]["elina"]["phone_number_known"]
        is True
    )
    assert len(messages) == 1
    assert messages[0]["from"] == "dean"
    assert messages[0]["to"] == "elina"
    assert messages[0]["trigger"] == "skating_lesson_followup"
    assert duplicate_messages == []
    assert "wait and observe briefly" in empty_input_context
    assert "current active location" in empty_input_context
