"""Point d'entree du prototype CLI Ink & Fate.

Ce fichier orchestre la boucle principale :
charger les donnees, generer une scene, lire l'action du joueur,
appliquer les relations et afficher le resultat.
"""

from pathlib import Path
from typing import Any, Dict

from app.core.character_loader import (
    load_characters,
    save_characters,
)
from app.core.json_loader import load_json
from app.core.openai_client import generate_text
from app.core.prompt_builder import build_structured_scene_prompt
from app.core.renderer import render_scene_result
from app.core.scene_context import build_scene_context
from app.core.scene_result_parser import parse_scene_result
from app.core.scene_validator import (
    clamp_relationship_updates,
    remove_invalid_actions,
    remove_invalid_dialogues,
    remove_invalid_events,
    remove_invalid_relationship_updates,
    remove_player_dialogues,
)
from app.core.relationship_engine import apply_relationship_updates


PROJECT_ROOT = Path(__file__).resolve().parents[1]
UNIVERSE_PATH = PROJECT_ROOT / "data" / "universes" / "off-campus"


def generate_scene(
    world: Dict[str, Any],
    scene_context: Dict[str, Any],
    player_input: str | None = None,
    scene_history: str | None = None,
) -> Dict[str, Any]:
    """Genere, parse et filtre une scene produite par le LLM."""

    prompt = build_structured_scene_prompt(
        world,
        scene_context,
        player_input,
        scene_history,
    )

    scene_response = generate_text(prompt)
    scene_result = parse_scene_result(scene_response)

    valid_character_ids = world["characters"]

    # Le validator nettoie les morceaux du JSON que le moteur ne doit pas accepter.
    scene_result = remove_invalid_dialogues(
        scene_result,
        valid_character_ids,
    )

    scene_result = remove_invalid_actions(
        scene_result,
        valid_character_ids,
    )

    scene_result = remove_invalid_events(
        scene_result,
        valid_character_ids,
    )

    scene_result = remove_invalid_relationship_updates(
        scene_result,
        valid_character_ids,
    )

    scene_result = remove_player_dialogues(
        scene_result,
        world["player_character"],
    )

    scene_result = clamp_relationship_updates(scene_result)

    return scene_result


def print_project_header(world: Dict[str, Any]) -> None:
    """Affiche le titre du projet et le nom de l'univers charge."""

    print("Ink & Fate")
    print("----------")
    print(f"Universe: {world['universe']['name']}")


def print_loaded_characters(
    characters: Dict[str, Dict[str, Any]],
) -> None:
    """Affiche les personnages charges au lancement."""

    print()
    print("Loaded characters:")

    for character in characters.values():
        first_name = character["identity"]["first_name"]
        last_name = character["identity"]["last_name"]

        print(f"- {first_name} {last_name}")


def print_active_scene(
    scene_context: Dict[str, Any],
) -> None:
    """Affiche les informations de la scene active."""

    print()
    print("Active scene:")
    print(f"- Location: {scene_context['location']['name']}")
    print(f"- Date: {scene_context['date']}")
    print(f"- Time: {scene_context['time']}")

    print()
    print("Participants:")

    for character in scene_context["participants"]:
        first_name = character["identity"]["first_name"]
        last_name = character["identity"]["last_name"]

        print(f"- {first_name} {last_name}")


def print_rendered_scene(
    title: str,
    scene_result: Dict[str, Any],
) -> None:
    """Affiche une scene deja transformee en texte lisible."""

    rendered_scene = render_scene_result(scene_result)

    print()
    print(title)
    print("-" * len(title))
    print(rendered_scene)


def main() -> None:
    """Lance le prototype CLI."""

    # Chargement initial : monde, personnages, puis contexte de scene.
    world = load_json(UNIVERSE_PATH / "world.json")
    character_ids = world["characters"]

    characters = load_characters(
        UNIVERSE_PATH / "characters",
        character_ids,
    )

    scene_context = build_scene_context(
        world,
        characters,
    )

    print_project_header(world)
    print_loaded_characters(characters)
    print_active_scene(scene_context)

    opening_scene = generate_scene(
        world,
        scene_context,
    )

    print_rendered_scene(
        "Opening scene",
        opening_scene,
    )

    scene_history = render_scene_result(opening_scene)

    while True:
        print()
        player_input = input("Your action > ")

        if player_input.lower() in ["quit", "exit"]:
            print("Fin de la session.")
            break

        next_scene = generate_scene(
            world,
            scene_context,
            player_input,
            scene_history,
        )

        characters = apply_relationship_updates(
            next_scene,
            characters,
        )

        # Les relations modifiees sont sauvegardees directement dans les JSON.
        save_characters(
            UNIVERSE_PATH / "characters",
            characters,
        )

        print()
        print("Updated relationships:")
        print("----------------------")

        for character_id, character in characters.items():
            print(character_id)

            relationships = character.get(
                "relationships",
                {}
            )

            print(relationships)
            print()

        print_rendered_scene(
            "Next scene",
            next_scene,
        )

        scene_history += "\n\n"
        scene_history += f"Player: {player_input}"
        scene_history += "\n\n"
        scene_history += render_scene_result(next_scene)


if __name__ == "__main__":
    main()
