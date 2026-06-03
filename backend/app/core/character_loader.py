from pathlib import Path
from typing import Any, Dict

from app.core.json_loader import load_json


def load_character(character_path: Path) -> Dict[str, Any]:
    """Charge un personnage depuis un fichier JSON."""

    return load_json(character_path)


def load_characters(
    characters_path: Path,
    character_ids: list[str],
) -> Dict[str, Dict[str, Any]]:
    """Charge plusieurs personnages a partir de leurs identifiants."""

    characters: Dict[str, Dict[str, Any]] = {}

    # Chaque identifiant correspond a un fichier JSON du meme nom.
    for character_id in character_ids:
        character_file = characters_path / f"{character_id}.json"
        character_data = load_character(character_file)

        characters[character_id] = character_data

    return characters
