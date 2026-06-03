from typing import Any, Dict


def build_structured_scene_prompt(
    world: Dict[str, Any],
    scene_context: Dict[str, Any],
) -> str:
    """
    Construit le prompt envoye au LLM pour generer une scene structuree.

    Le LLM doit retourner un objet JSON SceneResult exploitable par le moteur.
    """

    universe_name = world["universe"]["name"]

    location = scene_context["location"]
    location_name = location["name"]
    location_description = location["description"]

    date = scene_context["date"]
    time = scene_context["time"]

    participant_lines = []

    for character in scene_context["participants"]:
        character_id = character["id"]
        first_name = character["identity"]["first_name"]
        last_name = character["identity"]["last_name"]

        participant_lines.append(
            f"- {character_id} = {first_name} {last_name}"
        )

    # Ce bloc montre au LLM la structure JSON attendue.
    expected_json_format = """
{
  "scene": {
    "location": "",
    "time": "",
    "participants": []
  },
  "narration": [],
  "dialogues": [
    {
      "speaker": "",
      "text": ""
    }
  ],
  "actions": [
    {
      "character": "",
      "type": "",
      "target": ""
    }
  ],
  "events": [
    {
      "type": "",
      "participants": []
    }
  ],
  "relationship_updates": [
    {
      "source": "",
      "target": "",
      "changes": {
        "attraction": 0,
        "respect": 0
      }
    }
  ]
}
"""

    prompt = f"""
You are the narrative engine of Ink & Fate.

Universe: {universe_name}
Location: {location_name}
Location description: {location_description}
Date: {date}
Time: {time}

Active participants and IDs:
{chr(10).join(participant_lines)}

Generate a SceneResult JSON object.

Rules:
- Write in French.
- Use a contemporary college romance tone.
- Keep characters emotionally believable.
- Do not control the player character's thoughts or actions.
- Never narrate the player character's thoughts, feelings or decisions.
- The player character must remain fully controllable by the player.
- Only describe the player character's visible actions.
- Do not write dialogue for the player character.
- Always use character IDs in JSON fields.
- Never use full names inside JSON structures.

Canon and consistency rules:
- Do not invent another university name.
- The story takes place at Briar University.
- Do not invent past events unless explicitly provided.
- Elina is arriving on campus with luggage.
- Beau is Elina's older brother.
- Dean is Beau's best friend.
- Dean notices Elina and wants to tease Beau.
- Dean should feel charismatic, teasing and socially confident.
- Beau should feel protective and familiar with Dean's behavior.
- Keep dialogue natural and modern.
- Avoid cliches and overly dramatic narration.

JSON rules:
- You MUST return valid JSON only.
- Do not wrap the JSON in markdown.
- Do not add explanations before or after the JSON.
- Use character IDs for speakers, characters, sources, targets and participants.
- Use the location ID or location name consistently.
- Relationship changes must be small integers between -5 and 5.

Expected JSON format:
{expected_json_format}
"""

    return prompt.strip()
