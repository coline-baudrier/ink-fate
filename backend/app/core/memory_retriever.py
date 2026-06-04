from typing import Any, Dict


def score_memory(
    memory: Dict[str, Any],
    player_input: str | None,
    scene_history: str | None,
    context_terms: list[str] | None = None,
) -> int:
    """Calcule un score de pertinence pour un souvenir."""

    importance = memory.get("importance", 0)

    if not isinstance(importance, int):
        importance = 0

    age = memory.get("age", 0)

    if not isinstance(age, int):
        age = 0

    score = importance * 3
    score -= age

    searchable_text = " ".join(
        [
            player_input or "",
            scene_history or "",
            " ".join(context_terms or []),
        ]
    ).lower()

    content = memory.get("content", "")

    if not isinstance(content, str):
        content = ""

    content = content.lower()

    tags = memory.get("tags", [])

    if not isinstance(tags, list):
        tags = []

    for tag in tags:
        if isinstance(tag, str) and tag.lower() in searchable_text:
            score += 5

    for word in content.split():
        if len(word) > 4 and word in searchable_text:
            score += 2

    return score


def select_relevant_memories(
    scene_context: Dict[str, Any],
    player_input: str | None = None,
    scene_history: str | None = None,
    max_memories_per_character: int = 5,
) -> Dict[str, list[Dict[str, Any]]]:
    """Selectionne les souvenirs les plus pertinents par personnage."""

    selected_memories = {}
    context_terms = build_scene_context_terms(scene_context)

    for character in scene_context["participants"]:
        character_id = character["id"]
        memories = character.get("memories", [])

        if not isinstance(memories, list):
            continue

        scored_memories = []

        for memory in memories:
            if not isinstance(memory, dict):
                continue

            score = score_memory(
                memory,
                player_input,
                scene_history,
                context_terms,
            )

            scored_memories.append(
                (score, memory)
            )

        scored_memories.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        top_memories = [
            memory
            for score, memory in scored_memories[:max_memories_per_character]
            if score > 0
        ]

        if top_memories:
            selected_memories[character_id] = top_memories

    return selected_memories


def build_scene_context_terms(
    scene_context: Dict[str, Any],
) -> list[str]:
    """Construit des mots utiles a partir du lieu et des relations."""

    terms = []
    location = scene_context.get(
        "location",
        {},
    )

    if isinstance(location, dict):
        for key in [
            "id",
            "name",
            "description",
        ]:
            value = location.get(key)

            if isinstance(value, str):
                terms.append(value)

    for character in scene_context.get("participants", []):
        if not isinstance(character, dict):
            continue

        character_id = character.get("id")

        if isinstance(character_id, str):
            terms.append(character_id)

        relationships = character.get(
            "relationships",
            {},
        )

        if not isinstance(relationships, dict):
            continue

        for target_id, relationship in relationships.items():
            if isinstance(target_id, str):
                terms.append(target_id)

            if not isinstance(relationship, dict):
                continue

            for dimension, value in relationship.items():
                if isinstance(dimension, str):
                    terms.append(dimension)

                if isinstance(value, int) and value >= 50:
                    terms.append(f"high_{dimension}")

    recent_events = scene_context.get(
        "recent_events",
        [],
    )

    if isinstance(recent_events, list):
        for event in recent_events:
            if not isinstance(event, dict):
                continue

            for value in event.values():
                if isinstance(value, str):
                    terms.append(value)

    return terms
