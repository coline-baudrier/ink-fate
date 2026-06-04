from typing import Any, Dict
import re
import unicodedata


def apply_memory_updates(
    scene_result: Dict[str, Any],
    characters: Dict[str, Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """
    Applique les nouveaux souvenirs
    aux personnages concernés.
    """

    memory_updates = scene_result.get(
        "memory_updates",
        [],
    )

    for memory in memory_updates:
        owner_id = memory.get("owner")

        character = characters.get(owner_id)

        if not character:
            continue

        character_memories = character.get(
            "memories",
            [],
        )

        if not isinstance(character_memories, list):
            character_memories = []

        if memory_already_exists(
            character_memories,
            memory,
        ):
            continue

        # Ce marqueur evite de vieillir un souvenir cree pendant ce tour.
        memory["_created_this_turn"] = True
        character_memories.append(memory)

        character["memories"] = character_memories

    return characters


def memory_already_exists(
    memories: list[Dict[str, Any]],
    new_memory: Dict[str, Any],
) -> bool:
    """Evite d'ajouter deux fois le meme souvenir textuel."""

    new_content = normalize_memory_content(
        new_memory.get(
            "content",
            "",
        )
    )

    if not new_content:
        return False

    for memory in memories:
        if not isinstance(memory, dict):
            continue

        content = normalize_memory_content(
            memory.get(
                "content",
                "",
            )
        )

        if content == new_content:
            return True

    return False


def normalize_memory_content(value: Any) -> str:
    """Normalise un contenu de souvenir pour detecter les doublons."""

    if not isinstance(value, str):
        return ""

    normalized = value.lower()
    normalized = unicodedata.normalize(
        "NFKD",
        normalized,
    )
    normalized = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )
    normalized = re.sub(
        r"[^a-z0-9]+",
        " ",
        normalized,
    )

    return re.sub(
        r"\s+",
        " ",
        normalized,
    ).strip()


def increase_memory_age(
    characters: Dict[str, Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """
    Vieillit les souvenirs de tous les personnages.
    """

    for character in characters.values():
        memories = character.get(
            "memories",
            [],
        )

        for memory in memories:
            if memory.pop("_created_this_turn", False):
                continue

            age = memory.get("age", 0)

            if not isinstance(age, int):
                age = 0

            memory["age"] = age + 1

    return characters
