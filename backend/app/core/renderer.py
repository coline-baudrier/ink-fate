"""Rendu texte d'un SceneResult.

Le LLM renvoie un dictionnaire structure. Ce module transforme la narration
et les dialogues en texte simple affichable dans le terminal.
"""

from typing import Any, Dict


def scene_result_to_entries(
    scene_result: Dict[str, Any],
    turn_id: str,
) -> list[Dict[str, Any]]:
    """Convertit un SceneResult en liste d'entries structurées pour l'API."""

    entries = []

    for i, paragraph in enumerate(scene_result.get("narration", [])):
        if not isinstance(paragraph, str) or not paragraph.strip():
            continue

        entries.append(
            {
                "id": f"{turn_id}_n{i}",
                "type": "narration",
                "character": None,
                "text": paragraph.strip(),
            }
        )

    for i, dialogue in enumerate(scene_result.get("dialogues", [])):
        if not isinstance(dialogue, dict):
            continue

        speaker = dialogue.get("speaker", "")
        text = dialogue.get("text", "")

        if not text:
            continue

        entries.append(
            {
                "id": f"{turn_id}_d{i}",
                "type": "dialogue",
                "character": speaker,
                "text": text,
            }
        )

    return entries


def render_scene_result(scene_result: Dict[str, Any]) -> str:
    """Transforme un SceneResult en texte lisible pour le joueur."""

    output_lines = []

    # La narration est affichee telle quelle, bloc par bloc.
    narration_blocks = scene_result.get("narration", [])

    for narration in narration_blocks:
        output_lines.append(narration)
        output_lines.append("")

    dialogues = scene_result.get("dialogues", [])

    for dialogue in dialogues:
        # Les dialogues ont deja ete filtres par le validator.
        speaker = dialogue.get("speaker", "Unknown")
        text = dialogue.get("text", "")

        output_lines.append(f"{speaker}:")
        output_lines.append(f'"{text}"')
        output_lines.append("")

    return "\n".join(output_lines).strip()
