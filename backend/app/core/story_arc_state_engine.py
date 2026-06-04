"""Etat runtime des arcs narratifs.

Ce module observe les scenes et SMS pour noter des signaux dramatiques deja
joues. Il ne choisit pas la prochaine scene et ne force aucune progression.
"""

from typing import Any, Dict, List, Set
import unicodedata


SIGNAL_TO_BEAT = {
    "playful_challenge_seen": "playful_challenge",
    "boundary_set_by_player": "boundary_set_by_player",
    "text_followup_seen": "text_followup",
    "missed_connection_seen": "missed_connection",
    "protective_interruption_seen": "protective_interruption",
    "unexpected_sincerity_seen": "unexpected_sincerity",
}

SIGNAL_KEYWORDS = {
    "playful_challenge_seen": [
        "defi",
        "challenge",
        "pari",
        "patin",
        "patinoire",
        "skating",
        "rink",
        "tenir debout",
    ],
    "boundary_set_by_player": [
        "limite",
        "boundary",
        "stop",
        "pas besoin",
        "laisse moi",
        "seule",
        "sans eux",
        "ne me suis pas",
        "je refuse",
    ],
    "missed_connection_seen": [
        "ignore",
        "ignored",
        "sans repondre",
        "ne repond pas",
        "no answer",
        "missed connection",
        "vu sans repondre",
    ],
    "protective_interruption_seen": [
        "beau intervient",
        "beau s'interpose",
        "beau la protege",
        "protective",
        "protection",
        "s'interpose",
    ],
    "unexpected_sincerity_seen": [
        "sincere",
        "sincerite",
        "sans blague",
        "serieusement",
        "vulnerable",
        "vulnerabilite",
        "pour une fois",
    ],
}

MESSAGE_TRIGGER_SIGNALS = {
    "skating_lesson_followup": [
        "text_followup_seen",
        "playful_challenge_seen",
    ],
    "skating_lesson_reply_confirmation": [
        "text_followup_seen",
    ],
    "beau_dormitory_checkin": [
        "text_followup_seen",
    ],
    "player_reply": [
        "text_followup_seen",
    ],
}


def apply_story_arc_state_after_scene(
    world: Dict[str, Any],
    scenario: Dict[str, Any] | None,
    scene_result: Dict[str, Any],
) -> Dict[str, Any]:
    """Observe une scene et note les signaux d'arcs actifs."""

    arc_definitions = get_active_story_arcs(scenario)

    if not arc_definitions:
        return world

    signals = detect_scene_arc_signals(scene_result)

    if not signals:
        return world

    involved_characters = collect_scene_character_ids(scene_result)

    for arc in arc_definitions:
        if not arc_overlaps_characters(
            arc,
            involved_characters,
        ):
            continue

        world = append_arc_signals(
            world,
            arc,
            signals,
        )

    return world


def apply_story_arc_state_from_messages(
    world: Dict[str, Any],
    messages: List[Dict[str, Any]],
    scenario: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Observe les SMS ajoutes et note les signaux d'arcs concernes."""

    if not messages:
        return world

    arc_definitions = get_active_story_arcs(scenario)

    if not arc_definitions:
        arc_definitions = get_fallback_arc_definitions(world)

    if not arc_definitions:
        return world

    for message in messages:
        if not isinstance(message, dict):
            continue

        signals = detect_message_arc_signals(message)

        if not signals:
            continue

        involved_characters = collect_message_character_ids(message)

        for arc in arc_definitions:
            if not arc_overlaps_characters(
                arc,
                involved_characters,
            ):
                continue

            world = append_arc_signals(
                world,
                arc,
                signals,
            )

    return world


def build_story_arc_state_context(
    world: Dict[str, Any],
    scenario: Dict[str, Any] | None = None,
) -> str:
    """Construit le contexte prompt des signaux d'arcs deja observes."""

    arc_state = world.get(
        "arc_state",
        {},
    )

    if not isinstance(arc_state, dict) or not arc_state:
        return "No observed arc state yet."

    arc_definitions = {
        arc["id"]: arc
        for arc in get_active_story_arcs(scenario)
        if isinstance(arc.get("id"), str)
    }

    lines = []

    for arc_id, state in arc_state.items():
        if not isinstance(arc_id, str) or not isinstance(state, dict):
            continue

        arc = arc_definitions.get(
            arc_id,
            {},
        )
        title = safe_string(
            arc.get("title"),
        )
        phase = safe_string(
            state.get("phase"),
        )
        played_beats = format_state_list(
            state.get("played_beats"),
        )
        signals = format_state_list(
            state.get("signals"),
        )

        lines.append(f"- Arc state: {arc_id}")

        if title:
            lines.append(f"  - Title: {title}")

        if phase:
            lines.append(f"  - Runtime phase: {phase}")

        if played_beats:
            lines.append(f"  - Played beats: {played_beats}")

        if signals:
            lines.append(f"  - Observed signals: {signals}")

    if not lines:
        return "No observed arc state yet."

    return "\n".join(lines)


def detect_scene_arc_signals(
    scene_result: Dict[str, Any],
) -> List[str]:
    """Detecte des signaux narratifs simples dans un SceneResult."""

    text = normalize_text(
        " ".join(
            collect_scene_text(scene_result)
        )
    )

    if not text:
        return []

    signals = []

    for signal, keywords in SIGNAL_KEYWORDS.items():
        if any(
            normalize_text(keyword) in text
            for keyword in keywords
        ):
            signals.append(signal)

    return signals


def detect_message_arc_signals(
    message: Dict[str, Any],
) -> List[str]:
    """Detecte des signaux narratifs simples dans un SMS."""

    trigger = message.get(
        "trigger",
        "",
    )
    signals = []

    if isinstance(trigger, str):
        signals.extend(
            MESSAGE_TRIGGER_SIGNALS.get(
                trigger,
                [],
            )
        )

    content = message.get(
        "content",
        "",
    )

    if isinstance(content, str):
        normalized_content = normalize_text(content)

        for signal, keywords in SIGNAL_KEYWORDS.items():
            if any(
                normalize_text(keyword) in normalized_content
                for keyword in keywords
            ):
                signals.append(signal)

    return unique_preserving_order(signals)


def append_arc_signals(
    world: Dict[str, Any],
    arc: Dict[str, Any],
    signals: List[str],
) -> Dict[str, Any]:
    """Ajoute des signaux et beats observes a world.arc_state."""

    arc_id = safe_string(
        arc.get("id"),
    )

    if not arc_id:
        return world

    arc_state = world.setdefault(
        "arc_state",
        {},
    )

    if not isinstance(arc_state, dict):
        world["arc_state"] = {}
        arc_state = world["arc_state"]

    state = arc_state.setdefault(
        arc_id,
        {
            "phase": safe_string(arc.get("phase")),
            "played_beats": [],
            "signals": [],
        },
    )

    if not isinstance(state, dict):
        state = {
            "phase": safe_string(arc.get("phase")),
            "played_beats": [],
            "signals": [],
        }
        arc_state[arc_id] = state

    state.setdefault(
        "phase",
        safe_string(arc.get("phase")),
    )
    state.setdefault(
        "played_beats",
        [],
    )
    state.setdefault(
        "signals",
        [],
    )

    if not isinstance(state["played_beats"], list):
        state["played_beats"] = []

    if not isinstance(state["signals"], list):
        state["signals"] = []

    for signal in unique_preserving_order(signals):
        append_unique_string(
            state["signals"],
            signal,
        )

        beat = SIGNAL_TO_BEAT.get(
            signal,
        )

        if beat:
            append_unique_string(
                state["played_beats"],
                beat,
            )

    timeline = world.get(
        "timeline",
        {},
    )

    if isinstance(timeline, dict):
        current_day = timeline.get(
            "current_day",
        )

        if isinstance(current_day, int) and not isinstance(current_day, bool):
            state["last_updated_day"] = current_day

    return world


def get_active_story_arcs(
    scenario: Dict[str, Any] | None,
) -> List[Dict[str, Any]]:
    """Retourne les arcs actifs du scenario."""

    if not isinstance(scenario, dict):
        return []

    story_arcs = scenario.get(
        "story_arcs",
        [],
    )

    if not isinstance(story_arcs, list):
        return []

    active_arcs = []

    for arc in story_arcs:
        if not isinstance(arc, dict):
            continue

        if not safe_string(arc.get("id")):
            continue

        status = safe_string(
            arc.get("status"),
        )

        if status and status != "active":
            continue

        active_arcs.append(arc)

    return active_arcs


def get_fallback_arc_definitions(
    world: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Construit des definitions minimales depuis un arc_state existant."""

    arc_state = world.get(
        "arc_state",
        {},
    )

    if not isinstance(arc_state, dict):
        return []

    return [
        {
            "id": arc_id,
            "participants": [],
        }
        for arc_id in arc_state
        if isinstance(arc_id, str) and arc_id
    ]


def arc_overlaps_characters(
    arc: Dict[str, Any],
    character_ids: Set[str],
) -> bool:
    """Verifie si un arc concerne au moins un personnage observe."""

    participants = arc.get(
        "participants",
        [],
    )

    if not isinstance(participants, list):
        return False

    participant_ids = {
        participant
        for participant in participants
        if isinstance(participant, str)
    }

    if not participant_ids:
        return True

    return bool(
        participant_ids.intersection(character_ids)
    )


def collect_scene_character_ids(
    scene_result: Dict[str, Any],
) -> Set[str]:
    """Recupere les IDs de personnages mentionnes par la scene."""

    character_ids: Set[str] = set()

    scene = scene_result.get(
        "scene",
        {},
    )

    if isinstance(scene, dict):
        participants = scene.get(
            "participants",
            [],
        )

        if isinstance(participants, list):
            character_ids.update(
                participant
                for participant in participants
                if isinstance(participant, str)
            )

    for field_name in [
        "dialogues",
        "events",
        "actions",
        "relationship_updates",
        "memory_updates",
    ]:
        values = scene_result.get(
            field_name,
            [],
        )

        if not isinstance(values, list):
            continue

        for value in values:
            if not isinstance(value, dict):
                continue

            character_ids.update(
                collect_character_ids_from_dict(value)
            )

    return character_ids


def collect_message_character_ids(
    message: Dict[str, Any],
) -> Set[str]:
    """Recupere les personnages d'un SMS."""

    character_ids = set()

    for key in [
        "from",
        "to",
    ]:
        value = message.get(key)

        if isinstance(value, str) and value:
            character_ids.add(value)

    return character_ids


def collect_character_ids_from_dict(
    values: Dict[str, Any],
) -> Set[str]:
    """Recupere les IDs simples d'un dictionnaire SceneResult."""

    character_ids: Set[str] = set()

    for key in [
        "speaker",
        "character",
        "source",
        "target",
        "owner",
    ]:
        value = values.get(key)

        if isinstance(value, str) and value:
            character_ids.add(value)

    participants = values.get(
        "participants",
        [],
    )

    if isinstance(participants, list):
        character_ids.update(
            participant
            for participant in participants
            if isinstance(participant, str)
        )

    return character_ids


def collect_scene_text(
    scene_result: Dict[str, Any],
) -> List[str]:
    """Recupere les textes utiles d'une scene."""

    texts: List[str] = []

    narration = scene_result.get(
        "narration",
        [],
    )

    if isinstance(narration, list):
        texts.extend(
            item
            for item in narration
            if isinstance(item, str)
        )

    for field_name in [
        "dialogues",
        "events",
        "actions",
        "memory_updates",
    ]:
        values = scene_result.get(
            field_name,
            [],
        )

        if not isinstance(values, list):
            continue

        for value in values:
            if not isinstance(value, dict):
                continue

            texts.extend(
                collect_text_from_dict(value)
            )

    return texts


def collect_text_from_dict(
    values: Dict[str, Any],
) -> List[str]:
    """Recupere recursivement les valeurs texte d'un dictionnaire."""

    texts: List[str] = []

    for value in values.values():
        if isinstance(value, str):
            texts.append(value)
        elif isinstance(value, list):
            texts.extend(
                item
                for item in value
                if isinstance(item, str)
            )
        elif isinstance(value, dict):
            texts.extend(
                collect_text_from_dict(value)
            )

    return texts


def append_unique_string(
    values: List[Any],
    new_value: str,
) -> None:
    """Ajoute new_value si absent."""

    if not isinstance(new_value, str) or not new_value:
        return

    if new_value not in values:
        values.append(new_value)


def unique_preserving_order(
    values: List[str],
) -> List[str]:
    """Dedoublonne une liste de chaines en gardant l'ordre."""

    unique_values = []

    for value in values:
        if not isinstance(value, str) or not value:
            continue

        if value not in unique_values:
            unique_values.append(value)

    return unique_values


def format_state_list(
    values: Any,
) -> str:
    """Formate une liste runtime de chaines."""

    if not isinstance(values, list):
        return ""

    cleaned_values = [
        value
        for value in values
        if isinstance(value, str) and value
    ]

    return "; ".join(cleaned_values)


def safe_string(
    value: Any,
) -> str:
    """Retourne une chaine nettoyee."""

    if not isinstance(value, str):
        return ""

    return value.strip()


def normalize_text(value: str) -> str:
    """Normalise accents/casse pour detection MVP."""

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
