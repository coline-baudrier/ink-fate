from pathlib import Path
# Permet d'indiquer qu'une fonction retourne un dictionnaire
from typing import Dict, Any
from app.core.json_loader import load_json

# Fonction permettant de charger un seul personnage
def load_character(character_path: Path) -> Dict[str, Any]:
    return load_json(character_path)

# Fonction permettant de charger plusieurs personnages
def load_characters(characters_path: Path, character_ids: list[str]) -> Dict[str, Dict[str, Any]]:

    # Dictionnaire final avec tous les personnages
    characters = {}

    # Boucle sur chaque id
    for character_id in character_ids:
        character_file = (characters_path / f"{character_id}.json")
        character_data = load_character(character_file)

        # Stocke le personnage dans le dictionnaire
        characters[character_id] = (character_data)
    
    return characters