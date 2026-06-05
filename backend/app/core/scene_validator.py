"""Validation minimale d'un SceneResult.

Le LLM peut renvoyer une structure imparfaite. Ce module nettoie ce que le
moteur sait verifier avant d'appliquer des effets au monde.
"""

from typing import Any, Dict
import re
import unicodedata

RELATIONSHIP_DELTA_LIMITS = {
    "attraction": {
        "min": -2,
        "max": 2,
    },
    "respect": {
        "min": -3,
        "max": 3,
    },
    "friendship": {
        "min": -2,
        "max": 2,
    },
    "trust": {
        "min": -1,
        "max": 2,
    },
    "attachment": {
        "min": -1,
        "max": 1,
    },
    "jealousy": {
        "min": -2,
        "max": 2,
    },
}

CONTACT_UPDATE_FIELDS = {
    "phone_number_known",
    "phone_numbers_exchanged",
    "instagram_connected",
}

MEMORY_TYPES = {
    "memory",
    "relationship",
    "event",
    "promise",
    "conflict",
    "preference",
}

MAX_NARRATION_PARAGRAPHS = 3
MAX_DIALOGUES = 4

FILLER_NARRATION_PATTERNS = [
    # Phrases méta-narratives sur la pause de la scène elle-même
    "la scene marque une pause",
    "la scene se suspend",
    "l'echange marque une pause",
    "la conversation marque une pause",
    "l'instant marque une pause",
    "l'instant se suspend",
    "le moment marque une pause",
    # Reprendre ses repères — idiome filler caractéristique
    "reprenne ses reperes",
    "reprend ses reperes",
    "retrouve ses reperes",
    "retrouve ses marques",
    "reprennent leurs reperes",
    "retrouvent leurs reperes",
    # Phrases collectives méta — uniquement les combinaisons spécifiques
    "chacun se repositionne",
    "chacun reprend son souffle",
    "le temps que chacun",
    "le temps que tout le monde",
    "le groupe se reajuste",
    # Atmosphère qui se réinstalle / retombe
    "l'atmosphere retombe",
    "l'atmosphere se reinstalle",
    "l'atmosphere se reequilibre",
    # Silence collectif de remplissage
    "nul n'ajoute rien",
    "personne n'ajoute rien",
    "plus personne ne dit",
    "plus personne n'ajoute",
]

# Patterns d'état intérieur — s'appliquent si le nom du joueur OU le pronom "elle" est présent.
# Restent peu ambigus car ces états sont rares dans la narration d'un PNJ.
PLAYER_INTERNAL_STATE_PATTERNS = [
    # Pensées / cognition
    "pense",
    "songe",
    "se demande",
    "sait que",
    "comprend que",
    "realise que",
    "consciente que",
    "remarque que",
    "note que",
    # Émotions / états intérieurs
    "se sent",
    "ressent",
    "espere",
    "redoute",
    "craint",
    "a envie",
    "est excitee",
    "est nerveuse",
    "est determinee",
    "est curieuse",
    "est soulagee",
    "est troublee",
    "est attiree",
    "est effrayee",
    "est amusee",
    "est agacee",
    "est surprise",
    "fait ressentir",
    # Attribution implicite d'état
    "semble",
    "parait",
    "comme si elle",
    "donne l'impression",
    "on dirait qu'elle",
    "anticipant",
    "profitant",
    "savourant",
]

# Patterns d'action volontaire — s'appliquent SEULEMENT si le nom du joueur est explicitement
# mentionné dans la phrase. "elle" seul est insuffisant car n'importe quel PNJ féminin peut
# "décider de", "s'apprêter à", etc.
PLAYER_ACTION_PATTERNS = [
    "decide de",
    "choisit de",
    "s'apprete a",
    "a l'intention de",
    "compte partir",
    "compte rejoindre",
    "prend conge",
    "tourne les talons",
    "regagne sa chambre",
    "rentre dans sa chambre",
    "rentre chez elle",
    "se dirige vers sa chambre",
    "monte vers sa chambre",
]


def ensure_list(value: Any) -> list:
    """Retourne la valeur si c'est une liste, sinon une liste vide."""

    if isinstance(value, list):
        return value

    return []


def ensure_dict(value: Any) -> dict:
    """Retourne la valeur si c'est un dictionnaire, sinon un dict vide."""

    if isinstance(value, dict):
        return value

    return {}


def ensure_string(value: Any) -> str:
    """Retourne une chaine propre, sinon une chaine vide."""

    if not isinstance(value, str):
        return ""

    return value.strip()


def ensure_int(value: Any, default: int = 0) -> int:
    """Retourne un entier, en evitant les booleens."""

    if isinstance(value, bool):
        return default

    if not isinstance(value, int):
        return default

    return value


def is_valid_time(value: Any) -> bool:
    """Verifie qu'une heure ressemble a HH:MM."""

    if not isinstance(value, str):
        return False

    parts = value.split(":")

    if len(parts) != 2:
        return False

    hours, minutes = parts

    if not hours.isdigit():
        return False

    if not minutes.isdigit():
        return False

    hour_value = int(hours)
    minute_value = int(minutes)

    return 0 <= hour_value <= 23 and 0 <= minute_value <= 59


def validate_scene(
    scene_result: Dict[str, Any],
    world: Dict[str, Any],
) -> Dict[str, Any]:
    """Nettoie les informations principales de la scene."""

    valid_location_ids = {
        location["id"]
        for location in world["locations"]
    }

    valid_character_ids = set(
        world["characters"]
    )

    active_scene = world["active_scene"]
    timeline = world["timeline"]
    player_character_id = world.get(
        "player_character",
        "",
    )
    scene = ensure_dict(
        scene_result.get(
            "scene",
            {},
        )
    )

    location = ensure_string(
        scene.get(
            "location",
            active_scene["location"],
        )
    )

    if location not in valid_location_ids:
        location = active_scene["location"]

    time = scene.get(
        "time",
        timeline["current_time"],
    )

    if not is_valid_time(time):
        time = timeline["current_time"]

    participant_ids = ensure_list(
        scene.get(
            "participants",
            active_scene.get(
                "participants",
                [],
            ),
        )
    )

    participant_location_ids = get_allowed_participant_location_ids(
        scene_result,
        world,
        location,
    )
    valid_participants = []

    for character_id in participant_ids:
        character_id = ensure_string(character_id)

        if character_id not in valid_character_ids:
            continue

        if not can_character_participate_at_location(
            world,
            character_id,
            location,
            participant_location_ids,
        ):
            continue

        valid_participants.append(character_id)

    if not valid_participants:
        valid_participants = [
            character_id
            for character_id in active_scene.get(
                "participants",
                [],
            )
            if character_id in valid_character_ids
        ]

    if (
        player_character_id in valid_character_ids
        and player_character_id not in valid_participants
    ):
        valid_participants.insert(
            0,
            player_character_id,
        )

    scene_result["scene"] = {
        "location": location,
        "time": time,
        "participants": valid_participants,
    }

    return scene_result


def remove_player_dialogues(
    scene_result: Dict[str, Any],
    player_character_id: str,
) -> Dict[str, Any]:
    """Supprime les dialogues generes pour le personnage joueur."""

    filtered_dialogues = []

    # On force une liste pour eviter de planter si le LLM renvoie autre chose.
    dialogues = ensure_list(scene_result.get("dialogues", []))

    for dialogue in dialogues:
        if not isinstance(dialogue, dict):
            continue

        speaker = ensure_string(
            dialogue.get("speaker")
        )

        if speaker == player_character_id:
            continue

        dialogue["speaker"] = speaker
        filtered_dialogues.append(dialogue)

    scene_result["dialogues"] = filtered_dialogues

    return scene_result


def remove_invalid_dialogues(
    scene_result: Dict[str, Any],
    valid_character_ids: list[str],
) -> Dict[str, Any]:
    """Supprime les dialogues dont le speaker n'est pas valide."""

    valid_dialogues = []

    dialogues = ensure_list(scene_result.get("dialogues", []))

    for dialogue in dialogues:
        if not isinstance(dialogue, dict):
            continue

        speaker = ensure_string(
            dialogue.get("speaker")
        )

        if speaker not in valid_character_ids:
            continue

        dialogue["speaker"] = speaker
        valid_dialogues.append(dialogue)

    scene_result["dialogues"] = valid_dialogues

    return scene_result


def remove_invalid_actions(
    scene_result: Dict[str, Any],
    valid_character_ids: list[str],
) -> Dict[str, Any]:
    """Supprime les actions dont le personnage n'est pas valide."""

    valid_actions = []

    actions = ensure_list(scene_result.get("actions", []))

    for action in actions:
        if not isinstance(action, dict):
            continue

        character = ensure_string(
            action.get("character")
        )

        if character not in valid_character_ids:
            continue

        action_type = ensure_string(
            action.get("type")
        )

        if not action_type:
            continue

        target = ensure_string(
            action.get("target")
        )

        if target and target not in valid_character_ids:
            continue

        action["character"] = character
        action["type"] = action_type
        action["target"] = target

        valid_actions.append(action)

    scene_result["actions"] = valid_actions

    return scene_result


def remove_invalid_events(
    scene_result: Dict[str, Any],
    valid_character_ids: list[str],
) -> Dict[str, Any]:
    """Supprime les evenements ou participants invalides."""

    valid_events = []

    events = ensure_list(scene_result.get("events", []))

    for event in events:
        if not isinstance(event, dict):
            continue

        participants = ensure_list(event.get("participants", []))

        valid_participants = []

        for participant in participants:
            participant = ensure_string(participant)

            if participant in valid_character_ids:
                valid_participants.append(participant)

        if not valid_participants:
            continue

        event_type = ensure_string(
            event.get("type")
        )

        if not event_type:
            continue

        summary = ensure_string(
            event.get("summary")
        )

        event["type"] = event_type

        if summary:
            event["summary"] = summary
        elif "summary" in event:
            event.pop("summary")

        # On garde l'evenement, mais seulement avec ses participants valides.
        event["participants"] = valid_participants
        valid_events.append(event)

    scene_result["events"] = valid_events

    return scene_result


def remove_invalid_relationship_updates(
    scene_result: Dict[str, Any],
    valid_character_ids: list[str],
) -> Dict[str, Any]:
    """Supprime les mises a jour relationnelles invalides."""

    valid_updates = []

    relationship_updates = ensure_list(
        scene_result.get("relationship_updates", [])
    )

    for update in relationship_updates:
        if not isinstance(update, dict):
            continue

        source = ensure_string(
            update.get("source")
        )

        target = ensure_string(
            update.get("target")
        )

        if source not in valid_character_ids:
            continue

        if target not in valid_character_ids:
            continue

        update["source"] = source
        update["target"] = target

        valid_updates.append(update)

    scene_result["relationship_updates"] = valid_updates

    return scene_result


def clamp_relationship_updates(
    scene_result: Dict[str, Any],
) -> Dict[str, Any]:
    """Valide et limite les changements relationnels."""

    relationship_updates = ensure_list(
        scene_result.get("relationship_updates", [])
    )

    valid_relationship_updates = []

    for update in relationship_updates:
        if not isinstance(update, dict):
            continue

        changes = ensure_dict(update.get("changes", {}))
        valid_changes = {}

        for key, value in changes.items():
            key = ensure_string(key)

            if not key:
                continue

            if isinstance(value, bool) or not isinstance(value, int):
                continue

            limits = RELATIONSHIP_DELTA_LIMITS.get(
                key,
                {
                    "min": -2,
                    "max": 2,
                },
            )

            min_value = limits["min"]
            max_value = limits["max"]

            if value < min_value:
                value = min_value

            if value > max_value:
                value = max_value

            valid_changes[key] = value

        update["changes"] = valid_changes
        valid_relationship_updates.append(update)

    scene_result["relationship_updates"] = valid_relationship_updates

    return scene_result


def remove_player_internal_state_from_narration(
    scene_result: Dict[str, Any],
    player_character_id: str,
) -> Dict[str, Any]:
    """Retire les phrases qui decident l'interiorite du joueur."""

    narration = ensure_list(
        scene_result.get(
            "narration",
            [],
        )
    )
    filtered_narration = []
    player_names = build_player_reference_names(
        player_character_id,
    )

    for paragraph in narration:
        if not isinstance(paragraph, str):
            continue

        cleaned_paragraph = remove_player_internal_state_sentences(
            paragraph,
            player_names,
        )

        if cleaned_paragraph:
            filtered_narration.append(cleaned_paragraph)

    scene_result["narration"] = filtered_narration

    return scene_result


def remove_filler_narration(
    scene_result: Dict[str, Any],
) -> Dict[str, Any]:
    """Retire les phrases de narration qui ne font que combler un vide."""

    narration = ensure_list(scene_result.get("narration", []))
    filtered_narration = []

    for paragraph in narration:
        if not isinstance(paragraph, str):
            continue

        cleaned = remove_filler_sentences(paragraph)

        if cleaned:
            filtered_narration.append(cleaned)

    scene_result["narration"] = filtered_narration
    return scene_result


def remove_filler_sentences(paragraph: str) -> str:
    """Supprime les phrases de remplissage dans un paragraphe."""

    sentences = split_narration_sentences(paragraph)
    kept = []

    for sentence in sentences:
        if is_filler_sentence(sentence):
            continue
        kept.append(sentence.strip())

    return " ".join(s for s in kept if s).strip()


def is_filler_sentence(sentence: str) -> bool:
    """Detecte une phrase de transition sans contenu narratif reel."""

    normalized = normalize_text(sentence)
    return any(pattern in normalized for pattern in FILLER_NARRATION_PATTERNS)


def build_player_reference_names(
    player_character_id: str,
) -> set[str]:
    """Construit les references textuelles simples au joueur."""

    names = set()
    player_character_id = ensure_string(
        player_character_id,
    )

    if player_character_id:
        names.add(
            normalize_text(player_character_id)
        )

    return names


def remove_player_internal_state_sentences(
    paragraph: str,
    player_names: set[str],
) -> str:
    """Supprime les phrases qui attribuent une pensee ou emotion au joueur."""

    sentences = split_narration_sentences(
        paragraph,
    )
    kept_sentences = []

    for sentence in sentences:
        if is_player_internal_state_sentence(
            sentence,
            player_names,
        ):
            continue

        kept_sentences.append(
            sentence.strip()
        )

    return " ".join(
        sentence
        for sentence in kept_sentences
        if sentence
    ).strip()


def split_narration_sentences(
    paragraph: str,
) -> list[str]:
    """Decoupe un paragraphe en phrases en gardant la ponctuation."""

    paragraph = paragraph.strip()

    if not paragraph:
        return []

    return [
        sentence.strip()
        for sentence in re.split(
            r"(?<=[.!?])\s+",
            paragraph,
        )
        if sentence.strip()
    ]


def is_player_internal_state_sentence(
    sentence: str,
    player_names: set[str],
) -> bool:
    """Detecte une phrase qui decrit l'interiorite du joueur."""

    normalized_sentence = normalize_text(
        sentence,
    )

    mentions_player = any(
        player_name in normalized_sentence
        for player_name in player_names
    )
    uses_player_pronoun = bool(
        re.search(
            r"\belle\b",
            normalized_sentence,
        )
    )

    if not mentions_player and not uses_player_pronoun:
        return False

    # Patterns d'état intérieur : suffisant d'avoir le nom ou le pronom.
    if any(pattern in normalized_sentence for pattern in PLAYER_INTERNAL_STATE_PATTERNS):
        return True

    # Patterns d'action volontaire : exige que le nom du joueur soit explicitement présent,
    # car "elle" seul peut désigner n'importe quel PNJ féminin.
    if mentions_player and any(pattern in normalized_sentence for pattern in PLAYER_ACTION_PATTERNS):
        return True

    return False


def remove_narration_about_absent_characters(
    scene_result: Dict[str, Any],
    all_character_ids: list[str],
) -> Dict[str, Any]:
    """Retire les paragraphes de narration portant sur des personnages absents.

    Un paragraphe est retire s'il mentionne uniquement des personnages absents
    de la scene active, sans mentionner aucun participant present.
    Les paragraphes neutres (pas de personnage) sont conserves.
    """

    scene = ensure_dict(scene_result.get("scene", {}))
    participants = {
        ensure_string(p)
        for p in ensure_list(scene.get("participants", []))
        if ensure_string(p)
    }
    absent = {cid for cid in all_character_ids if cid not in participants}

    if not absent:
        return scene_result

    narration = ensure_list(scene_result.get("narration", []))
    filtered = []

    for paragraph in narration:
        if not isinstance(paragraph, str) or not paragraph.strip():
            continue

        normalized = normalize_text(paragraph)
        mentions_absent = any(normalize_text(cid) in normalized for cid in absent)

        if not mentions_absent:
            filtered.append(paragraph)
            continue

        # A participant counts as "mentioned" only when their name is NOT preceded by
        # a French apostrophe — this avoids false positives like "d'Elina" (genitive
        # reference) being mistaken for Elina being the subject of the sentence.
        def _is_subject_mention(text: str, character_id: str) -> bool:
            pattern = r"(?<!['’])" + re.escape(normalize_text(character_id))
            return bool(re.search(pattern, text))

        mentions_participant_as_subject = any(
            _is_subject_mention(normalized, pid) for pid in participants
        )

        # If the paragraph starts with an absent character's name, it is primarily
        # about that absent character and must be removed even if a participant
        # appears later as an object/reference.
        paragraph_starts_with_absent = any(
            normalized.lstrip().startswith(normalize_text(cid)) for cid in absent
        )

        if paragraph_starts_with_absent or not mentions_participant_as_subject:
            continue

        filtered.append(paragraph)

    scene_result["narration"] = filtered
    return scene_result


def remove_dialogues_from_nonparticipants(
    scene_result: Dict[str, Any],
) -> Dict[str, Any]:
    """Supprime les dialogues de personnages absents de la scene validee."""

    scene = ensure_dict(
        scene_result.get(
            "scene",
            {},
        )
    )
    participants = {
        ensure_string(participant)
        for participant in ensure_list(
            scene.get(
                "participants",
                [],
            )
        )
    }
    filtered_dialogues = []

    for dialogue in ensure_list(scene_result.get("dialogues", [])):
        if not isinstance(dialogue, dict):
            continue

        speaker = ensure_string(
            dialogue.get("speaker")
        )

        if speaker not in participants:
            continue

        dialogue["speaker"] = speaker
        filtered_dialogues.append(dialogue)

    scene_result["dialogues"] = filtered_dialogues

    return scene_result


def get_allowed_participant_location_ids(
    scene_result: Dict[str, Any],
    world: Dict[str, Any],
    scene_location: str,
) -> Dict[str, str]:
    """Retourne les destinations proposees qui autorisent une presence."""

    world_updates = ensure_dict(
        scene_result.get(
            "world_updates",
            {},
        )
    )
    character_movements = ensure_dict(
        world_updates.get(
            "character_movements",
            {},
        )
    )
    player_character_id = world.get(
        "player_character",
        "",
    )
    new_location = ensure_string(
        world_updates.get(
            "new_location",
            "",
        )
    )

    allowed_locations = {}

    for character_id, location_id in character_movements.items():
        character_id = ensure_string(character_id)
        location_id = ensure_string(location_id)

        if character_id and location_id:
            allowed_locations[character_id] = location_id

    if new_location == scene_location and player_character_id:
        allowed_locations[player_character_id] = new_location

    return allowed_locations


def can_character_participate_at_location(
    world: Dict[str, Any],
    character_id: str,
    scene_location: str,
    proposed_locations: Dict[str, str],
) -> bool:
    """Verifie qu'un participant peut etre present dans cette scene."""

    if "character_locations" not in world:
        return True

    character_locations = world.get(
        "character_locations",
        {},
    )

    if not isinstance(character_locations, dict):
        return True

    player_character_id = world.get(
        "player_character",
        "",
    )

    if character_id == player_character_id:
        return True

    if proposed_locations.get(character_id) == scene_location:
        return True

    return character_locations.get(character_id) == scene_location


def remove_invalid_contact_updates(
    scene_result: Dict[str, Any],
    valid_character_ids: list[str],
) -> Dict[str, Any]:
    """Supprime les mises a jour de contacts invalides."""

    valid_updates = []

    contact_updates = ensure_list(
        scene_result.get("contact_updates", [])
    )

    for update in contact_updates:
        if not isinstance(update, dict):
            continue

        source = ensure_string(
            update.get("source")
        )

        target = ensure_string(
            update.get("target")
        )

        if source not in valid_character_ids:
            continue

        if target not in valid_character_ids:
            continue

        changes = ensure_dict(
            update.get("changes", {})
        )

        valid_changes = {}

        for key, value in changes.items():
            key = ensure_string(key)

            if key not in CONTACT_UPDATE_FIELDS:
                continue

            if not isinstance(value, bool):
                continue

            valid_changes[key] = value

        update["source"] = source
        update["target"] = target
        update["changes"] = valid_changes

        valid_updates.append(update)

    scene_result["contact_updates"] = valid_updates

    return scene_result


def remove_invalid_memory_updates(
    scene_result: Dict[str, Any],
    valid_character_ids: list[str],
) -> Dict[str, Any]:
    """Supprime les souvenirs invalides."""

    valid_memories = []

    memory_updates = ensure_list(
        scene_result.get("memory_updates", [])
    )

    for memory in memory_updates:
        if not isinstance(memory, dict):
            continue

        owner = ensure_string(
            memory.get("owner")
        )

        if owner not in valid_character_ids:
            continue

        content = ensure_string(
            memory.get("content")
        )

        if not content:
            continue

        memory_type = ensure_string(
            memory.get("type")
        )

        if memory_type not in MEMORY_TYPES:
            memory_type = "memory"

        age = ensure_int(
            memory.get("age"),
            0,
        )

        if age < 0:
            age = 0

        tags = ensure_list(
            memory.get("tags", [])
        )

        cleaned_tags = []

        for tag in tags:
            tag = ensure_string(tag)

            if tag:
                cleaned_tags.append(tag)

        memory["owner"] = owner
        memory["type"] = memory_type
        memory["content"] = content
        memory["age"] = age
        memory["tags"] = cleaned_tags

        valid_memories.append(memory)

    scene_result["memory_updates"] = valid_memories

    return scene_result


def clamp_memory_importance(
    scene_result: Dict[str, Any],
    min_value: int = 1,
    max_value: int = 10,
) -> Dict[str, Any]:
    """Valide et limite l'importance des souvenirs."""

    memory_updates = ensure_list(
        scene_result.get("memory_updates", [])
    )

    for memory in memory_updates:
        if not isinstance(memory, dict):
            continue

        importance = ensure_int(
            memory.get("importance"),
            min_value,
        )

        if importance < min_value:
            importance = min_value

        if importance > max_value:
            importance = max_value

        memory["importance"] = importance

    scene_result["memory_updates"] = memory_updates

    return scene_result


def validate_world_updates(
    scene_result: Dict[str, Any],
    world: Dict[str, Any],
) -> Dict[str, Any]:
    """Nettoie les world_updates invalides."""

    valid_location_ids = {
        location["id"]
        for location in world["locations"]
    }

    valid_character_ids = set(
        world["characters"]
    )

    player_character_id = world.get(
        "player_character",
        "",
    )

    world_updates = ensure_dict(
        scene_result.get(
            "world_updates",
            {},
        )
    )

    new_location = ensure_string(
        world_updates.get(
            "new_location",
            "",
        )
    )

    if new_location:
        if new_location not in valid_location_ids:
            new_location = ""

    world_updates["new_location"] = new_location

    time_advance_minutes = world_updates.get(
        "time_advance_minutes",
        0,
    )

    time_advance_minutes = ensure_int(time_advance_minutes)

    if time_advance_minutes < 0:
        time_advance_minutes = 0

    if time_advance_minutes > 180:
        time_advance_minutes = 180

    world_updates["time_advance_minutes"] = (
        time_advance_minutes
    )

    character_movements = ensure_dict(
        world_updates.get(
            "character_movements",
            {},
        )
    )

    cleaned_movements = {}

    for character_id, location_id in (
        character_movements.items()
    ):
        character_id = ensure_string(character_id)
        location_id = ensure_string(location_id)

        if character_id not in valid_character_ids:
            continue

        if character_id == player_character_id:
            continue

        if location_id not in valid_location_ids:
            continue

        cleaned_movements[
            character_id
        ] = location_id

    world_updates[
        "character_movements"
    ] = cleaned_movements

    scene_result[
        "world_updates"
    ] = world_updates

    return scene_result


def validate_scene_pacing(
    scene_result: Dict[str, Any],
) -> Dict[str, Any]:
    """Nettoie et limite une scene pour garder un rythme interactif."""

    narration = ensure_list(
        scene_result.get("narration", [])
    )

    dialogues = ensure_list(
        scene_result.get("dialogues", [])
    )

    valid_narration = []

    for paragraph in narration:
        if not isinstance(paragraph, str):
            continue

        paragraph = paragraph.strip()

        if not paragraph:
            continue

        valid_narration.append(paragraph)

    valid_dialogues = []

    for dialogue in dialogues:
        if not isinstance(dialogue, dict):
            continue

        speaker = dialogue.get("speaker")
        text = dialogue.get("text")

        if not isinstance(speaker, str):
            continue

        if not isinstance(text, str):
            continue

        speaker = speaker.strip()
        text = text.strip()

        if not speaker:
            continue

        if not text:
            continue

        dialogue["speaker"] = speaker
        dialogue["text"] = strip_enclosing_dialogue_quotes(text)
        valid_dialogues.append(dialogue)

    scene_result["narration"] = valid_narration[
        :MAX_NARRATION_PARAGRAPHS
    ]

    scene_result["dialogues"] = valid_dialogues[
        :MAX_DIALOGUES
    ]

    return scene_result


def strip_enclosing_dialogue_quotes(text: str) -> str:
    """Supprime uniquement les guillemets qui encadrent toute la replique."""

    quote_pairs = [
        ('"', '"'),
        ("'", "'"),
        ("“", "”"),
        ("‘", "’"),
        ("«", "»"),
    ]

    cleaned_text = text.strip()

    changed = True

    while changed and len(cleaned_text) >= 2:
        changed = False

        for opening_quote, closing_quote in quote_pairs:
            if cleaned_text.startswith(
                opening_quote
            ) and cleaned_text.endswith(closing_quote):
                cleaned_text = cleaned_text[
                    len(opening_quote) : -len(closing_quote)
                ].strip()
                changed = True
                break

    return cleaned_text


def normalize_text(value: str) -> str:
    """Normalise les accents et la casse pour les detections simples."""

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

    return normalized
