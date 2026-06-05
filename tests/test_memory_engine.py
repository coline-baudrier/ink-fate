from backend.app.core.memory_engine import (
    apply_memory_updates,
    increase_memory_age,
    prune_memories,
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


def test_apply_memory_updates_skips_duplicate_content():
    characters = {
        "dean": {
            "memories": [
                {
                    "content": "Elina challenged Dean.",
                    "age": 1,
                }
            ]
        }
    }
    scene_result = {
        "memory_updates": [
            {
                "owner": "dean",
                "content": "  elina challenged dean! ",
                "age": 0,
            }
        ]
    }

    updated = apply_memory_updates(
        scene_result,
        characters,
    )

    assert len(updated["dean"]["memories"]) == 1


def test_prune_memories_keeps_most_important():
    characters = {
        "dean": {
            "memories": [
                {"content": f"Memory {i}", "importance": i, "age": 0}
                for i in range(1, 60)
            ]
        }
    }

    pruned = prune_memories(characters, max_per_character=10)

    memories = pruned["dean"]["memories"]
    assert len(memories) == 10

    importances = [m["importance"] for m in memories]
    assert min(importances) >= 50


def test_prune_memories_skips_characters_under_limit():
    characters = {
        "dean": {
            "memories": [
                {"content": "Memory", "importance": 5, "age": 0}
            ]
        }
    }

    pruned = prune_memories(characters, max_per_character=50)

    assert len(pruned["dean"]["memories"]) == 1


def test_prune_memories_favors_young_over_old_at_equal_importance():
    # Young important (5*3-0=15), Old important (5*3-5=10), Filler (1*3-0=3)
    # Top 2 → Young important + Old important, Filler pruned.
    characters = {
        "dean": {
            "memories": [
                {"content": "Old important", "importance": 5, "age": 5},
                {"content": "Young important", "importance": 5, "age": 0},
                {"content": "Filler", "importance": 1, "age": 0},
            ]
        }
    }

    pruned = prune_memories(characters, max_per_character=2)

    contents = [m["content"] for m in pruned["dean"]["memories"]]
    assert "Young important" in contents
    assert "Old important" in contents
    assert "Filler" not in contents
