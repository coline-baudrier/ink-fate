from backend.app.core.scene_validator import (
    remove_invalid_actions,
    remove_invalid_contact_updates,
    remove_invalid_events,
    remove_invalid_memory_updates,
    remove_invalid_relationship_updates,
    validate_scene,
    validate_world_updates,
)
from backend.app.core.scene_validator import clamp_relationship_updates
from backend.app.core.scene_validator import validate_scene_pacing


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
            {"id": "dormitory", "name": "Dormitory"},
            {"id": "library", "name": "Library"},
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
            ],
        },
    }


def test_validate_scene_keeps_valid_scene():
    world = build_world()

    scene_result = {
        "scene": {
            "location": "dormitory",
            "time": "11:30",
            "participants": [
                "elina",
                "dean",
            ],
        }
    }

    validated = validate_scene(
        scene_result,
        world,
    )

    assert validated["scene"] == {
        "location": "dormitory",
        "time": "11:30",
        "participants": [
            "elina",
            "dean",
        ],
    }


def test_validate_scene_replaces_invalid_location_and_time():
    world = build_world()

    scene_result = {
        "scene": {
            "location": "moon",
            "time": "99:99",
            "participants": [
                "elina",
            ],
        }
    }

    validated = validate_scene(
        scene_result,
        world,
    )

    assert validated["scene"]["location"] == "campus"
    assert validated["scene"]["time"] == "10:15"


def test_validate_scene_removes_invalid_participants():
    world = build_world()

    scene_result = {
        "scene": {
            "location": "campus",
            "time": "10:20",
            "participants": [
                "elina",
                "unknown",
            ],
        }
    }

    validated = validate_scene(
        scene_result,
        world,
    )

    assert validated["scene"]["participants"] == ["elina"]


def test_validate_scene_uses_active_scene_when_scene_is_missing():
    world = build_world()

    validated = validate_scene(
        {},
        world,
    )

    assert validated["scene"] == {
        "location": "campus",
        "time": "10:15",
        "participants": [
            "elina",
            "beau",
        ],
    }


def test_validate_scene_handles_invalid_secondary_types():
    world = build_world()

    scene_result = {
        "scene": {
            "location": [
                "campus",
            ],
            "time": True,
            "participants": [
                "elina",
                [
                    "dean",
                ],
            ],
        }
    }

    validated = validate_scene(
        scene_result,
        world,
    )

    assert validated["scene"] == {
        "location": "campus",
        "time": "10:15",
        "participants": [
            "elina",
        ],
    }


def test_remove_invalid_actions_cleans_secondary_fields():
    scene_result = {
        "actions": [
            {
                "character": " dean ",
                "type": " tease ",
                "target": " elina ",
            },
            {
                "character": "dean",
                "type": "",
                "target": "elina",
            },
            {
                "character": "beau",
                "type": "follow",
                "target": "unknown",
            },
            {
                "character": "unknown",
                "type": "wave",
                "target": "",
            },
        ]
    }

    validated = remove_invalid_actions(
        scene_result,
        [
            "elina",
            "beau",
            "dean",
        ],
    )

    assert validated["actions"] == [
        {
            "character": "dean",
            "type": "tease",
            "target": "elina",
        }
    ]


def test_remove_invalid_events_cleans_type_summary_and_participants():
    scene_result = {
        "events": [
            {
                "type": " arrival ",
                "participants": [
                    " elina ",
                    "unknown",
                ],
                "summary": " Elina arrives. ",
            },
            {
                "type": "",
                "participants": [
                    "dean",
                ],
            },
            {
                "type": "empty_participants",
                "participants": [
                    "unknown",
                ],
            },
        ]
    }

    validated = remove_invalid_events(
        scene_result,
        [
            "elina",
            "beau",
            "dean",
        ],
    )

    assert validated["events"] == [
        {
            "type": "arrival",
            "participants": [
                "elina",
            ],
            "summary": "Elina arrives.",
        }
    ]


def test_validate_world_updates_keeps_valid_new_location():
    world = build_world()

    scene_result = {
        "world_updates": {
            "new_location": "dormitory",
            "time_advance_minutes": 5,
            "character_movements": {},
        }
    }

    validated = validate_world_updates(
        scene_result,
        world,
    )

    assert validated["world_updates"]["new_location"] == "dormitory"


def test_validate_world_updates_removes_invalid_new_location():
    world = build_world()

    scene_result = {
        "world_updates": {
            "new_location": "moon",
            "time_advance_minutes": 5,
            "character_movements": {},
        }
    }

    validated = validate_world_updates(
        scene_result,
        world,
    )

    assert validated["world_updates"]["new_location"] == ""


def test_validate_world_updates_clamps_negative_time():
    world = build_world()

    scene_result = {
        "world_updates": {
            "new_location": "",
            "time_advance_minutes": -10,
            "character_movements": {},
        }
    }

    validated = validate_world_updates(
        scene_result,
        world,
    )

    assert validated["world_updates"]["time_advance_minutes"] == 0


def test_validate_world_updates_clamps_large_time():
    world = build_world()

    scene_result = {
        "world_updates": {
            "new_location": "",
            "time_advance_minutes": 999,
            "character_movements": {},
        }
    }

    validated = validate_world_updates(
        scene_result,
        world,
    )

    assert validated["world_updates"]["time_advance_minutes"] == 180


def test_validate_world_updates_cleans_character_movements():
    world = build_world()

    scene_result = {
        "world_updates": {
            "new_location": "",
            "time_advance_minutes": 5,
            "character_movements": {
                "beau": "dormitory",
                "unknown": "library",
                "dean": "moon",
            },
        }
    }

    validated = validate_world_updates(
        scene_result,
        world,
    )

    assert validated["world_updates"]["character_movements"] == {
        "beau": "dormitory",
    }


def test_validate_world_updates_removes_player_movement():
    world = build_world()

    scene_result = {
        "world_updates": {
            "new_location": "dormitory",
            "time_advance_minutes": 5,
            "character_movements": {
                "elina": "campus",
                "beau": "dormitory",
            },
        }
    }

    validated = validate_world_updates(
        scene_result,
        world,
    )

    assert validated["world_updates"]["character_movements"] == {
        "beau": "dormitory",
    }


def test_validate_world_updates_handles_invalid_secondary_types():
    world = build_world()

    scene_result = {
        "world_updates": {
            "new_location": [
                "dormitory",
            ],
            "time_advance_minutes": True,
            "character_movements": {
                123: "library",
                "beau": [
                    "dormitory",
                ],
                "dean": " library ",
            },
        }
    }

    validated = validate_world_updates(
        scene_result,
        world,
    )

    assert validated["world_updates"] == {
        "new_location": "",
        "time_advance_minutes": 0,
        "character_movements": {
            "dean": "library",
        },
    }


def test_remove_invalid_relationship_updates_cleans_ids():
    scene_result = {
        "relationship_updates": [
            {
                "source": " dean ",
                "target": " elina ",
                "changes": {},
            },
            {
                "source": "dean",
                "target": "unknown",
                "changes": {},
            },
        ]
    }

    validated = remove_invalid_relationship_updates(
        scene_result,
        [
            "elina",
            "beau",
            "dean",
        ],
    )

    assert validated["relationship_updates"] == [
        {
            "source": "dean",
            "target": "elina",
            "changes": {},
        }
    ]


def test_remove_invalid_contact_updates_cleans_ids_and_changes():
    scene_result = {
        "contact_updates": [
            {
                "source": " dean ",
                "target": " elina ",
                "changes": {
                    "phone_number_known": True,
                    "phone_numbers_exchanged": "yes",
                    "instagram_connected": False,
                    "unknown": True,
                },
            },
            {
                "source": "dean",
                "target": "unknown",
                "changes": {
                    "phone_number_known": True,
                },
            },
            "invalid",
        ]
    }

    validated = remove_invalid_contact_updates(
        scene_result,
        [
            "elina",
            "beau",
            "dean",
        ],
    )

    assert validated["contact_updates"] == [
        {
            "source": "dean",
            "target": "elina",
            "changes": {
                "phone_number_known": True,
                "instagram_connected": False,
            },
        }
    ]


def test_remove_invalid_memory_updates_cleans_secondary_fields():
    scene_result = {
        "memory_updates": [
            {
                "owner": " dean ",
                "type": "",
                "content": " Elina challenged him. ",
                "age": -5,
                "tags": [
                    " elina ",
                    "",
                    123,
                ],
            },
            {
                "owner": "dean",
                "content": "",
            },
            {
                "owner": "unknown",
                "content": "Invalid owner.",
            },
        ]
    }

    validated = remove_invalid_memory_updates(
        scene_result,
        [
            "elina",
            "beau",
            "dean",
        ],
    )

    assert validated["memory_updates"] == [
        {
            "owner": "dean",
            "type": "memory",
            "content": "Elina challenged him.",
            "age": 0,
            "tags": [
                "elina",
            ],
        }
    ]


def test_clamp_relationship_updates_limits_attraction():
    scene_result = {
        "relationship_updates": [
            {
                "source": "dean",
                "target": "elina",
                "changes": {
                    "attraction": 5,
                },
            }
        ]
    }

    validated = clamp_relationship_updates(scene_result)

    assert (
        validated["relationship_updates"][0]["changes"]["attraction"]
        == 2
    )


def test_clamp_relationship_updates_limits_attachment():
    scene_result = {
        "relationship_updates": [
            {
                "source": "dean",
                "target": "elina",
                "changes": {
                    "attachment": 5,
                },
            }
        ]
    }

    validated = clamp_relationship_updates(scene_result)

    assert (
        validated["relationship_updates"][0]["changes"]["attachment"]
        == 1
    )


def test_clamp_relationship_updates_limits_trust_negative():
    scene_result = {
        "relationship_updates": [
            {
                "source": "dean",
                "target": "elina",
                "changes": {
                    "trust": -5,
                },
            }
        ]
    }

    validated = clamp_relationship_updates(scene_result)

    assert (
        validated["relationship_updates"][0]["changes"]["trust"]
        == -1
    )


def test_clamp_relationship_updates_removes_invalid_change_values():
    scene_result = {
        "relationship_updates": [
            {
                "source": "dean",
                "target": "elina",
                "changes": {
                    "attraction": "high",
                    "respect": True,
                    "trust": 1,
                    123: 2,
                },
            },
            "invalid",
        ]
    }

    validated = clamp_relationship_updates(scene_result)

    assert validated["relationship_updates"] == [
        {
            "source": "dean",
            "target": "elina",
            "changes": {
                "trust": 1,
            },
        }
    ]


def test_validate_scene_pacing_limits_narration():
    scene_result = {
        "narration": [
            "Paragraph 1",
            "Paragraph 2",
            "Paragraph 3",
            "Paragraph 4",
        ],
        "dialogues": [],
    }

    validated = validate_scene_pacing(scene_result)

    assert validated["narration"] == [
        "Paragraph 1",
        "Paragraph 2",
        "Paragraph 3",
    ]


def test_validate_scene_pacing_limits_dialogues():
    scene_result = {
        "narration": [],
        "dialogues": [
            {"speaker": "dean", "text": "1"},
            {"speaker": "beau", "text": "2"},
            {"speaker": "dean", "text": "3"},
            {"speaker": "beau", "text": "4"},
        ],
    }

    validated = validate_scene_pacing(scene_result)

    assert validated["dialogues"] == [
        {"speaker": "dean", "text": "1"},
        {"speaker": "beau", "text": "2"},
        {"speaker": "dean", "text": "3"},
    ]


def test_validate_scene_pacing_removes_invalid_narration():
    scene_result = {
        "narration": [
            "  Paragraph 1  ",
            "",
            "   ",
            123,
            "Paragraph 2",
        ],
        "dialogues": [],
    }

    validated = validate_scene_pacing(scene_result)

    assert validated["narration"] == [
        "Paragraph 1",
        "Paragraph 2",
    ]


def test_validate_scene_pacing_removes_invalid_dialogues():
    scene_result = {
        "narration": [],
        "dialogues": [
            {"speaker": " dean ", "text": " Hello "},
            {"speaker": "", "text": "No speaker"},
            {"speaker": "beau", "text": ""},
            {"speaker": "dean"},
            "invalid",
            {"speaker": "beau", "text": "Valid"},
        ],
    }

    validated = validate_scene_pacing(scene_result)

    assert validated["dialogues"] == [
        {"speaker": "dean", "text": "Hello"},
        {"speaker": "beau", "text": "Valid"},
    ]


def test_validate_scene_pacing_handles_non_list_values():
    scene_result = {
        "narration": "not-a-list",
        "dialogues": "not-a-list",
    }

    validated = validate_scene_pacing(scene_result)

    assert validated["narration"] == []
    assert validated["dialogues"] == []
