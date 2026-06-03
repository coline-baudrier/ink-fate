from backend.app.core.contact_engine import (
    apply_contact_updates,
    build_contact_context,
)


def build_characters():
    return {
        "dean": {
            "contacts": {
                "elina": {
                    "phone_number_known": False,
                    "phone_numbers_exchanged": False,
                    "instagram_connected": False,
                }
            }
        },
        "elina": {
            "contacts": {
                "dean": {
                    "phone_number_known": False,
                    "phone_numbers_exchanged": False,
                    "instagram_connected": False,
                }
            }
        },
    }


def test_apply_contact_updates_adds_directional_phone_number():
    characters = build_characters()
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

    updated_characters = apply_contact_updates(
        scene_result,
        characters,
    )

    assert (
        updated_characters["elina"]["contacts"]["dean"]["phone_number_known"]
        is True
    )
    assert (
        updated_characters["dean"]["contacts"]["elina"]["phone_number_known"]
        is False
    )


def test_apply_contact_updates_mirrors_phone_number_exchange():
    characters = build_characters()
    scene_result = {
        "contact_updates": [
            {
                "source": "elina",
                "target": "dean",
                "changes": {
                    "phone_numbers_exchanged": True,
                },
            }
        ]
    }

    updated_characters = apply_contact_updates(
        scene_result,
        characters,
    )

    assert (
        updated_characters["elina"]["contacts"]["dean"]["phone_number_known"]
        is True
    )
    assert (
        updated_characters["dean"]["contacts"]["elina"]["phone_number_known"]
        is True
    )
    assert (
        updated_characters["elina"]["contacts"]["dean"][
            "phone_numbers_exchanged"
        ]
        is True
    )
    assert (
        updated_characters["dean"]["contacts"]["elina"][
            "phone_numbers_exchanged"
        ]
        is True
    )


def test_apply_contact_updates_mirrors_instagram_connection():
    characters = build_characters()
    scene_result = {
        "contact_updates": [
            {
                "source": "dean",
                "target": "elina",
                "changes": {
                    "instagram_connected": True,
                },
            }
        ]
    }

    updated_characters = apply_contact_updates(
        scene_result,
        characters,
    )

    assert (
        updated_characters["dean"]["contacts"]["elina"][
            "instagram_connected"
        ]
        is True
    )
    assert (
        updated_characters["elina"]["contacts"]["dean"][
            "instagram_connected"
        ]
        is True
    )


def test_build_contact_context_shows_derived_access():
    scene_context = {
        "participants": [
            {
                "id": "elina",
                "contacts": {
                    "dean": {
                        "phone_number_known": True,
                        "phone_numbers_exchanged": False,
                        "instagram_connected": False,
                    }
                },
            }
        ]
    }

    context = build_contact_context(scene_context)

    assert "elina -> dean" in context
    assert "phone known: yes" in context
    assert "numbers exchanged: no" in context
    assert "can text/call: yes" in context
    assert "can DM: no" in context
