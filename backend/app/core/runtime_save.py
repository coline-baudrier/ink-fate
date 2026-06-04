"""Chargement et sauvegarde de l'etat runtime.

Les fichiers dans data/universes restent le canon de depart. L'etat qui bouge
pendant une partie est sauvegarde dans data/saves.
"""

from pathlib import Path
from typing import Any, Dict
import re
import shutil

from app.core.character_loader import load_characters, save_characters
from app.core.json_loader import load_json, save_json


DEFAULT_SAVE_ID = "default"


def build_runtime_save_path(
    project_root: Path,
    universe_id: str,
    save_id: str = DEFAULT_SAVE_ID,
) -> Path:
    """Retourne le dossier de sauvegarde runtime pour un univers."""

    return (
        Path(project_root)
        / "data"
        / "saves"
        / universe_id
        / normalize_save_id(save_id)
    )


def normalize_save_id(
    save_id: Any,
) -> str:
    """Normalise un identifiant de sauvegarde pour eviter les chemins ambigus."""

    if not isinstance(save_id, str):
        return DEFAULT_SAVE_ID

    normalized = save_id.strip()

    if not normalized:
        return DEFAULT_SAVE_ID

    normalized = re.sub(
        r"[^A-Za-z0-9_-]+",
        "-",
        normalized,
    )
    normalized = normalized.strip(
        "-_",
    )

    return normalized or DEFAULT_SAVE_ID


def get_runtime_world_path(
    runtime_save_path: Path,
) -> Path:
    """Retourne le chemin du world runtime."""

    return runtime_save_path / "world.json"


def get_runtime_characters_path(
    runtime_save_path: Path,
) -> Path:
    """Retourne le dossier des personnages runtime."""

    return runtime_save_path / "characters"


def load_runtime_world(
    canon_world_path: Path,
    runtime_save_path: Path,
) -> Dict[str, Any]:
    """Charge le world runtime s'il existe, sinon le world canon."""

    runtime_world_path = get_runtime_world_path(
        runtime_save_path,
    )

    if runtime_world_path.exists():
        return load_json(runtime_world_path)

    return load_json(canon_world_path)


def load_runtime_characters(
    canon_characters_path: Path,
    character_ids: list[str],
    runtime_save_path: Path,
) -> Dict[str, Dict[str, Any]]:
    """Charge les personnages runtime s'ils existent, sinon les personnages canon."""

    runtime_characters_path = get_runtime_characters_path(
        runtime_save_path,
    )

    if runtime_characters_path.exists():
        return load_characters(
            runtime_characters_path,
            character_ids,
        )

    return load_characters(
        canon_characters_path,
        character_ids,
    )


def save_runtime_state(
    runtime_save_path: Path,
    world: Dict[str, Any],
    characters: Dict[str, Dict[str, Any]],
) -> None:
    """Sauvegarde le world et les personnages dans le dossier runtime."""

    save_json(
        get_runtime_world_path(runtime_save_path),
        world,
    )

    save_characters(
        get_runtime_characters_path(runtime_save_path),
        characters,
    )


def clear_runtime_save(
    runtime_save_path: Path,
) -> None:
    """Supprime une sauvegarde runtime existante."""

    if runtime_save_path.exists():
        shutil.rmtree(runtime_save_path)
