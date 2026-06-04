"""Detection MVP des intentions de contact du joueur."""

from typing import Any, Dict
import re
import unicodedata


PHONE_GIVE_PATTERNS = [
    "je te donne mon numero",
    "je te donne mon num",
    "prends mon numero",
    "prend mon numero",
    "je t'envoie mon numero",
    "tu peux avoir mon numero",
    "voici mon numero",
]


def build_contact_intent_hints(
    player_input: str | None,
    world: Dict[str, Any],
    scene_context: Dict[str, Any],
) -> Dict[str, Any]:
    """Construit les indices deterministes de contact joueur."""

    return {
        "phone_number_given_to": detect_phone_number_recipient(
            player_input,
            world,
            scene_context,
        )
    }


def detect_phone_number_recipient(
    player_input: str | None,
    world: Dict[str, Any],
    scene_context: Dict[str, Any],
) -> str | None:
    """Detecte a quel PNJ le joueur donne clairement son numero."""

    if not player_input or not player_input.strip():
        return None

    normalized_input = normalize_text(player_input)

    if not any(
        pattern in normalized_input
        for pattern in PHONE_GIVE_PATTERNS
    ):
        return None

    player_character_id = world.get(
        "player_character",
        "",
    )
    participants = scene_context.get(
        "participants",
        [],
    )
    candidate_ids = []

    for participant in participants:
        if not isinstance(participant, dict):
            continue

        character_id = participant.get("id")

        if not isinstance(character_id, str):
            continue

        if character_id == player_character_id:
            continue

        identity = participant.get(
            "identity",
            {},
        )

        if participant_is_mentioned(
            normalized_input,
            character_id,
            identity,
        ):
            candidate_ids.append(character_id)

    if len(candidate_ids) == 1:
        return candidate_ids[0]

    non_player_participants = [
        participant.get("id")
        for participant in participants
        if isinstance(participant, dict)
        and isinstance(participant.get("id"), str)
        and participant.get("id") != player_character_id
    ]

    if len(non_player_participants) == 1:
        return non_player_participants[0]

    if "dean" in non_player_participants and contains_second_person_cue(
        normalized_input
    ):
        return "dean"

    return None


def apply_contact_intent_hints(
    scene_result: Dict[str, Any],
    world: Dict[str, Any],
    contact_intent_hints: Dict[str, Any] | None,
) -> Dict[str, Any]:
    """Ajoute un contact_update fiable quand le joueur donne son numero."""

    if not isinstance(contact_intent_hints, dict):
        return scene_result

    recipient_id = contact_intent_hints.get(
        "phone_number_given_to",
    )

    if not isinstance(recipient_id, str) or not recipient_id:
        return scene_result

    player_character_id = world.get(
        "player_character",
        "",
    )

    if recipient_id == player_character_id:
        return scene_result

    valid_character_ids = set(
        world.get(
            "characters",
            [],
        )
    )

    if recipient_id not in valid_character_ids:
        return scene_result

    if player_character_id not in valid_character_ids:
        return scene_result

    contact_updates = scene_result.get(
        "contact_updates",
        [],
    )

    if not isinstance(contact_updates, list):
        contact_updates = []

    for update in contact_updates:
        if not isinstance(update, dict):
            continue

        if update.get("source") != recipient_id:
            continue

        if update.get("target") != player_character_id:
            continue

        changes = update.get(
            "changes",
            {},
        )

        if not isinstance(changes, dict):
            continue

        if changes.get("phone_number_known") is True:
            scene_result["contact_updates"] = contact_updates
            return scene_result

    contact_updates.append(
        {
            "source": recipient_id,
            "target": player_character_id,
            "changes": {
                "phone_number_known": True,
            },
        }
    )
    scene_result["contact_updates"] = contact_updates

    return scene_result


def participant_is_mentioned(
    normalized_input: str,
    character_id: str,
    identity: Any,
) -> bool:
    """Verifie si le texte mentionne explicitement un participant."""

    aliases = [
        character_id,
    ]

    if isinstance(identity, dict):
        for key in ["first_name", "last_name"]:
            value = identity.get(key)

            if isinstance(value, str):
                aliases.append(value)

    return any(
        contains_phrase(
            normalized_input,
            normalize_text(alias),
        )
        for alias in aliases
        if alias
    )


def contains_second_person_cue(normalized_input: str) -> bool:
    """Detecte les formulations adressees directement a quelqu'un."""

    return any(
        cue in normalized_input
        for cue in [
            "je te ",
            "tu ",
            "t'envoie",
            "te donne",
            "ton ",
        ]
    )


def contains_phrase(text: str, phrase: str) -> bool:
    """Cherche une phrase avec frontieres de mots simples."""

    pattern = r"(?<!\w)" + re.escape(phrase) + r"(?!\w)"

    return re.search(
        pattern,
        text,
    ) is not None


def normalize_text(value: str) -> str:
    """Normalise accents, apostrophes, ponctuation et casse."""

    normalized = value.lower()
    normalized = normalized.replace("’", "'")
    normalized = normalized.replace("â€™", "'")
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
