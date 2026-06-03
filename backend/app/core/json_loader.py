import json
from pathlib import Path
from typing import Any


def load_json(path: str | Path) -> Any:
    """Charge un fichier JSON et retourne son contenu Python."""

    # Path permet de manipuler les chemins de facon propre et moderne.
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"JSON file not found: {file_path}")

    # L'encodage UTF-8 permet de lire correctement les accents dans les JSON.
    with file_path.open("r", encoding="utf-8") as file:
        # json.load transforme le JSON en dict/list Python.
        return json.load(file)


def save_json(path: str | Path, data: Any) -> None:
    """Sauvegarde des donnees Python dans un fichier JSON."""

    file_path = Path(path)

    # Cree automatiquement les dossiers parents s'ils n'existent pas.
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", encoding="utf-8") as file:
        # indent rend le JSON lisible, ensure_ascii=False garde les accents.
        json.dump(data, file, indent=2, ensure_ascii=False)
