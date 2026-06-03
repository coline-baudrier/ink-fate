from typing import Any, Dict


def score_memory(
    memory: Dict[str, Any],
    player_input: str | None,
    scene_history: str | None,
) -> int:
    """Calcule un score de pertinence pour un souvenir."""

    score = memory.get("importance", 0) * 3
    score -= memory.get("age", 0)

    searchable_text = " ".join(
        [
            player_input or "",
            scene_history or "",
        ]
    ).lower()

    content = memory.get("content", "").lower()
    tags = memory.get("tags", [])

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