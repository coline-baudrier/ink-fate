from backend.app.core.relationship_engine import (
    apply_relationship_updates,
    clamp_value,
)


def build_characters():
    return {
        "dean": {
            "relationships": {
                "elina": {
                    "attraction": 40,
                    "respect": 50,
                }
            }
        },
        "elina": {
            "relationships": {
                "dean": {
                    "attraction": 10,
                    "respect": 20,
                }
            }
        },
    }


def test_clamp_value_keeps_value_inside_bounds():
    assert clamp_value(50) == 50


def test_clamp_value_clamps_below_zero():
    assert clamp_value(-10) == 0


def test_clamp_value_clamps_above_hundred():
    assert clamp_value(150) == 100


def test_apply_relationship_updates_applies_valid_delta():
    characters = build_characters()

    scene_result = {
        "relationship_updates": [
            {
                "source": "dean",
                "target": "elina",
                "changes": {
                    "attraction": 3,
                    "respect": 2,
                },
            }
        ]
    }

    updated_characters = apply_relationship_updates(
        scene_result,
        characters,
    )

    relationship = updated_characters["dean"]["relationships"]["elina"]

    assert relationship["attraction"] == 43
    assert relationship["respect"] == 52


def test_apply_relationship_updates_clamps_to_zero():
    characters = build_characters()

    scene_result = {
        "relationship_updates": [
            {
                "source": "dean",
                "target": "elina",
                "changes": {
                    "respect": -999,
                },
            }
        ]
    }

    updated_characters = apply_relationship_updates(
        scene_result,
        characters,
    )

    assert (
        updated_characters["dean"]["relationships"]["elina"]["respect"]
        == 0
    )


def test_apply_relationship_updates_clamps_to_hundred():
    characters = build_characters()

    scene_result = {
        "relationship_updates": [
            {
                "source": "dean",
                "target": "elina",
                "changes": {
                    "attraction": 999,
                },
            }
        ]
    }

    updated_characters = apply_relationship_updates(
        scene_result,
        characters,
    )

    assert (
        updated_characters["dean"]["relationships"]["elina"]["attraction"]
        == 100
    )


def test_apply_relationship_updates_ignores_unknown_source():
    characters = build_characters()

    scene_result = {
        "relationship_updates": [
            {
                "source": "unknown",
                "target": "elina",
                "changes": {
                    "attraction": 10,
                },
            }
        ]
    }

    updated_characters = apply_relationship_updates(
        scene_result,
        characters,
    )

    assert (
        updated_characters["dean"]["relationships"]["elina"]["attraction"]
        == 40
    )


def test_apply_relationship_updates_ignores_unknown_target_relationship():
    characters = build_characters()

    scene_result = {
        "relationship_updates": [
            {
                "source": "dean",
                "target": "beau",
                "changes": {
                    "respect": 10,
                },
            }
        ]
    }

    updated_characters = apply_relationship_updates(
        scene_result,
        characters,
    )

    assert (
        updated_characters["dean"]["relationships"]["elina"]["respect"]
        == 50
    )