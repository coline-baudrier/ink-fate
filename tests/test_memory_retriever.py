from backend.app.core.memory_retriever import (
    score_memory,
    select_relevant_memories,
)

def build_scene_context():
    return {
        "participants": [
            {
                "id": "dean",
                "memories": [
                    {
                        "content": "Elina challenged Dean directly.",
                        "importance": 8,
                        "age": 1,
                        "tags": ["challenge", "elina"],
                    },
                    {
                        "content": "Dean ate breakfast.",
                        "importance": 2,
                        "age": 0,
                        "tags": ["food"],
                    },
                    {
                        "content": "Dean noticed Elina's confidence.",
                        "importance": 6,
                        "age": 2,
                        "tags": ["attraction", "confidence"],
                    },
                ],
            },
            {
                "id": "beau",
                "memories": [
                    {
                        "content": "Beau saw Elina tease Dean.",
                        "importance": 5,
                        "age": 1,
                        "tags": ["teasing", "dean"],
                    }
                ],
            },
        ]
    }


def test_score_memory_uses_importance_and_age():
    memory = {
        "content": "A simple memory.",
        "importance": 5,
        "age": 2,
        "tags": [],
    }

    score = score_memory(
        memory,
        player_input=None,
        scene_history=None,
    )

    assert score == 13


def test_score_memory_adds_tag_bonus():
    memory = {
        "content": "Dean remembers the challenge.",
        "importance": 1,
        "age": 0,
        "tags": ["challenge"],
    }

    score = score_memory(
        memory,
        player_input="Elina challenges him again.",
        scene_history=None,
    )

    assert score == 8


def test_score_memory_adds_content_word_bonus():
    memory = {
        "content": "Elina showed confidence.",
        "importance": 1,
        "age": 0,
        "tags": [],
    }

    score = score_memory(
        memory,
        player_input="Dean notices her confidence.",
        scene_history=None,
    )

    assert score == 5


def test_score_memory_handles_invalid_fields():
    memory = {
        "content": None,
        "importance": "high",
        "age": "old",
        "tags": "challenge",
    }

    score = score_memory(
        memory,
        player_input="challenge",
        scene_history=None,
    )

    assert score == 0


def test_select_relevant_memories_returns_sorted_memories():
    scene_context = build_scene_context()

    selected = select_relevant_memories(
        scene_context,
        player_input="Elina challenges Dean with confidence.",
        scene_history=None,
    )

    dean_memories = selected["dean"]

    assert dean_memories[0]["content"] == (
        "Elina challenged Dean directly."
    )
    assert dean_memories[1]["content"] == (
        "Dean noticed Elina's confidence."
    )


def test_select_relevant_memories_respects_limit():
    scene_context = build_scene_context()

    selected = select_relevant_memories(
        scene_context,
        player_input="Elina challenges Dean with confidence.",
        scene_history=None,
        max_memories_per_character=1,
    )

    assert len(selected["dean"]) == 1


def test_select_relevant_memories_ignores_invalid_memory_list():
    scene_context = {
        "participants": [
            {
                "id": "dean",
                "memories": "not-a-list",
            }
        ]
    }

    selected = select_relevant_memories(
        scene_context,
        player_input="anything",
        scene_history=None,
    )

    assert selected == {}


def test_select_relevant_memories_uses_location_context():
    scene_context = {
        "location": {
            "id": "library",
            "name": "University Library",
        },
        "participants": [
            {
                "id": "dean",
                "memories": [
                    {
                        "content": "Dean saw Elina in the library.",
                        "importance": 1,
                        "age": 0,
                        "tags": [
                            "library",
                        ],
                    }
                ],
            }
        ],
    }

    selected = select_relevant_memories(
        scene_context,
    )

    assert selected["dean"][0]["content"] == (
        "Dean saw Elina in the library."
    )


def test_select_relevant_memories_uses_relationship_context():
    scene_context = {
        "participants": [
            {
                "id": "dean",
                "relationships": {
                    "elina": {
                        "attraction": 60,
                    }
                },
                "memories": [
                    {
                        "content": "Dean felt romantic tension.",
                        "importance": 1,
                        "age": 0,
                        "tags": [
                            "high_attraction",
                        ],
                    }
                ],
            }
        ],
    }

    selected = select_relevant_memories(
        scene_context,
    )

    assert selected["dean"][0]["content"] == (
        "Dean felt romantic tension."
    )
