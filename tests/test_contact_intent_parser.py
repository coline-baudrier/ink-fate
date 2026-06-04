from backend.app.core.contact_intent_parser import (
    apply_contact_intent_hints,
    build_contact_intent_hints,
    detect_phone_number_recipient,
)


def build_world():
    return {
        "player_character": "elina",
        "characters": [
            "elina",
            "dean",
            "beau",
        ],
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
                "id": "dean",
                "identity": {
                    "first_name": "Dean",
                    "last_name": "Di Laurentis",
                },
            },
            {
                "id": "beau",
                "identity": {
                    "first_name": "Beau",
                },
            },
        ]
    }


def test_detect_phone_number_recipient_from_explicit_name():
    assert (
        detect_phone_number_recipient(
            "Dean, je te donne mon numero.",
            build_world(),
            build_scene_context(),
        )
        == "dean"
    )


def test_detect_phone_number_recipient_defaults_to_dean_for_direct_cue():
    assert (
        detect_phone_number_recipient(
            "Je te donne mon numero. Tu me dois la patinoire.",
            build_world(),
            build_scene_context(),
        )
        == "dean"
    )


def test_detect_phone_number_recipient_ignores_empty_input():
    assert (
        detect_phone_number_recipient(
            "",
            build_world(),
            build_scene_context(),
        )
        is None
    )


def test_detect_phone_number_recipient_ignores_unrelated_input():
    assert (
        detect_phone_number_recipient(
            "Je vais au dortoir.",
            build_world(),
            build_scene_context(),
        )
        is None
    )


def test_build_contact_intent_hints_detects_recipient():
    assert build_contact_intent_hints(
        "Je te donne mon numero.",
        build_world(),
        build_scene_context(),
    ) == {
        "phone_number_given_to": "dean",
    }


def test_apply_contact_intent_hints_adds_correct_directional_update():
    scene_result = {
        "contact_updates": [
            {
                "source": "elina",
                "target": "dean",
                "changes": {
                    "phone_number_known": True,
                },
            }
        ]
    }

    updated = apply_contact_intent_hints(
        scene_result,
        build_world(),
        {
            "phone_number_given_to": "dean",
        },
    )

    assert {
        "source": "dean",
        "target": "elina",
        "changes": {
            "phone_number_known": True,
        },
    } in updated["contact_updates"]


def test_apply_contact_intent_hints_does_not_duplicate_existing_update():
    scene_result = {
        "contact_updates": [
            {
                "source": "dean",
                "target": "elina",
                "changes": {
                    "phone_number_known": True,
                },
            }
        ]
    }

    updated = apply_contact_intent_hints(
        scene_result,
        build_world(),
        {
            "phone_number_given_to": "dean",
        },
    )

    assert len(updated["contact_updates"]) == 1
