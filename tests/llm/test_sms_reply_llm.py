import os

import pytest


if os.getenv("INK_FATE_RUN_LLM_TESTS") != "1":
    pytest.skip(
        "Set INK_FATE_RUN_LLM_TESTS=1 to run LLM tests.",
        allow_module_level=True,
    )

if not os.getenv("OPENAI_API_KEY"):
    pytest.skip(
        "OPENAI_API_KEY is required to run LLM tests.",
        allow_module_level=True,
    )


from backend.app.core.message_engine import apply_player_sms_reply
from backend.app.core.openai_client import generate_text


def build_world():
    return {
        "timeline": {
            "current_day": 1,
            "current_date": "2026-09-01",
            "current_time": "10:30",
        },
        "player_character": "elina",
        "character_locations": {
            "dean": "campus",
            "elina": "dormitory",
        },
        "active_scene": {
            "location": "dormitory",
            "participants": [
                "elina",
            ],
        },
        "event_log": [],
        "messages": [
            {
                "from": "dean",
                "to": "elina",
                "channel": "sms",
                "content": (
                    "Demain matin. Patinoire. 7h. "
                    "Si tu survis a la premiere heure, je te paie un cafe."
                ),
                "status": "unread",
                "trigger": "skating_lesson_followup",
            }
        ],
    }


def build_characters():
    return {
        "dean": {
            "identity": {
                "first_name": "Dean",
                "last_name": "Di Laurentis",
            },
            "archetype": "charmer",
            "current_goals": [
                "keep social interactions playful",
                "avoid emotional vulnerability",
            ],
            "speech_style": [
                "confident, teasing and direct",
                "uses playful provocation",
            ],
            "behavior_rules": [
                "when challenged, accepts quickly and raises the stakes",
                "hides sincere interest behind jokes",
            ],
            "contacts": {
                "elina": {
                    "phone_number_known": True,
                }
            },
            "relationships": {
                "elina": {
                    "respect": 7,
                    "attraction": 5,
                }
            },
        },
        "elina": {
            "identity": {
                "first_name": "Elina",
                "last_name": "Maxwell",
            },
            "contacts": {},
        },
    }


def build_generic_world():
    world = build_world()
    world["messages"] = []
    world["character_locations"]["beau"] = "campus"

    return world


def build_generic_characters():
    characters = build_characters()
    characters["beau"] = {
        "identity": {
            "first_name": "Beau",
            "last_name": "Maxwell",
        },
        "archetype": "protective_brother",
        "speech_style": [
            "protective but not humorless",
            "uses dry warnings",
        ],
        "behavior_rules": [
            "protects people he loves while respecting their independence",
        ],
        "contacts": {
            "elina": {
                "phone_number_known": True,
            }
        },
        "relationships": {
            "elina": {
                "trust": 95,
                "attachment": 100,
            }
        },
    }
    characters["elina"]["contacts"] = {
        "beau": {
            "phone_number_known": True,
        }
    }

    return characters


@pytest.mark.llm
def test_llm_can_write_npc_sms_reply_content():
    world, result = apply_player_sms_reply(
        build_world(),
        build_characters(),
        {
            "to": "dean",
            "content": "Ok pour 7h. Essaie de ne pas etre en retard.",
        },
        generate_text,
    )

    assert result["sent"] is True
    assert len(result["npc_replies"]) == 1

    reply = result["npc_replies"][0]

    assert reply["from"] == "dean"
    assert reply["to"] == "elina"
    assert reply["channel"] == "sms"
    assert reply["trigger"] == "skating_lesson_reply_confirmation"
    assert isinstance(reply["content"], str)
    assert reply["content"].strip()
    assert len(reply["content"]) <= 240
    assert "Dean:" not in reply["content"]
    assert "Elina:" not in reply["content"]
    assert world["active_scene"] == {
        "location": "dormitory",
        "participants": [
            "elina",
        ],
    }


@pytest.mark.llm
def test_llm_can_write_generic_npc_sms_reply_content():
    world, result = apply_player_sms_reply(
        build_generic_world(),
        build_generic_characters(),
        {
            "to": "beau",
            "content": (
                "Je suis au dortoir. Pas besoin de venir verifier, "
                "je gere."
            ),
        },
        generate_text,
    )

    assert result["sent"] is True
    assert len(result["npc_replies"]) == 1

    reply = result["npc_replies"][0]

    assert reply["from"] == "beau"
    assert reply["to"] == "elina"
    assert reply["channel"] == "sms"
    assert reply["trigger"].startswith("generic_sms_reply_beau_to_elina")
    assert isinstance(reply["content"], str)
    assert reply["content"].strip()
    assert len(reply["content"]) <= 240
    assert "Beau:" not in reply["content"]
    assert "Elina:" not in reply["content"]
