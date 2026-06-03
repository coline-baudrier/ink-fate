"""Parsing du SceneResult renvoye par le LLM."""

import json
import re
from typing import Any, Dict


def extract_json_object(response_text: str) -> str:
    """Extrait le premier objet JSON probable depuis une reponse texte."""

    start_index = response_text.find("{")
    end_index = response_text.rfind("}")

    if start_index == -1 or end_index == -1:
        return ""

    if end_index <= start_index:
        return ""

    return response_text[start_index:end_index + 1]


def remove_trailing_commas(json_text: str) -> str:
    """Supprime les virgules finales avant } ou ]."""

    return re.sub(
        r",\s*([}\]])",
        r"\1",
        json_text,
    )


def build_fallback_scene_result() -> Dict[str, Any]:
    """Retourne une scene vide mais valide en cas d'erreur de parsing."""

    return {
        "scene": {
            "location": "",
            "time": "",
            "participants": [],
        },
        "narration": [
            "La scène marque une pause, le temps que chacun reprenne ses repères."
        ],
        "dialogues": [],
        "actions": [],
        "events": [],
        "relationship_updates": [],
        "memory_updates": [],
        "world_updates": {
            "new_location": "",
            "time_advance_minutes": 0,
            "character_movements": {},
        },
    }


def parse_scene_result(
    response_text: str,
) -> Dict[str, Any]:
    """Parse un SceneResult JSON avec quelques corrections simples."""

    json_text = extract_json_object(
        response_text,
    )

    if not json_text:
        return build_fallback_scene_result()

    cleaned_json_text = remove_trailing_commas(
        json_text,
    )

    try:
        parsed_result = json.loads(
            cleaned_json_text,
        )
    except json.JSONDecodeError:
        return build_fallback_scene_result()

    if not isinstance(parsed_result, dict):
        return build_fallback_scene_result()

    return parsed_result