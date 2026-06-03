"""Construction du prompt envoye au LLM.

Le prompt explique au modele le contexte de la scene, l'action du joueur,
les regles narratives et le format JSON attendu.
"""

from typing import Any, Dict, List


def build_structured_scene_prompt(
    world: Dict[str, Any],
    scene_context: Dict[str, Any],
    player_input: str | None = None,
    scene_history: str | None = None,
) -> str:
    """
    Construit le prompt envoye au LLM pour generer une scene.

    Le resultat attendu n'est pas du texte libre, mais un JSON SceneResult.
    """

    universe_name = world["universe"]["name"]
    player_character_id = world["player_character"]

    location = scene_context["location"]
    location_name = location["name"]
    location_description = location["description"]

    date = scene_context["date"]
    time = scene_context["time"]

    participant_lines = build_participant_lines(scene_context)
    player_context = build_player_context(player_input)
    expected_json_format = build_expected_json_format()
    scene_history_context = build_scene_history_context(scene_history)
    memory_context = build_memory_context(scene_context)

    # Le prompt est volontairement separe en sections lisibles.
    prompt = f"""
You are the narrative engine of Ink & Fate.

Your job is to generate the next narrative scene.
You must return a structured JSON object, not prose outside JSON.

WORLD CONTEXT
- Universe: {universe_name}
- Date: {date}
- Time: {time}
- Location: {location_name}
- Location description: {location_description}

PLAYER CHARACTER
- The player controls: {player_character_id}
- Never write dialogue for the player character.
- Never decide the player character's thoughts, feelings or choices.
- You may only describe visible actions already implied by the player input.

ACTIVE PARTICIPANTS
{participant_lines}

SCENE HISTORY
{scene_history_context}

RELEVANT MEMORIES
{memory_context}

PLAYER INPUT
{player_context}

NARRATIVE RULES
- Write in French.
- Use a contemporary college romance tone.
- Keep characters emotionally believable.
- Keep dialogue natural and modern.
- Avoid cliches and overly dramatic narration.
- Do not invent important past events unless they are provided.
- Do not invent another university name.
- The story takes place at Briar University.
- If the player character directly addresses a character, that character should usually respond directly to the player character.
- Do not route every interaction through Beau.
- Dean may tease Beau, but he should also engage directly with Elina when she challenges him.
- Carefully track who the player is addressing.
- If the player mentions "tu", infer the addressed character from the previous sentence and scene context.
- Do not reinterpret the player's insult or challenge as targeting another character.
- When the player directly challenges Dean, Dean should respond directly.
- If the player directly addresses Dean, Dean must answer Elina directly.
- Do not redirect Dean's answer toward Beau unless the player explicitly mentions Beau.
- Dean can tease Beau briefly, but the main reaction must target Elina.
- Characters should remember emotionally or socially significant moments.
- When a player input creates emotional tension, intimacy, teasing or vulnerability, relationship_updates should reflect it.
- If Dean reacts positively to Elina, update dean -> elina accordingly.

CANON RULES
- Elina is arriving on campus with luggage.
- Beau is Elina's older brother.
- Dean is Beau's best friend.
- Dean initially wants to tease Beau, but once Elina challenges him, he becomes directly interested in her reactions.
- Dean should feel charismatic, teasing and socially confident.
- Beau should feel protective and used to Dean's behavior.

JSON RULES
- Return valid JSON only.
- Do not wrap the JSON in markdown.
- Do not add explanations before or after the JSON.
- Use character IDs for speakers, characters, sources, targets and participants.
- Never use full names inside JSON structures.
- Relationship changes must be small integers between -5 and 5.
- Use the location ID for scene.location.
- The player character ID is elina.
- Never include "elina" as a speaker in dialogues.
- Never generate dialogue for elina.
- If the player writes dialogue, treat it as already spoken by elina and only generate reactions from other characters.
- memory_updates must use character IDs.
- memory owner must be one of the active participants.
- importance must be an integer between 1 and 10.
- Only create memories for narratively meaningful moments.
- Do not create memories for every line of dialogue.

EXPECTED JSON FORMAT
{expected_json_format}
"""

    return prompt.strip()


def build_participant_lines(scene_context: Dict[str, Any]) -> str:
    """Construit la liste des personnages presents pour le prompt."""

    lines: List[str] = []

    for character in scene_context["participants"]:
        character_id = character["id"]
        first_name = character["identity"]["first_name"]
        last_name = character["identity"]["last_name"]

        lines.append(f"- {character_id} = {first_name} {last_name}")

    return "\n".join(lines)


def build_player_context(player_input: str | None) -> str:
    """Prepare la partie du prompt qui depend de l'action du joueur."""

    if player_input:
        return f"""
The player wrote:
{player_input}

Continue the scene from this input.
""".strip()

    return "This is the opening scene. Start the scene from the current context."


def build_expected_json_format() -> str:
    """Retourne le format JSON que le LLM doit respecter."""

    return """
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
  ],
  "memory_updates": [
    {
      "owner": "",
      "type": "",
      "content": "",
      "importance": 0,
      "age": 0,
      "tags": []
    }
  ]
}
""".strip()


def build_scene_history_context(scene_history: str | None) -> str:
    """Prepare l'historique de scene a envoyer au LLM."""

    if scene_history:
        return f"""
Previous scene :
{scene_history}
""".strip()

    return "No previous scene yet."

def build_memory_context(
    scene_context: Dict[str, Any],
) -> str:
    """
    Construit le contexte mémoire envoyé au LLM.
    """

    memory_lines = []

    for character in scene_context["participants"]:
        first_name = character["identity"]["first_name"]

        memories = character.get(
            "memories",
            [],
        )

        if not memories:
            continue

        memory_lines.append(
            f"{first_name} memories:"
        )

        sorted_memories = sorted(
            memories,
            key=lambda memory: memory.get(
                "importance",
                0,
            ),
            reverse=True,
        )

        top_memories = sorted_memories[:5]

        for memory in top_memories:
            content = memory.get(
                "content",
                "",
            )

            importance = memory.get(
                "importance",
                0,
            )

            memory_lines.append(
                f'- {content} '
                f'(importance: {importance})'
            )

        memory_lines.append("")

    if not memory_lines:
        return "No important memories yet."

    return "\n".join(memory_lines)