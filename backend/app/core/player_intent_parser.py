"""Detection MVP des intentions explicites du joueur.

Ce module reste volontairement simple et deterministe. Il ne cherche pas a
comprendre toutes les actions, seulement les deplacements clairs vers un lieu
connu du monde courant.
"""

from typing import Any, Dict
import re
import unicodedata


LOCATION_SYNONYMS = {
    "campus": [
        "campus",
    ],
    "dormitory": [
        "dortoir",
        "residence",
        "résidence",
        "chambre",
    ],
    "hockey_house": [
        "hockey house",
        "maison de hockey",
        "maison des hockeyeurs",
    ],
    "library": [
        "bibliotheque",
        "bibliothèque",
        "library",
    ],
    "ice_rink": [
        "patinoire",
        "rink",
        "ice rink",
    ],
    "malones": [
        "malone's",
        "malones",
        "malone",
        "bar",
    ],
}

MOVEMENT_TERMS = [
    "je vais",
    "j'avance",
    "javance",
    "je rentre",
    "je retourne",
    "je file",
    "je pars",
    "je me dirige",
    "je marche",
    "je monte",
    "j'entre",
    "jentre",
    "direction",
    "vers",
]

LEAVES_NPCS_BEHIND_PHRASES = [
    "les laissant la",
    "je les laisse la",
    "je les plante la",
    "je pars sans eux",
    "je m'en vais seule",
    "je vais seule",
    "sans les attendre",
    "je les abandonne la",
]


def detect_player_movement(
    player_input: str | None,
    world: Dict[str, Any],
) -> str | None:
    """Retourne un lieu valide si le joueur s'y deplace clairement."""

    if not player_input or not player_input.strip():
        return None

    normalized_input = normalize_text(player_input)

    if not has_movement_signal(normalized_input):
        return None

    matches = []

    for location in world.get("locations", []):
        if not isinstance(location, dict):
            continue

        location_id = location.get("id")

        if not isinstance(location_id, str) or not location_id:
            continue

        aliases = build_location_aliases(location)

        for alias in aliases:
            normalized_alias = normalize_text(alias)

            if not normalized_alias:
                continue

            if contains_phrase(normalized_input, normalized_alias):
                matches.append(location_id)
                break

    unique_matches = sorted(set(matches))

    if len(unique_matches) != 1:
        return None

    return unique_matches[0]


def detect_player_leaves_npcs_behind(
    player_input: str | None,
) -> bool:
    """Detecte les cas explicites ou le joueur part sans les PNJ."""

    if not player_input or not player_input.strip():
        return False

    normalized_input = normalize_text(player_input)

    return any(
        phrase in normalized_input
        for phrase in LEAVES_NPCS_BEHIND_PHRASES
    )


def build_player_intent_hints(
    player_input: str | None,
    world: Dict[str, Any],
) -> Dict[str, Any]:
    """Construit les indices d'intention joueur injectables au prompt."""

    return {
        "detected_movement": detect_player_movement(
            player_input,
            world,
        ),
        "leaves_npcs_behind": detect_player_leaves_npcs_behind(
            player_input,
        ),
    }


def apply_player_intent_hints(
    scene_result: Dict[str, Any],
    world: Dict[str, Any],
    player_intent_hints: Dict[str, Any] | None,
) -> Dict[str, Any]:
    """Force new_location si le LLM a oublie un mouvement joueur detecte."""

    if not isinstance(player_intent_hints, dict):
        return scene_result

    detected_movement = player_intent_hints.get(
        "detected_movement",
    )

    if not isinstance(detected_movement, str) or not detected_movement:
        return scene_result

    valid_location_ids = {
        location.get("id")
        for location in world.get("locations", [])
        if isinstance(location, dict)
    }

    if detected_movement not in valid_location_ids:
        return scene_result

    world_updates = scene_result.get(
        "world_updates",
        {},
    )

    if not isinstance(world_updates, dict):
        world_updates = {}

    current_new_location = world_updates.get(
        "new_location",
        "",
    )

    if (
        not isinstance(current_new_location, str)
        or not current_new_location
    ):
        world_updates["new_location"] = detected_movement

    if player_intent_hints.get("leaves_npcs_behind") is True:
        world_updates["character_movements"] = (
            remove_npc_movements_to_player_destination(
                world_updates.get("character_movements", {}),
                detected_movement,
                world.get("player_character", ""),
            )
        )
        scene_result["dialogues"] = limit_left_behind_npc_dialogues(
            scene_result.get("dialogues", []),
            world.get("player_character", ""),
        )

    scene_result["world_updates"] = world_updates

    return scene_result


def limit_left_behind_npc_dialogues(
    dialogues: Any,
    player_character_id: str,
    max_dialogues: int = 1,
) -> list[Dict[str, Any]]:
    """Garde au plus une reaction PNJ quand le joueur les laisse derriere."""

    if not isinstance(dialogues, list):
        return []

    kept_dialogues = []

    for dialogue in dialogues:
        if not isinstance(dialogue, dict):
            continue

        if dialogue.get("speaker") == player_character_id:
            continue

        kept_dialogues.append(dialogue)

        if len(kept_dialogues) >= max_dialogues:
            break

    return kept_dialogues


def remove_npc_movements_to_player_destination(
    character_movements: Any,
    player_destination: str,
    player_character_id: str,
) -> Dict[str, str]:
    """Retire les PNJ qui suivent le joueur malgre une intention contraire."""

    if not isinstance(character_movements, dict):
        return {}

    cleaned_movements = {}

    for character_id, location_id in character_movements.items():
        if not isinstance(character_id, str):
            continue

        if not isinstance(location_id, str):
            continue

        if character_id == player_character_id:
            cleaned_movements[character_id] = location_id
            continue

        if location_id == player_destination:
            continue

        cleaned_movements[character_id] = location_id

    return cleaned_movements


def build_location_aliases(location: Dict[str, Any]) -> list[str]:
    """Retourne les noms et synonymes utilisables pour un lieu."""

    aliases = []
    location_id = location.get("id")
    location_name = location.get("name")

    if isinstance(location_id, str):
        aliases.append(location_id.replace("_", " "))
        aliases.extend(
            LOCATION_SYNONYMS.get(
                location_id,
                [],
            )
        )

    if isinstance(location_name, str):
        aliases.append(location_name)

    return aliases


def has_movement_signal(normalized_input: str) -> bool:
    """Verifie qu'il y a au moins un verbe ou marqueur de deplacement."""

    return any(
        movement_term in normalized_input
        for movement_term in MOVEMENT_TERMS
    )


def contains_phrase(text: str, phrase: str) -> bool:
    """Cherche une phrase en respectant les frontieres de mots simples."""

    pattern = r"(?<!\w)" + re.escape(phrase) + r"(?!\w)"

    return re.search(
        pattern,
        text,
    ) is not None


def normalize_text(value: str) -> str:
    """Normalise accents, apostrophes et casse pour comparer simplement."""

    normalized = value.lower()
    normalized = normalized.replace("’", "'")
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
        r"[^a-z0-9']+",
        " ",
        normalized,
    )

    return re.sub(
        r"\s+",
        " ",
        normalized,
    ).strip()
