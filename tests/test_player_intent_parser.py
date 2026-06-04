from backend.app.core.player_intent_parser import (
    apply_player_intent_hints,
    build_player_intent_hints,
    detect_player_leaves_npcs_behind,
    detect_player_movement,
)


def build_world():
    return {
        "player_character": "elina",
        "locations": [
            {
                "id": "campus",
                "name": "Briar University Campus",
            },
            {
                "id": "dormitory",
                "name": "Briar Dormitory",
            },
            {
                "id": "hockey_house",
                "name": "Hockey House",
            },
            {
                "id": "library",
                "name": "University Library",
            },
            {
                "id": "ice_rink",
                "name": "Briar Ice Rink",
            },
            {
                "id": "malones",
                "name": "Malone's",
            },
        ]
    }


def test_detect_player_movement_to_dormitory():
    assert (
        detect_player_movement(
            "je vais au dortoir",
            build_world(),
        )
        == "dormitory"
    )


def test_detect_player_movement_toward_my_dormitory():
    assert (
        detect_player_movement(
            "j'avance vers mon dortoir",
            build_world(),
        )
        == "dormitory"
    )


def test_detect_player_movement_to_residence():
    assert (
        detect_player_movement(
            "je rentre a la residence",
            build_world(),
        )
        == "dormitory"
    )


def test_detect_player_movement_to_library():
    assert (
        detect_player_movement(
            "je vais a la bibliotheque",
            build_world(),
        )
        == "library"
    )


def test_detect_player_movement_to_hockey_house():
    assert (
        detect_player_movement(
            "je file a la hockey house",
            build_world(),
        )
        == "hockey_house"
    )


def test_detect_player_movement_to_campus():
    assert (
        detect_player_movement(
            "je retourne sur le campus",
            build_world(),
        )
        == "campus"
    )


def test_detect_player_movement_to_ice_rink():
    assert (
        detect_player_movement(
            "je vais a la patinoire",
            build_world(),
        )
        == "ice_rink"
    )


def test_detect_player_movement_to_malones():
    assert (
        detect_player_movement(
            "je file au Malone's",
            build_world(),
        )
        == "malones"
    )


def test_detect_player_movement_ignores_ambiguous_departure():
    assert (
        detect_player_movement(
            "je m'eloigne",
            build_world(),
        )
        is None
    )


def test_detect_player_movement_ignores_none():
    assert detect_player_movement(None, build_world()) is None


def test_detect_player_movement_ignores_empty_input():
    assert detect_player_movement("", build_world()) is None


def test_build_player_intent_hints_returns_detected_movement():
    assert build_player_intent_hints(
        "je vais au dortoir",
        build_world(),
    ) == {
        "detected_movement": "dormitory",
        "leaves_npcs_behind": False,
    }


def test_build_player_intent_hints_detects_leaving_npcs_behind():
    assert build_player_intent_hints(
        '"Salut les nazes" *j avance vers mon dortoir les laissant la*',
        build_world(),
    ) == {
        "detected_movement": "dormitory",
        "leaves_npcs_behind": True,
    }


def test_detect_player_leaves_npcs_behind_from_leaving_them_there():
    assert detect_player_leaves_npcs_behind("les laissant la") is True


def test_detect_player_leaves_npcs_behind_from_i_leave_them_there():
    assert detect_player_leaves_npcs_behind("je les laisse la") is True


def test_detect_player_leaves_npcs_behind_from_i_ditch_them_there():
    assert detect_player_leaves_npcs_behind("je les plante la") is True


def test_detect_player_leaves_npcs_behind_from_without_them():
    assert detect_player_leaves_npcs_behind("je pars sans eux") is True


def test_detect_player_leaves_npcs_behind_from_alone():
    assert detect_player_leaves_npcs_behind("je m'en vais seule") is True


def test_detect_player_leaves_npcs_behind_from_alone_to_dormitory():
    assert (
        detect_player_leaves_npcs_behind("je vais seule au dortoir")
        is True
    )


def test_detect_player_leaves_npcs_behind_from_without_waiting():
    assert detect_player_leaves_npcs_behind("sans les attendre") is True


def test_detect_player_leaves_npcs_behind_from_abandoning_them():
    assert detect_player_leaves_npcs_behind("je les abandonne la") is True


def test_detect_player_leaves_npcs_behind_ignores_simple_move():
    assert detect_player_leaves_npcs_behind("je vais au dortoir") is False


def test_detect_player_leaves_npcs_behind_ignores_simple_departure():
    assert detect_player_leaves_npcs_behind("je pars") is False


def test_detect_player_leaves_npcs_behind_ignores_none():
    assert detect_player_leaves_npcs_behind(None) is False


def test_apply_player_intent_hints_fills_empty_new_location():
    scene_result = {
        "world_updates": {
            "new_location": "",
            "character_movements": {},
        }
    }

    updated = apply_player_intent_hints(
        scene_result,
        build_world(),
        {
            "detected_movement": "dormitory",
        },
    )

    assert updated["world_updates"]["new_location"] == "dormitory"


def test_apply_player_intent_hints_keeps_existing_same_location():
    scene_result = {
        "world_updates": {
            "new_location": "dormitory",
            "character_movements": {},
        }
    }

    updated = apply_player_intent_hints(
        scene_result,
        build_world(),
        {
            "detected_movement": "dormitory",
        },
    )

    assert updated["world_updates"]["new_location"] == "dormitory"


def test_apply_player_intent_hints_does_not_override_other_valid_location():
    scene_result = {
        "world_updates": {
            "new_location": "library",
            "character_movements": {},
        }
    }

    updated = apply_player_intent_hints(
        scene_result,
        build_world(),
        {
            "detected_movement": "dormitory",
        },
    )

    assert updated["world_updates"]["new_location"] == "library"


def test_apply_player_intent_hints_removes_npc_move_to_player_destination():
    scene_result = {
        "dialogues": [
            {
                "speaker": "dean",
                "text": "Une reaction courte.",
            },
            {
                "speaker": "beau",
                "text": "Une deuxieme reaction.",
            },
        ],
        "world_updates": {
            "new_location": "",
            "character_movements": {
                "beau": "dormitory",
                "dean": "campus",
            },
        }
    }

    updated = apply_player_intent_hints(
        scene_result,
        build_world(),
        {
            "detected_movement": "dormitory",
            "leaves_npcs_behind": True,
        },
    )

    assert updated["world_updates"]["new_location"] == "dormitory"
    assert updated["world_updates"]["character_movements"] == {
        "dean": "campus",
    }
    assert updated["dialogues"] == [
        {
            "speaker": "dean",
            "text": "Une reaction courte.",
        }
    ]


def test_apply_player_intent_hints_keeps_npc_move_to_other_location():
    scene_result = {
        "world_updates": {
            "new_location": "",
            "character_movements": {
                "beau": "campus",
            },
        }
    }

    updated = apply_player_intent_hints(
        scene_result,
        build_world(),
        {
            "detected_movement": "dormitory",
            "leaves_npcs_behind": True,
        },
    )

    assert updated["world_updates"]["character_movements"] == {
        "beau": "campus",
    }


def test_apply_player_intent_hints_keeps_npc_moves_without_leave_signal():
    scene_result = {
        "world_updates": {
            "new_location": "",
            "character_movements": {
                "beau": "dormitory",
            },
        }
    }

    updated = apply_player_intent_hints(
        scene_result,
        build_world(),
        {
            "detected_movement": "dormitory",
            "leaves_npcs_behind": False,
        },
    )

    assert updated["world_updates"]["character_movements"] == {
        "beau": "dormitory",
    }
