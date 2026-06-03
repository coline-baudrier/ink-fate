from pathlib import Path

from app.core.character_loader import load_characters
from app.core.json_loader import load_json
from app.core.openai_client import generate_text
from app.core.prompt_builder import build_structured_scene_prompt
from app.core.renderer import render_scene_result
from app.core.scene_context import build_scene_context
from app.core.scene_result_parser import parse_scene_result


PROJECT_ROOT = Path(__file__).resolve().parents[1]
UNIVERSE_PATH = PROJECT_ROOT / "data" / "universes" / "off-campus"


def main() -> None:
    # Charge l'etat du monde et les personnages de l'univers de test.
    world = load_json(UNIVERSE_PATH / "world.json")
    character_ids = world["characters"]

    characters = load_characters(
        UNIVERSE_PATH / "characters",
        character_ids,
    )

    # Construit les donnees utiles pour la scene active.
    scene_context = build_scene_context(
        world,
        characters,
    )

    prompt = build_structured_scene_prompt(
        world,
        scene_context,
    )

    scene_response = generate_text(prompt)
    scene_result = parse_scene_result(scene_response)
    rendered_scene = render_scene_result(scene_result)

    print("Ink & Fate")
    print("----------")
    print(f"Universe: {world['universe']['name']}")

    print()
    print("Loaded characters:")

    for character in characters.values():
        first_name = character["identity"]["first_name"]
        last_name = character["identity"]["last_name"]

        print(f"- {first_name} {last_name}")

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

    print()
    print("Generated prompt:")
    print("-----------------")
    print(prompt)

    print()
    print("Raw LLM response:")
    print("-----------------")
    print(scene_response)

    print()
    print("Parsed SceneResult:")
    print("-------------------")
    print(scene_result)

    print()
    print("Rendered scene:")
    print("---------------")
    print(rendered_scene)


if __name__ == "__main__":
    main()
