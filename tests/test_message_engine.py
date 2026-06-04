from backend.app.core.character_state_engine import (
    update_characters_after_scene,
)
from backend.app.core.message_engine import (
    append_pending_messages,
    apply_player_sms_reply,
    build_npc_sms_reply_content,
    generate_pending_messages,
    get_player_messages,
    mark_player_messages_read,
    parse_sms_reply_command,
    sanitize_llm_sms_content,
)
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
            "dean",
            "beau",
            "elina",
        ],
        "active_scene": {
            "location": "dormitory",
            "participants": [
                "elina",
            ],
        },
        "character_locations": {
            "dean": "campus",
            "beau": "campus",
            "elina": "dormitory",
        },
        "event_log": [],
        "messages": [],
    }


def build_characters(dean_knows_elina_phone=True):
    return {
        "dean": {
            "contacts": {
                "elina": {
                    "phone_number_known": dean_knows_elina_phone,
                    "phone_numbers_exchanged": False,
                    "instagram_connected": False,
                }
            },
            "memories": [],
        },
        "beau": {
            "identity": {
                "first_name": "Beau",
                "last_name": "Maxwell",
            },
            "archetype": "protective_brother",
            "speech_style": [
                "protective but not humorless",
                "uses dry warnings",
            ],
            "contacts": {
                "elina": {
                    "phone_number_known": True,
                    "phone_numbers_exchanged": True,
                    "instagram_connected": True,
                }
            },
            "relationships": {
                "elina": {
                    "trust": 95,
                    "attachment": 100,
                }
            },
            "memories": [],
        },
        "elina": {
            "contacts": {},
            "memories": [],
        },
    }


def build_scene_result_with_skating_context():
    return {
        "memory_updates": [
            {
                "owner": "dean",
                "content": "Dean promised Elina a skating lesson.",
            }
        ],
        "events": [
            {
                "type": "challenge",
                "participants": [
                    "dean",
                    "elina",
                ],
                "summary": "Dean mentions the patinoire challenge.",
            }
        ],
        "dialogues": [
            {
                "speaker": "dean",
                "text": "On verra si tu tiens sur des patins.",
            }
        ],
    }


def test_generate_pending_messages_for_dean_skating_followup():
    messages = generate_pending_messages(
        build_world(),
        build_characters(),
        build_scene_result_with_skating_context(),
    )

    assert messages == [
        {
            "id": "dean-elina-skating_lesson_followup-d1-1030",
            "from": "dean",
            "to": "elina",
            "channel": "sms",
            "content": (
                "Demain matin. Patinoire. 7h. "
                "Si tu survis a la premiere heure, je te paie un cafe."
            ),
            "sent_at_day": 1,
            "sent_at_time": "10:30",
            "status": "unread",
            "trigger": "skating_lesson_followup",
        }
    ]


def test_generate_pending_messages_uses_scenario_trigger_config():
    messages = generate_pending_messages(
        build_world(),
        build_characters(),
        {
            "events": [
                {
                    "summary": "Dean promises a rink challenge.",
                }
            ],
        },
        {
            "message_triggers": [
                {
                    "trigger": "skating_lesson_followup",
                    "content": "Rink. Seven. Coffee if you survive.",
                    "keywords": [
                        "rink",
                    ],
                }
            ]
        },
    )

    assert messages[0]["content"] == "Rink. Seven. Coffee if you survive."


def test_generate_pending_messages_uses_generic_scenario_trigger():
    scene_result = {
        "events": [
            {
                "summary": "Elina reaches the dormitory and settles in.",
            }
        ],
    }
    scenario = {
        "message_triggers": [
            {
                "trigger": "beau_dormitory_checkin",
                "from": "beau",
                "to": "elina",
                "channel": "sms",
                "content": (
                    "T'es bien arrivee au dortoir ? "
                    "Je te laisse respirer, promis."
                ),
                "keywords": [
                    "dormitory",
                    "dortoir",
                    "settles",
                ],
            }
        ]
    }

    messages = generate_pending_messages(
        build_world(),
        build_characters(),
        scene_result,
        scenario,
    )

    assert messages == [
        {
            "id": "beau-elina-beau_dormitory_checkin-d1-1030",
            "from": "beau",
            "to": "elina",
            "channel": "sms",
            "content": (
                "T'es bien arrivee au dortoir ? "
                "Je te laisse respirer, promis."
            ),
            "sent_at_day": 1,
            "sent_at_time": "10:30",
            "status": "unread",
            "trigger": "beau_dormitory_checkin",
        }
    ]


def test_generate_pending_messages_can_use_llm_for_generic_trigger():
    scene_result = {
        "events": [
            {
                "summary": "Elina reaches the dormitory and settles in.",
            }
        ],
    }
    scenario = {
        "message_triggers": [
            {
                "trigger": "beau_dormitory_checkin",
                "from": "beau",
                "to": "elina",
                "channel": "sms",
                "content": "Tout va bien au dortoir ?",
                "keywords": [
                    "dormitory",
                ],
            }
        ]
    }

    def fake_generate_text(prompt):
        assert "The sender is Beau Maxwell (beau)." in prompt
        assert "RECENT NARRATIVE CONTEXT" in prompt
        assert "beau_dormitory_checkin" in prompt
        return '"T’es au dortoir ? Je te laisse tranquille, mais confirme-moi que tout va bien."'

    messages = generate_pending_messages(
        build_world(),
        build_characters(),
        scene_result,
        scenario,
        None,
        fake_generate_text,
    )

    assert messages[0]["content"] == (
        "T’es au dortoir ? Je te laisse tranquille, "
        "mais confirme-moi que tout va bien."
    )


def test_generate_pending_messages_falls_back_when_llm_fails():
    scenario = {
        "message_triggers": [
            {
                "trigger": "beau_dormitory_checkin",
                "from": "beau",
                "to": "elina",
                "channel": "sms",
                "content": "Tout va bien au dortoir ?",
                "keywords": [
                    "dortoir",
                ],
            }
        ]
    }

    def failing_generate_text(prompt):
        raise RuntimeError("api down")

    messages = generate_pending_messages(
        build_world(),
        build_characters(),
        {
            "events": [
                {
                    "summary": "Elina arrive au dortoir.",
                }
            ]
        },
        scenario,
        None,
        failing_generate_text,
    )

    assert messages[0]["content"] == "Tout va bien au dortoir ?"


def test_generate_pending_messages_requires_sender_contact_access():
    characters = build_characters()
    characters["beau"]["contacts"]["elina"] = {
        "phone_number_known": False,
        "phone_numbers_exchanged": False,
    }
    scenario = {
        "message_triggers": [
            {
                "trigger": "beau_dormitory_checkin",
                "from": "beau",
                "to": "elina",
                "channel": "sms",
                "content": "Tout va bien ?",
                "keywords": [
                    "dortoir",
                ],
            }
        ]
    }

    messages = generate_pending_messages(
        build_world(),
        characters,
        {
            "events": [
                {
                    "summary": "Elina arrive au dortoir.",
                }
            ]
        },
        scenario,
    )

    assert messages == []


def test_generate_pending_messages_generic_trigger_requires_separation():
    world = build_world()
    world["character_locations"]["beau"] = "dormitory"
    scenario = {
        "message_triggers": [
            {
                "trigger": "beau_dormitory_checkin",
                "from": "beau",
                "to": "elina",
                "channel": "sms",
                "content": "Tout va bien ?",
                "keywords": [
                    "dortoir",
                ],
            }
        ]
    }

    messages = generate_pending_messages(
        world,
        build_characters(),
        {
            "events": [
                {
                    "summary": "Elina arrive au dortoir.",
                }
            ]
        },
        scenario,
    )

    assert messages == []


def test_generate_pending_messages_generic_trigger_does_not_duplicate():
    world = build_world()
    world["messages"] = [
        {
            "from": "beau",
            "to": "elina",
            "trigger": "beau_dormitory_checkin",
        }
    ]
    scenario = {
        "message_triggers": [
            {
                "trigger": "beau_dormitory_checkin",
                "from": "beau",
                "to": "elina",
                "channel": "sms",
                "content": "Tout va bien ?",
                "keywords": [
                    "dortoir",
                ],
            }
        ]
    }

    messages = generate_pending_messages(
        world,
        build_characters(),
        {
            "events": [
                {
                    "summary": "Elina arrive au dortoir.",
                }
            ]
        },
        scenario,
    )

    assert messages == []


def test_generate_pending_messages_ignores_invalid_generic_trigger():
    scenario = {
        "message_triggers": [
            {
                "trigger": "beau_dormitory_checkin",
                "from": "beau",
                "to": "elina",
                "channel": "sms",
                "content": "Tout va bien ?",
                "keywords": [],
            }
        ]
    }

    messages = generate_pending_messages(
        build_world(),
        build_characters(),
        {
            "events": [
                {
                    "summary": "Elina arrive au dortoir.",
                }
            ]
        },
        scenario,
    )

    assert messages == []


def test_generate_pending_messages_requires_dean_knows_phone():
    messages = generate_pending_messages(
        build_world(),
        build_characters(dean_knows_elina_phone=False),
        build_scene_result_with_skating_context(),
    )

    assert messages == []


def test_generate_pending_messages_requires_different_locations():
    world = build_world()
    world["character_locations"]["dean"] = "dormitory"

    messages = generate_pending_messages(
        world,
        build_characters(),
        build_scene_result_with_skating_context(),
    )

    assert messages == []


def test_generate_pending_messages_requires_skating_context():
    messages = generate_pending_messages(
        build_world(),
        build_characters(),
        {
            "memory_updates": [
                {
                    "owner": "dean",
                    "content": "Dean noticed Elina leaving.",
                }
            ],
            "events": [],
            "dialogues": [],
        },
    )

    assert messages == []


def test_generate_pending_messages_uses_player_input_context():
    messages = generate_pending_messages(
        build_world(),
        build_characters(),
        {
            "narration": [
                "Elina entre dans le dortoir.",
            ],
            "events": [],
            "memory_updates": [],
            "dialogues": [],
        },
        None,
        {
            "player_input": (
                "Je te donne mon numero pour la patinoire, "
                "puis je pars au dortoir."
            )
        },
    )

    assert len(messages) == 1
    assert messages[0]["trigger"] == "skating_lesson_followup"


def test_generate_pending_messages_uses_scene_history_context():
    messages = generate_pending_messages(
        build_world(),
        build_characters(),
        {
            "narration": [
                "Elina arrive au dortoir.",
            ],
            "events": [],
            "memory_updates": [],
            "dialogues": [],
        },
        None,
        {
            "player_input": "Je pars au dortoir.",
            "scene_history": (
                "Dean a recu le numero d'Elina pour organiser "
                "la seance a la patinoire."
            ),
        },
    )

    assert len(messages) == 1
    assert messages[0]["trigger"] == "skating_lesson_followup"


def test_generate_pending_messages_does_not_duplicate_trigger():
    world = build_world()
    world["messages"] = [
        {
            "from": "dean",
            "to": "elina",
            "trigger": "skating_lesson_followup",
        }
    ]

    messages = generate_pending_messages(
        world,
        build_characters(),
        build_scene_result_with_skating_context(),
    )

    assert messages == []


def test_append_pending_messages_adds_messages_to_world():
    world = build_world()
    messages = generate_pending_messages(
        world,
        build_characters(),
        build_scene_result_with_skating_context(),
    )

    world = append_pending_messages(
        world,
        messages,
    )

    assert world["messages"] == messages


def test_append_pending_messages_updates_story_arc_state_with_scenario():
    world = build_world()
    messages = [
        {
            "from": "dean",
            "to": "elina",
            "channel": "sms",
            "content": "Demain matin. Patinoire. 7h.",
            "trigger": "skating_lesson_followup",
        }
    ]
    scenario = {
        "story_arcs": [
            {
                "id": "dean_elina_slow_burn",
                "status": "active",
                "phase": "initial_tension",
                "participants": [
                    "dean",
                    "elina",
                ],
            }
        ]
    }

    world = append_pending_messages(
        world,
        messages,
        scenario,
    )

    assert world["arc_state"]["dean_elina_slow_burn"]["signals"] == [
        "text_followup_seen",
        "playful_challenge_seen",
    ]


def test_get_player_messages_returns_only_player_inbox():
    world = build_world()
    world["messages"] = [
        {
            "from": "dean",
            "to": "elina",
            "content": "A demain.",
        },
        {
            "from": "elina",
            "to": "dean",
            "content": "Vu.",
        },
        "invalid",
    ]

    messages = get_player_messages(world)

    assert messages == [
        {
            "from": "dean",
            "to": "elina",
            "content": "A demain.",
        }
    ]


def test_get_player_messages_ignores_invalid_messages_field():
    world = build_world()
    world["messages"] = {}

    assert get_player_messages(world) == []


def test_mark_player_messages_read_updates_only_player_messages():
    world = build_world()
    world["messages"] = [
        {
            "from": "dean",
            "to": "elina",
            "status": "unread",
        },
        {
            "from": "elina",
            "to": "dean",
            "status": "unread",
        },
        {
            "from": "beau",
            "to": "elina",
            "status": "read",
        },
    ]

    updated_world = mark_player_messages_read(world)

    assert updated_world["messages"] == [
        {
            "from": "dean",
            "to": "elina",
            "status": "read",
        },
        {
            "from": "elina",
            "to": "dean",
            "status": "unread",
        },
        {
            "from": "beau",
            "to": "elina",
            "status": "read",
        },
    ]


def test_mark_player_messages_read_ignores_invalid_messages_field():
    world = build_world()
    world["messages"] = {}

    assert mark_player_messages_read(world) == world


def test_parse_sms_reply_command_from_reply():
    assert parse_sms_reply_command("reply dean: Ok pour 7h.") == {
        "to": "dean",
        "content": "Ok pour 7h.",
    }


def test_parse_sms_reply_command_from_sms_alias():
    assert parse_sms_reply_command("sms dean: J'arrive.") == {
        "to": "dean",
        "content": "J'arrive.",
    }


def test_parse_sms_reply_command_ignores_normal_input():
    assert parse_sms_reply_command("Je vais au dortoir.") is None
    assert parse_sms_reply_command("reply dean") is None
    assert parse_sms_reply_command(None) is None


def test_apply_player_sms_reply_allows_reply_to_existing_sms():
    world = build_world()
    world["messages"] = [
        {
            "from": "dean",
            "to": "elina",
            "channel": "sms",
            "content": "Patinoire demain.",
            "status": "unread",
            "trigger": "skating_lesson_followup",
        }
    ]
    characters = build_characters()

    world, result = apply_player_sms_reply(
        world,
        characters,
        {
            "to": "dean",
            "content": "Ok pour 7h.",
        },
    )

    assert result["sent"] is True
    assert world["messages"][-2] == {
        "id": "elina-dean-player_reply-d1-1030",
        "from": "elina",
        "to": "dean",
        "channel": "sms",
        "content": "Ok pour 7h.",
        "sent_at_day": 1,
        "sent_at_time": "10:30",
        "status": "sent",
        "trigger": "player_reply",
    }
    assert world["messages"][-1] == {
        "id": "dean-elina-skating_lesson_reply_confirmation-d1-1030",
        "from": "dean",
        "to": "elina",
        "channel": "sms",
        "content": (
            "Parfait. Mets quelque chose de chaud. "
            "Je promets de ne pas rire avant ta deuxieme chute."
        ),
        "sent_at_day": 1,
        "sent_at_time": "10:30",
        "status": "unread",
        "trigger": "skating_lesson_reply_confirmation",
    }
    assert result["npc_replies"] == [
        world["messages"][-1],
    ]
    assert world["event_log"][0] == {
        "day": 1,
        "date": "2026-09-01",
        "time": "10:30",
        "type": "text_message",
        "participants": [
            "elina",
            "dean",
        ],
        "summary": "elina texts dean: Ok pour 7h.",
    }
    assert world["event_log"][1] == {
        "day": 1,
        "date": "2026-09-01",
        "time": "10:30",
        "type": "planned_meeting",
        "participants": [
            "dean",
            "elina",
        ],
        "summary": (
            "Dean and Elina agreed by SMS to meet at the rink "
            "tomorrow at 7."
        ),
        "trigger": "skating_lesson_planned_meeting",
    }
    assert world["planned_events"] == [
        {
            "id": "planned_skating_lesson_dean_elina_day2_0700",
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
                "Dean and Elina agreed to meet at the rink for a "
                "skating lesson."
            ),
            "source": "sms",
        }
    ]
    assert characters["dean"]["memories"] == [
        {
            "owner": "dean",
            "type": "event",
            "content": (
                "elina texted: Ok pour 7h. Reply sent: "
                "Parfait. Mets quelque chose de chaud. Je promets de ne "
                "pas rire avant ta deuxieme chute."
            ),
            "importance": 4,
            "age": 0,
            "tags": [
                "sms",
                "elina",
            ],
        }
    ]
    assert world["active_scene"] == {
        "location": "dormitory",
        "participants": [
            "elina",
        ],
    }
    assert world["character_locations"] == {
        "beau": "campus",
        "dean": "campus",
        "elina": "dormitory",
    }


def test_apply_player_sms_reply_can_use_llm_for_npc_reply_content():
    world = build_world()
    world["messages"] = [
        {
            "from": "dean",
            "to": "elina",
            "channel": "sms",
            "content": "Demain matin. Patinoire. 7h.",
            "status": "unread",
            "trigger": "skating_lesson_followup",
        }
    ]
    characters = build_characters()

    def fake_generate_text(prompt):
        assert "SENDER CONTEXT" in prompt
        assert "PLAYER SMS" in prompt
        return '"7h. Je prends le cafe, tu prends ton courage."'

    world, result = apply_player_sms_reply(
        world,
        characters,
        {
            "to": "dean",
            "content": "Ok pour 7h.",
        },
        fake_generate_text,
    )

    assert result["sent"] is True
    assert world["messages"][-1]["content"] == (
        "7h. Je prends le cafe, tu prends ton courage."
    )
    assert world["messages"][-1]["trigger"] == (
        "skating_lesson_reply_confirmation"
    )
    assert world["event_log"][1]["type"] == "planned_meeting"


def test_build_npc_sms_reply_content_falls_back_when_llm_fails():
    def failing_generate_text(prompt):
        raise RuntimeError("api down")

    content = build_npc_sms_reply_content(
        build_world(),
        build_characters(),
        {
            "from": "elina",
            "to": "dean",
            "content": "Ok pour 7h.",
        },
        "dean",
        "elina",
        "Fallback.",
        failing_generate_text,
    )

    assert content == "Fallback."


def test_sanitize_llm_sms_content_removes_labels_quotes_and_fences():
    content = sanitize_llm_sms_content(
        '```text\nDean: "7h. Essaie de ne pas arriver en retard."\n```',
        "Fallback.",
    )

    assert content == "7h. Essaie de ne pas arriver en retard."


def test_sanitize_llm_sms_content_falls_back_for_empty_text():
    assert sanitize_llm_sms_content("   ", "Fallback.") == "Fallback."


def test_apply_player_sms_reply_allows_known_phone_number():
    world = build_world()
    characters = build_characters()
    characters["elina"]["contacts"] = {
        "dean": {
            "phone_number_known": True,
        }
    }

    world, result = apply_player_sms_reply(
        world,
        characters,
        {
            "to": "dean",
            "content": "Je confirme.",
        },
    )

    assert result["sent"] is True
    assert world["messages"][-1]["content"] == "Je confirme."


def test_apply_player_sms_reply_does_not_auto_reply_without_skating_followup():
    world = build_world()
    characters = build_characters()
    characters["elina"]["contacts"] = {
        "dean": {
            "phone_number_known": True,
        }
    }

    world, result = apply_player_sms_reply(
        world,
        characters,
        {
            "to": "dean",
            "content": "Je confirme.",
        },
    )

    assert result["sent"] is True
    assert result["npc_replies"] == []
    assert len(world["messages"]) == 1


def test_apply_player_sms_reply_can_generate_generic_llm_reply():
    world = build_world()
    characters = build_characters()
    characters["elina"]["contacts"] = {
        "beau": {
            "phone_number_known": True,
        }
    }

    def fake_generate_text(prompt):
        assert "The sender is Beau Maxwell (beau)." in prompt
        assert "protective but not humorless" in prompt
        return "Je te laisse respirer, mais envoie-moi juste un signe quand tu es installee."

    world, result = apply_player_sms_reply(
        world,
        characters,
        {
            "to": "beau",
            "content": "Je suis au dortoir. Pas besoin de monter me surveiller.",
        },
        fake_generate_text,
    )

    assert result["sent"] is True
    assert result["npc_replies"] == [
        world["messages"][-1],
    ]
    assert world["messages"][-1]["from"] == "beau"
    assert world["messages"][-1]["to"] == "elina"
    assert world["messages"][-1]["content"] == (
        "Je te laisse respirer, mais envoie-moi juste un signe "
        "quand tu es installee."
    )
    assert world["messages"][-1]["trigger"].startswith(
        "generic_sms_reply_beau_to_elina"
    )
    assert characters["beau"]["memories"] == [
        {
            "owner": "beau",
            "type": "event",
            "content": (
                "elina texted: Je suis au dortoir. Pas besoin de monter "
                "me surveiller. Reply sent: Je te laisse respirer, mais "
                "envoie-moi juste un signe quand tu es installee."
            ),
            "importance": 4,
            "age": 0,
            "tags": [
                "sms",
                "elina",
            ],
        }
    ]


def test_apply_player_sms_reply_does_not_generate_generic_reply_without_llm():
    world = build_world()
    characters = build_characters()
    characters["elina"]["contacts"] = {
        "beau": {
            "phone_number_known": True,
        }
    }

    world, result = apply_player_sms_reply(
        world,
        characters,
        {
            "to": "beau",
            "content": "Je suis au dortoir. Pas besoin de monter me surveiller.",
        },
    )

    assert result["sent"] is True
    assert result["npc_replies"] == []
    assert len(world["messages"]) == 1


def test_apply_player_sms_reply_does_not_generate_generic_reply_for_low_signal_sms():
    world = build_world()
    characters = build_characters()
    characters["elina"]["contacts"] = {
        "beau": {
            "phone_number_known": True,
        }
    }

    def fake_generate_text(prompt):
        return "Je reponds."

    world, result = apply_player_sms_reply(
        world,
        characters,
        {
            "to": "beau",
            "content": "ok",
        },
        fake_generate_text,
    )

    assert result["sent"] is True
    assert result["npc_replies"] == []
    assert len(world["messages"]) == 1


def test_apply_player_sms_reply_does_not_duplicate_npc_reply():
    world = build_world()
    world["messages"] = [
        {
            "from": "dean",
            "to": "elina",
            "channel": "sms",
            "trigger": "skating_lesson_followup",
        },
        {
            "from": "dean",
            "to": "elina",
            "channel": "sms",
            "trigger": "skating_lesson_reply_confirmation",
        },
    ]
    characters = build_characters()

    world, result = apply_player_sms_reply(
        world,
        characters,
        {
            "to": "dean",
            "content": "Ok pour 7h.",
        },
    )

    assert result["sent"] is True
    assert result["npc_replies"] == []
    assert len(world["messages"]) == 3


def test_apply_player_sms_reply_does_not_duplicate_planned_meeting_event():
    world = build_world()
    world["messages"] = [
        {
            "from": "dean",
            "to": "elina",
            "channel": "sms",
            "trigger": "skating_lesson_followup",
        }
    ]
    world["event_log"] = [
        {
            "type": "planned_meeting",
            "trigger": "skating_lesson_planned_meeting",
        }
    ]
    characters = build_characters()

    world, result = apply_player_sms_reply(
        world,
        characters,
        {
            "to": "dean",
            "content": "Ok pour 7h.",
        },
    )

    planned_meetings = [
        event
        for event in world["event_log"]
        if event.get("type") == "planned_meeting"
    ]

    assert result["sent"] is True
    assert len(planned_meetings) == 1
    assert world["planned_events"][0]["trigger"] == (
        "skating_lesson_planned_meeting"
    )


def test_apply_player_sms_reply_does_not_duplicate_planned_event():
    world = build_world()
    world["messages"] = [
        {
            "from": "dean",
            "to": "elina",
            "channel": "sms",
            "trigger": "skating_lesson_followup",
        }
    ]
    world["planned_events"] = [
        {
            "id": "planned_skating_lesson_dean_elina_day2_0700",
            "type": "planned_event",
        }
    ]
    characters = build_characters()

    world, result = apply_player_sms_reply(
        world,
        characters,
        {
            "to": "dean",
            "content": "Ok pour 7h.",
        },
    )

    assert result["sent"] is True
    assert len(world["planned_events"]) == 1


def test_apply_player_sms_reply_does_not_auto_reply_to_unrelated_content():
    world = build_world()
    world["messages"] = [
        {
            "from": "dean",
            "to": "elina",
            "channel": "sms",
            "trigger": "skating_lesson_followup",
        }
    ]
    characters = build_characters()

    world, result = apply_player_sms_reply(
        world,
        characters,
        {
            "to": "dean",
            "content": "On verra.",
        },
    )

    assert result["sent"] is True
    assert result["npc_replies"] == []


def test_apply_player_sms_reply_rejects_without_sms_access():
    world = build_world()
    characters = build_characters()

    world, result = apply_player_sms_reply(
        world,
        characters,
        {
            "to": "dean",
            "content": "Ok.",
        },
    )

    assert result == {
        "sent": False,
        "reason": "cannot_text_recipient",
    }
    assert world["messages"] == []
    assert world["event_log"] == []


def test_apply_player_sms_reply_rejects_unknown_recipient():
    world = build_world()
    characters = build_characters()

    world, result = apply_player_sms_reply(
        world,
        characters,
        {
            "to": "unknown",
            "content": "Ok.",
        },
    )

    assert result["sent"] is False
    assert world["messages"] == []


def test_message_generated_after_number_exchange_and_player_departure():
    world = build_world()
    world["active_scene"] = {
        "location": "campus",
        "participants": [
            "dean",
            "elina",
        ],
    }
    world["character_locations"] = {
        "dean": "campus",
        "elina": "campus",
    }

    characters = build_characters(
        dean_knows_elina_phone=False,
    )

    scene_result = {
        "scene": {
            "location": "campus",
            "time": "10:30",
            "participants": [
                "dean",
                "elina",
            ],
        },
        "contact_updates": [
            {
                "source": "dean",
                "target": "elina",
                "changes": {
                    "phone_number_known": True,
                },
            }
        ],
        "memory_updates": [
            {
                "owner": "dean",
                "content": "Dean can text Elina about the patinoire lesson.",
            }
        ],
        "events": [
            {
                "type": "skating_challenge",
                "participants": [
                    "dean",
                    "elina",
                ],
                "summary": "Dean gets Elina's number for a skating lesson.",
            }
        ],
        "dialogues": [],
        "world_updates": {
            "time_advance_minutes": 0,
            "new_location": "dormitory",
            "character_movements": {},
        },
    }

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
    )
    world = append_pending_messages(
        world,
        messages,
    )

    assert world["character_locations"]["elina"] == "dormitory"
    assert world["character_locations"]["dean"] == "campus"
    assert world["messages"][0]["from"] == "dean"
    assert world["messages"][0]["to"] == "elina"
    assert world["messages"][0]["trigger"] == "skating_lesson_followup"
