from typing import Any, Dict

# Fonction pour construire le prompt de génération de la scène initiale
# Pour le moment il retourne du texte simple, ensuite il demandera au LLM de retourne un SceneResult JSON
def build_initial_scene_prompt(
        world: Dict[str, Any],
        scene_context: Dict[str, Any]
) -> str:
    
    universe_name = world["universe"]["name"]
    location = scene_context["location"]
    date = scene_context["date"]
    time = scene_context["time"]

    participant_names = []

    for character in scene_context["participants"]:
        first_name = character["identity"]["first_name"]
        last_name = character["identity"]["last_name"]

        participant_names.append(
            f"{first_name} {last_name}"
        )

    prompt = f"""
You are the narrative engine of Ink & Fate.

Universe: {universe_name}
Location: {location}
Date: {date}
Time: {time}

Active participants:
{chr(10).join(f"- {name}" for name in participant_names)}

Write the opening scene of this interactive novel.

Rules:
- Write in French.
- Use a contemporary college romance tone.
- Keep characters emotionally believable.
- Do not control the player character's thoughts or actions.
- End with a natural moment where the player can respond.
"""
    
    return prompt.strip()