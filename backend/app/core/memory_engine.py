from typing import Any, Dict


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

        # Ce marqueur evite de vieillir un souvenir cree pendant ce tour.
        memory["_created_this_turn"] = True
        character_memories.append(memory)

        character["memories"] = character_memories

    return characters

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
