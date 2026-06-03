"""Rendu texte d'un SceneResult.

Le LLM renvoie un dictionnaire structure. Ce module transforme la narration
et les dialogues en texte simple affichable dans le terminal.
"""

from typing import Any, Dict


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
