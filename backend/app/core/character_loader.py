"""Chargement et sauvegarde des personnages.

Chaque personnage est stocke dans un fichier JSON separe.
Ce module transforme les ids de personnages en fichiers a lire ou ecrire.
"""

from pathlib import Path
from typing import Any, Dict

from app.core.json_loader import load_json, save_json


def load_character(character_path: Path) -> Dict[str, Any]:
    """Charge un personnage depuis un fichier JSON."""

    return load_json(character_path)


def load_characters(
    characters_path: Path,
    character_ids: list[str],
) -> Dict[str, Dict[str, Any]]:
    """Charge plusieurs personnages a partir de leurs identifiants."""

    characters: Dict[str, Dict[str, Any]] = {}

    for character_id in character_ids:
        # Exemple : "dean" devient "dean.json".
        character_file = characters_path / f"{character_id}.json"
        character_data = load_character(character_file)

        characters[character_id] = character_data

    return characters


def save_characters(
    characters_path: Path,
    characters: Dict[str, Dict[str, Any]],
) -> None:
    """Sauvegarde tous les personnages dans leurs fichiers JSON."""

    for character_id, character_data in characters.items():
        # On sauvegarde chaque personnage dans son fichier d'origine.
        character_file = characters_path / f"{character_id}.json"

        save_json(
            character_file,
            character_data,
        )
