from backend.app.core.relationship_stages import (
    build_relationship_context,
    get_dimension_stage,
)


def test_get_dimension_stage_low():
    assert get_dimension_stage("attraction", 0) == "low attraction"
    assert get_dimension_stage("trust", 10) == "guarded"


def test_get_dimension_stage_emerging():
    assert get_dimension_stage("attraction", 11) == "emerging attraction"
    assert get_dimension_stage("trust", 35) == "emerging trust"


def test_get_dimension_stage_mid():
    assert get_dimension_stage("attraction", 36) == "attracted"
    assert get_dimension_stage("respect", 65) == "respectful"


def test_get_dimension_stage_strong():
    assert get_dimension_stage("attraction", 66) == "strong attraction"
    assert get_dimension_stage("trust", 85) == "strong trust"


def test_get_dimension_stage_high():
    assert get_dimension_stage("attraction", 86) == "strong attraction"
    assert get_dimension_stage("trust", 100) == "trusted"


def test_build_relationship_context_outputs_all_dimensions():
    scene_context = {
        "participants": [
            {
                "id": "dean",
                "relationships": {
                    "elina": {
                        "friendship": 0,
                        "trust": 0,
                        "respect": 5,
                        "attachment": 0,
                        "jealousy": 0,
                        "attraction": 4,
                    }
                },
            }
        ]
    }

    context = build_relationship_context(
        scene_context,
    )

    assert "dean -> elina" in context
    assert "friendship: 0/100" in context
    assert "trust: 0/100" in context
    assert "respect: 5/100" in context
    assert "attachment: 0/100" in context
    assert "jealousy: 0/100" in context
    assert "attraction: 4/100" in context


def test_build_relationship_context_handles_missing_relationships():
    scene_context = {
        "participants": [
            {
                "id": "dean",
            }
        ]
    }

    context = build_relationship_context(
        scene_context,
    )

    assert context == "No significant relationships yet."