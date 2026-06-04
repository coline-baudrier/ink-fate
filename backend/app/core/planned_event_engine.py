"""Gestion MVP des evenements planifies.

Les planned_events representent des intentions concretes a venir
independamment du canal qui les a creees: dialogue en scene, SMS, etc.
"""

from typing import Any, Dict, List
import unicodedata


SKATING_LESSON_PLANNED_EVENT_ID = (
    "planned_skating_lesson_dean_elina_day2_0700"
)
SKATING_LESSON_PLANNED_EVENT_TRIGGER = "skating_lesson_planned_meeting"
SKATING_CONTEXT_KEYWORDS = [
    "patin",
    "patinoire",
    "skating",
    "rink",
    "hockey",
]
SKATING_TIME_KEYWORDS = [
    "7h",
    "07:00",
    "7:00",
    "demain",
    "tomorrow",
]


def append_planned_event(
    world: Dict[str, Any],
    planned_event: Dict[str, Any],
) -> Dict[str, Any]:
    """Ajoute un evenement planifie sans doublon exact."""

    if not isinstance(planned_event, dict):
        return world

    planned_event_id = planned_event.get(
        "id",
    )

    if not isinstance(planned_event_id, str) or not planned_event_id:
        return world

    planned_events = world.setdefault(
        "planned_events",
        [],
    )

    if not isinstance(planned_events, list):
        world["planned_events"] = []
        planned_events = world["planned_events"]

    for existing_event in planned_events:
        if not isinstance(existing_event, dict):
            continue

        if existing_event.get("id") == planned_event_id:
            return world

    planned_events.append(planned_event)

    return world


def build_skating_lesson_planned_event(
    world: Dict[str, Any],
    source: str,
) -> Dict[str, Any]:
    """Construit le rendez-vous patinoire Dean/Elina stable pour le MVP."""

    current_day = get_current_day(world)
    location_id = find_first_valid_location_id(
        world,
        [
            "ice_rink",
            "patinoire",
            "rink",
        ],
    )

    planned_event = {
        "id": SKATING_LESSON_PLANNED_EVENT_ID,
        "type": "planned_event",
        "trigger": SKATING_LESSON_PLANNED_EVENT_TRIGGER,
        "status": "scheduled",
        "participants": [
            "dean",
            "elina",
        ],
        "day": current_day + 1,
        "time": "07:00",
        "summary": (
            "Dean and Elina agreed to meet at the rink for a skating lesson."
        ),
        "source": source,
    }

    if location_id:
        planned_event["location"] = location_id

    return planned_event


def apply_planned_events_after_scene(
    world: Dict[str, Any],
    scene_result: Dict[str, Any],
) -> Dict[str, Any]:
    """Deduit des planned_events depuis une scene face-a-face."""

    if should_create_skating_lesson_from_scene(scene_result):
        world = append_planned_event(
            world,
            build_skating_lesson_planned_event(
                world,
                "scene",
            ),
        )

    return world


def should_create_skating_lesson_from_scene(
    scene_result: Dict[str, Any],
) -> bool:
    """Detecte une promesse concrete de patinoire dans un SceneResult."""

    context_text = normalize_text(
        " ".join(
            collect_scene_text(scene_result)
        )
    )

    if not context_text:
        return False

    has_skating_context = any(
        normalize_text(keyword) in context_text
        for keyword in SKATING_CONTEXT_KEYWORDS
    )
    has_time_context = any(
        normalize_text(keyword) in context_text
        for keyword in SKATING_TIME_KEYWORDS
    )
    has_core_participants = (
        "dean" in context_text
        and "elina" in context_text
    )

    return has_skating_context and has_time_context and has_core_participants


def build_planned_events_context(
    world: Dict[str, Any],
    max_events: int = 5,
) -> str:
    """Construit une section prompt lisible pour les rendez-vous prevus."""

    planned_events = world.get(
        "planned_events",
        [],
    )

    if not isinstance(planned_events, list) or not planned_events:
        return "No planned events yet."

    lines = []

    for event in planned_events[-max_events:]:
        if not isinstance(event, dict):
            continue

        if event.get("status") != "scheduled":
            continue

        day = event.get(
            "day",
            "?",
        )
        time = event.get(
            "time",
            "??:??",
        )
        location = event.get(
            "location",
            "",
        )
        summary = event.get(
            "summary",
            "",
        )
        participants = event.get(
            "participants",
            [],
        )

        if not isinstance(participants, list):
            participants = []

        participant_text = ", ".join(
            participant
            for participant in participants
            if isinstance(participant, str)
        )

        location_text = f", location {location}" if location else ""

        lines.append(
            f"- Day {day}, {time}{location_text} ({participant_text}): "
            f"{summary}"
        )

    if not lines:
        return "No planned events yet."

    return "\n".join(lines)


def collect_scene_text(
    scene_result: Dict[str, Any],
) -> List[str]:
    """Recupere les champs texte utiles du SceneResult."""

    texts: List[str] = []

    for field_name in [
        "narration",
    ]:
        values = scene_result.get(
            field_name,
            [],
        )

        if not isinstance(values, list):
            continue

        texts.extend(
            value
            for value in values
            if isinstance(value, str)
        )

    for field_name in [
        "dialogues",
        "events",
        "memory_updates",
        "actions",
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
                collect_dict_text(value)
            )

    return texts


def collect_dict_text(
    values: Dict[str, Any],
) -> List[str]:
    """Recupere recursivement les textes simples d'un dictionnaire."""

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
                collect_dict_text(value)
            )

    return texts


def find_first_valid_location_id(
    world: Dict[str, Any],
    candidates: List[str],
) -> str:
    """Retourne le premier lieu candidat present dans world.locations."""

    valid_location_ids = {
        location.get("id")
        for location in world.get(
            "locations",
            [],
        )
        if isinstance(location, dict)
        and isinstance(location.get("id"), str)
    }

    for candidate in candidates:
        if candidate in valid_location_ids:
            return candidate

    return ""


def get_current_day(
    world: Dict[str, Any],
) -> int:
    """Retourne le jour courant avec fallback stable."""

    timeline = world.get(
        "timeline",
        {},
    )

    if not isinstance(timeline, dict):
        return 1

    current_day = timeline.get(
        "current_day",
        1,
    )

    if isinstance(current_day, int) and not isinstance(current_day, bool):
        return current_day

    return 1


def normalize_text(value: str) -> str:
    """Normalise accents/casse pour la detection deterministe."""

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
