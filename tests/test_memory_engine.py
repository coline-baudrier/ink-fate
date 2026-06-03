from backend.app.core.memory_engine import (
    apply_memory_updates,
    increase_memory_age,
)


def test_increase_memory_age_does_not_age_new_memory():
    characters = {
        "dean": {
            "memories": [
                {
                    "content": "Old memory",
                    "age": 2,
                }
            ]
        }
    }

    scene_result = {
        "memory_updates": [
            {
                "owner": "dean",
                "content": "New memory",
                "age": 0,
            }
        ]
    }

    characters = apply_memory_updates(
        scene_result,
        characters,
    )

    characters = increase_memory_age(characters)

    memories = characters["dean"]["memories"]

    assert memories[0]["age"] == 3
    assert memories[1]["age"] == 0
    assert "_created_this_turn" not in memories[1]


def test_increase_memory_age_resets_invalid_age():
    characters = {
        "dean": {
            "memories": [
                {
                    "content": "Memory with invalid age",
                    "age": "old",
                }
            ]
        }
    }

    updated_characters = increase_memory_age(characters)

    memory = updated_characters["dean"]["memories"][0]

    assert memory["age"] == 1
