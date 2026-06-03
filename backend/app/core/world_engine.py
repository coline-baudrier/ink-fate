"""Gestion simple du world state.

Le world state contient l'heure, la scene active et les informations globales
de l'univers. Ce module regroupe les petites operations qui modifient ou
rafraichissent cet etat.
"""

from pathlib import Path
from typing import Any, Dict

from app.core.json_loader import save_json
from app.core.scene_context import build_scene_context
from app.core.time_engine import advance_time


def update_world_after_scene(
    world: Dict[str, Any],
    minutes: int = 5,
) -> Dict[str, Any]:
    """Applique les changements simples du monde apres une scene."""

    world = advance_time(
        world,
        minutes,
    )

    return world


def save_world(
    world_path: Path,
    world: Dict[str, Any],
) -> None:
    """Sauvegarde le world state dans son fichier JSON."""

    save_json(
        world_path,
        world,
    )


def rebuild_scene_context(
    world: Dict[str, Any],
    characters: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """Reconstruit le contexte de scene apres modification du monde."""

    return build_scene_context(
        world,
        characters,
    )
