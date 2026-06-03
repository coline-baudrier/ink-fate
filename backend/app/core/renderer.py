from typing import Any, Dict


def render_scene_result(scene_result: Dict[str, Any]) -> str:
    """Transforme un SceneResult en texte lisible pour le joueur."""

    output_lines = []

    narration_blocks = scene_result.get("narration", [])

    for narration in narration_blocks:
        output_lines.append(narration)
        output_lines.append("")

    dialogues = scene_result.get("dialogues", [])

    for dialogue in dialogues:
        speaker = dialogue.get("speaker", "Unknown")
        text = dialogue.get("text", "")

        output_lines.append(f"{speaker} : ")
        output_lines.append(f"« {text} »")
        output_lines.append("")

    return "\n".join(output_lines).strip()
