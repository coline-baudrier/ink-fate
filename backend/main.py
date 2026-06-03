from pathlib import Path
# Importe notre fonction custom load_json
from app.core.json_loader import load_json
# Import notre fonction de chargement des personnages
from app.core.character_loader import load_characters
from app.core.scene_context import build_scene_context
from app.core.prompt_builder import build_initial_scene_prompt

PROJECT_ROOT = Path(__file__).resolve().parents[1]
UNIVERSE_PATH = PROJECT_ROOT / "data" / "universes" / "off-campus"

# Fonction principale du programme
def main() -> None:
    # Charge le fichier de monde
    world = load_json(UNIVERSE_PATH / "world.json")

    # Récupération des ids des personnages
    character_ids = world["characters"]
    # Charge tous les personnages
    characters = load_characters(UNIVERSE_PATH / "characters", character_ids)
    # Charge la scène active
    scene_context = build_scene_context(world, characters)
    # Charge le prompt builder
    prompt = build_initial_scene_prompt(world, scene_context)

    print("Ink & Fate")
    print("----------")
    print(f"Universe: {world['universe']['name']}")

    print()

    print("Loaded characters : ")
    # Boucle sur les personnages chargés
    for character in characters.values():
        first_name = (character["identity"]["first_name"])
        last_name = (character["identity"]["last_name"])

        print(f"- {first_name} {last_name}")

    print()

    print("Active scene:")
    print(f"- Location: {scene_context['location']}")
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

if __name__ == "__main__":
    main()