"""Fonctions utilitaires pour lire et ecrire des fichiers JSON.

Dans ce projet, les mondes et les personnages sont stockes en JSON.
Ce module evite de repeter le meme code d'ouverture de fichier partout.
"""

import json
from pathlib import Path
from typing import Any


def load_json(path: str | Path) -> Any:
    """Charge un fichier JSON et retourne son contenu Python."""

    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"JSON file not found: {file_path}")

    with file_path.open("r", encoding="utf-8") as file:
        # json.load transforme le texte JSON en objets Python.
        return json.load(file)


def save_json(path: str | Path, data: Any) -> None:
    """Sauvegarde des donnees Python dans un fichier JSON."""

    file_path = Path(path)

    # Cree le dossier parent si on sauvegarde dans un dossier encore absent.
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", encoding="utf-8") as file:
        # indent rend le JSON lisible, ensure_ascii=False garde les accents.
        json.dump(data, file, indent=2, ensure_ascii=False)
