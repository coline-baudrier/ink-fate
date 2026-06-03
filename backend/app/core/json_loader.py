# Import du module standard du Python qui permet de lire et écrire des JSONs
import json
# pathlib permet de manipuler le chemin des fichiers de manière propre et moderne
from pathlib import Path
# Any signifie : "ce type peut être n'importe quoi"
from typing import Any

# Fonction qui permet de charger les JSON
def load_json(path: str | Path) -> Any:
    # Converti le chemin reçu en objet Path pourvoir utiliser les méthodes pathlib
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"JSON file not found: {file_path}")
    
    # Ouvre le fichier en lecture ("r") avec encodage UTF-8
    with file_path.open("r", encoding="utf-8") as file:
        #json.load() transforme le JSON en dictionnaire/list Python
        return json.load(file)

# Fonction permettant de sauvegarder du JSON
def save_json(path: str | Path, data: Any) -> None:
    file_path = Path(path)
    # Crée automatiquement les dossiers parents s'ils n'existent pas
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Ouvre le fichier en écriture ("w")
    with file_path.open("w", encoding="utf-8") as file:
        # json.dump() écrit le dictionnaire Python dans le fichier JSON
        # Données à écrire : data, fichier cible : file, rend le json joli / lisible : indent=2, garde les accents correctement : enscure_ascii=False
        json.dump(data, file, indent=2, ensure_ascii=False)