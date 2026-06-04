"""Construction du contexte d'arcs narratifs.

Les arcs sont une boussole dramatique: ils proposent des tensions, questions
et beats possibles sans forcer l'ordre ou l'issue de l'histoire.
"""

from typing import Any, Dict, List


def build_story_arcs_context(
    scenario: Dict[str, Any],
) -> str:
    """Construit une section prompt compacte depuis scenario.story_arcs."""

    story_arcs = scenario.get(
        "story_arcs",
        [],
    )

    if not isinstance(story_arcs, list) or not story_arcs:
        return "No active story arcs defined."

    arc_sections = []

    for arc in story_arcs:
        if not isinstance(arc, dict):
            continue

        if arc.get("status") not in [
            None,
            "",
            "active",
        ]:
            continue

        arc_section = build_story_arc_section(arc)

        if arc_section:
            arc_sections.append(arc_section)

    if not arc_sections:
        return "No active story arcs defined."

    return "\n\n".join(arc_sections)


def build_story_arc_section(
    arc: Dict[str, Any],
) -> str:
    """Formate un arc narratif individuel."""

    arc_id = safe_string(
        arc.get("id"),
    )

    if not arc_id:
        return ""

    title = safe_string(
        arc.get("title"),
    )
    phase = safe_string(
        arc.get("phase"),
    )

    lines = [
        f"- Arc: {arc_id}",
    ]

    if title:
        lines.append(f"  - Title: {title}")

    if phase:
        lines.append(f"  - Current phase: {phase}")

    append_optional_list_line(
        lines,
        "Participants",
        arc.get("participants"),
    )
    append_optional_list_line(
        lines,
        "Dramatic questions",
        arc.get("dramatic_questions"),
    )
    append_optional_list_line(
        lines,
        "Current tensions",
        arc.get("current_tensions"),
    )
    append_optional_list_line(
        lines,
        "Available beats",
        arc.get("available_beats"),
    )
    append_optional_list_line(
        lines,
        "Blocked beats",
        arc.get("blocked_beats"),
    )
    append_optional_list_line(
        lines,
        "Progress signals",
        arc.get("progress_signals"),
    )
    append_optional_list_line(
        lines,
        "Branching notes",
        arc.get("branching_notes"),
    )

    return "\n".join(lines)


def append_optional_list_line(
    lines: List[str],
    label: str,
    values: Any,
) -> None:
    """Ajoute une ligne si values est une liste non vide de textes."""

    formatted_values = format_list_values(values)

    if formatted_values:
        lines.append(f"  - {label}: {formatted_values}")


def format_list_values(
    values: Any,
) -> str:
    """Formate une liste de chaines de facon compacte."""

    if not isinstance(values, list):
        return ""

    cleaned_values = [
        value.strip()
        for value in values
        if isinstance(value, str) and value.strip()
    ]

    return "; ".join(cleaned_values)


def safe_string(
    value: Any,
) -> str:
    """Retourne value nettoyee si c'est une chaine."""

    if not isinstance(value, str):
        return ""

    return value.strip()
