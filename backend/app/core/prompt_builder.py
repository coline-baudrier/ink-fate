"""Construction du prompt envoye au LLM.

Le prompt explique au modele le contexte de la scene, l'action du joueur,
les regles narratives et le format JSON attendu.
"""

from typing import Any, Dict, List
from app.core.contact_engine import build_contact_context
from app.core.memory_retriever import select_relevant_memories
from app.core.planned_event_engine import build_planned_events_context
from app.core.relationship_stages import build_relationship_context
from app.core.runtime_directives import build_runtime_directives_context
from app.core.story_arc_state_engine import build_story_arc_state_context
from app.core.story_arc_engine import build_story_arcs_context


def build_structured_scene_prompt(
    world: Dict[str, Any],
    scenario: Dict[str, Any],
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

    participant_context = dict(scene_context)
    participant_context["player_character"] = player_character_id
    participant_lines = build_participant_lines(participant_context)
    player_context = build_player_context(player_input)
    expected_json_format = build_expected_json_format()
    scene_history_context = build_scene_history_context(scene_history)
    memory_context = build_memory_context(
        scene_context,
        player_input,
        scene_history,
    )
    available_locations = build_available_locations(world)
    event_log_context = build_event_log_context(world)
    planned_events_context = build_planned_events_context(world)
    scenario_context = build_scenario_context(scenario)
    story_arcs_context = build_story_arcs_context(scenario)
    story_arc_state_context = build_story_arc_state_context(world, scenario)
    relationship_context = build_relationship_context(scene_context)
    contact_context = build_contact_context(scene_context)
    player_intent_context = build_player_intent_context(scene_context)
    contact_intent_context = build_contact_intent_context(scene_context)
    runtime_directives_context = build_runtime_directives_context(world)

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

AVAILABLE LOCATIONS
{available_locations}

PLAYER CHARACTER
- The player controls: {player_character_id}
- Never write dialogue for the player character.
- Never decide the player character's thoughts, feelings or choices.
- You may only describe visible actions already implied by the player input.
- Do not describe the player character as feeling excited, nervous, afraid, attracted, relieved or any other internal emotion unless the player explicitly wrote it.

ACTIVE PARTICIPANTS
{participant_lines}
- Only the character IDs listed above are physically present in the current active scene.
- Scene history may mention other characters, but they are not present now unless they are listed above or world_updates.character_movements explicitly moves them into the current location.
- Do not describe absent NPCs as nearby, watching, smiling, speaking, reacting, leaning on a wall, following, or otherwise physically present.
- scene.participants and dialogues.speaker must stay limited to current active participants, except for NPCs explicitly moved into the scene by character_movements.

SCENE HISTORY
{scene_history_context}

RECENT EVENTS
{event_log_context}

PLANNED EVENTS
{planned_events_context}

RELEVANT MEMORIES
{memory_context}

RELATIONSHIP STATUS
{relationship_context}

CONTACT ACCESS
{contact_context}

PLAYER INPUT
{player_context}

PLAYER INTENT HINTS
{player_intent_context}

CONTACT INTENT HINTS
{contact_intent_context}

SCENARIO CONTEXT
{scenario_context}

STORY ARCS
{story_arcs_context}
- Story arcs are dramatic guidance, not a fixed script.
- Available beats are opportunities, not obligations.
- Do not force a beat if the player's action points elsewhere.
- The player may reject, delay, redirect or break an arc.
- Respect blocked beats unless the story state and relationship context clearly justify unlocking them later.
- Never force a couple outcome; romance can progress, stall, branch, or fail.

OBSERVED ARC STATE
{story_arc_state_context}
- Observed arc state is memory of what already happened, not an order to repeat it.
- Avoid repeating the same beat unless the player reopens it or the context changes meaningfully.
- Use observed refusals, boundaries, missed connections and follow-ups as consequences.

RUNTIME GM DIRECTIVES
{runtime_directives_context}
- These directives are out-of-character author guidance for this runtime save.
- Follow them when they do not conflict with JSON rules, player agency, safety, canon or validator constraints.
- Runtime directives cannot override the rule that the model must never write dialogue, thoughts or decisions for the player character.

NPC AUTONOMY RULES
- Non-player characters must not only answer the player's latest input.
- Each non-player character should actively pursue their own goals, desires, fears and relationships.
- Non-player characters may initiate actions, invitations, tension, jokes, light conflicts or changes in the dynamic.
- Keep every non-player character coherent with their personality, their relationship to the player and the scene context.
- Do not fully resolve the scene if the player can still respond.
- Create a concrete narrative opening for the player to answer.
- If a non-player character stays silent, they should still have an observable presence when their reaction matters.
- Never write dialogue, thoughts or decisions for the player character.
- When the player character leaves a group, the next active scene follows the player character, not the NPCs left behind.
- Do not continue NPC-only scenes unless explicitly requested by the system.

SCENE DIRECTION
- The player_input is a trigger, not the whole scene.
- Move the scene forward through a mix of reaction, non-player character initiative and consequence.
- Favor concrete micro-actions: a look, a gesture, a movement, a decision, an invitation or a moment of tension.
- Avoid generic responses like "I will call you soon" when a character can propose something more specific and embodied.
- Generate a scene that makes the player want to answer immediately.
- If player_input is empty during an ongoing scene, treat it as the player waiting or observing briefly, not as permission to shift focus away from the player.

JSON RULES
- Return valid JSON only.
- Do not wrap the JSON in markdown.
- Do not add explanations before or after the JSON.
- Use character IDs for speakers, characters, sources, targets and participants.
- Never use full names inside JSON structures.
- Relationship changes must be small integers between -5 and 5.
- Existing contact access controls whether characters can text, call, or DM each other outside the current in-person scene.
- Do not make a character text, call, or DM another character unless contact access already allows it, or the current scene clearly creates that access first.
- Use contact_updates when characters exchange phone numbers, get someone's phone number through a third party, connect on Instagram, accept a follow request, or otherwise gain communication access.
- Use phone_number_known true when source gets target's phone number without necessarily giving theirs back.
- Use phone_numbers_exchanged true only when both characters have each other's phone number.
- Use instagram_connected true only for a mutual Instagram connection in this MVP.
- Do not add contact_updates just because characters talk in person.
- dialogue.text must contain only the spoken words, without enclosing quotation marks.
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
- world_updates.new_location must be empty unless the player clearly moves to another location.
- If the player clearly leaves, walks toward, enters, or moves to a valid available location, set world_updates.new_location to that location ID.
- world_updates.new_location must use a valid location ID.
- world_updates.character_movements must map character IDs to valid location IDs.
- Only include character_movements when a non-player character clearly moves, follows, leaves, or stays behind.
- Do not move uninvolved characters.
- If no non-player character moves, use an empty object.
- If no location change happens, use an empty string.
- Keep narration concise: 1 to 3 narration paragraphs.
- Generate 1 to 4 dialogue lines maximum.
- Prefer fewer dialogue lines, but allow an extra line when it creates stronger character initiative or tension.
- At least one non-player character should usually take a concrete initiative when the player input creates an opportunity.
- Do not end the scene with a full resolution if the player can still respond.

EXPECTED JSON FORMAT
{expected_json_format}
"""

    return prompt.strip()


def build_participant_lines(scene_context: Dict[str, Any]) -> str:
    """Construit la liste des personnages presents pour le prompt."""

    lines: List[str] = []
    participants = scene_context.get(
        "participants",
        [],
    )

    if not isinstance(participants, list):
        return ""

    participant_ids = [
        participant.get("id", "")
        for participant in participants
        if isinstance(participant, dict)
    ]
    player_character_id = scene_context.get(
        "player_character",
        "elina",
    )

    for character in participants:
        if not isinstance(character, dict):
            continue

        character_id = character.get(
            "id",
            "unknown",
        )
        identity = character.get(
            "identity",
            {},
        )

        lines.append(
            f"- {character_id} = {format_identity(identity)}"
        )
        lines.extend(
            build_character_detail_lines(
                character,
                participant_ids,
                player_character_id,
            )
        )

    return "\n".join(lines)


def format_identity(identity: Any) -> str:
    """Retourne une identite compacte sans inventer de champs."""

    if not isinstance(identity, dict):
        return "Unknown character"

    name_parts = [
        identity.get("first_name", ""),
        identity.get("middle_name", ""),
        identity.get("last_name", ""),
    ]
    full_name = " ".join(
        part
        for part in name_parts
        if isinstance(part, str) and part.strip()
    )

    if not full_name:
        full_name = "Unknown character"

    age = identity.get("age")

    if isinstance(age, int) and not isinstance(age, bool):
        return f"{full_name}, {age}"

    return full_name


def format_list_values(values: Any) -> str:
    """Transforme une liste de valeurs simples en texte court."""

    if not isinstance(values, list):
        return ""

    cleaned_values = [
        value
        for value in values
        if isinstance(value, str) and value.strip()
    ]

    return ", ".join(cleaned_values)


def format_dict_values(values: Any) -> str:
    """Transforme un dictionnaire simple en paires compactes."""

    if not isinstance(values, dict):
        return ""

    pairs = []

    for key, value in values.items():
        if not isinstance(key, str) or not key.strip():
            continue

        if isinstance(value, bool):
            continue

        if isinstance(value, (int, float, str)):
            pairs.append(f"{key}: {value}")

    return ", ".join(pairs)


def append_optional_line(
    lines: List[str],
    label: str,
    value: str,
) -> None:
    """Ajoute une ligne detaillee seulement si elle contient des donnees."""

    if value:
        lines.append(f"  - {label}: {value}")


def build_character_detail_lines(
    character: Dict[str, Any],
    participant_ids: List[str],
    player_character_id: str,
) -> List[str]:
    """Construit les details narratifs utiles d'un participant."""

    lines: List[str] = []

    archetype = character.get(
        "archetype",
        "",
    )

    if isinstance(archetype, str) and archetype.strip():
        append_optional_line(lines, "Archetype", archetype)

    append_optional_line(
        lines,
        "Personality / traits",
        format_dict_values(character.get("personality")),
    )
    append_optional_line(
        lines,
        "Speech style",
        format_list_values(character.get("speech_style"))
        or format_dict_values(character.get("speech_style"))
        or safe_string(character.get("speech_style"))
        or format_list_values(character.get("speaking_style"))
        or format_dict_values(character.get("speaking_style"))
        or safe_string(character.get("speaking_style"))
        or format_list_values(character.get("dialogue_style"))
        or format_dict_values(character.get("dialogue_style"))
        or safe_string(character.get("dialogue_style"))
        or safe_string(character.get("voice")),
    )
    append_optional_line(
        lines,
        "Current emotional state",
        safe_string(character.get("current_emotional_state"))
        or format_dict_values(character.get("current_emotional_state"))
        or safe_string(character.get("emotional_state"))
        or format_dict_values(character.get("emotional_state"))
        or safe_string(character.get("mood")),
    )
    append_optional_line(
        lines,
        "Current goals",
        format_list_values(character.get("current_goals")),
    )
    append_optional_line(
        lines,
        "Desires / motivations",
        format_list_values(character.get("desires"))
        or format_list_values(character.get("motivations"))
        or format_list_values(character.get("goals")),
    )
    append_optional_line(
        lines,
        "Fears",
        format_list_values(character.get("fears")),
    )
    append_optional_line(
        lines,
        "Narrative limits / taboos",
        format_list_values(character.get("narrative_limits"))
        or format_list_values(character.get("limits"))
        or format_list_values(character.get("taboos"))
        or format_list_values(character.get("boundaries")),
    )

    relationship_lines = build_character_relationship_lines(
        character,
        participant_ids,
        player_character_id,
    )

    lines.extend(relationship_lines)

    return lines


def safe_string(value: Any) -> str:
    """Retourne une chaine propre si la valeur est deja textuelle."""

    if not isinstance(value, str):
        return ""

    return value.strip()


def build_character_relationship_lines(
    character: Dict[str, Any],
    participant_ids: List[str],
    player_character_id: str,
) -> List[str]:
    """Resume les relations du personnage avec la scene active."""

    character_id = character.get(
        "id",
        "",
    )
    relationships = character.get(
        "relationships",
        {},
    )

    if not isinstance(relationships, dict):
        return []

    lines: List[str] = []
    important_relationships = []

    for target_id in participant_ids:
        if target_id == character_id:
            continue

        relationship = relationships.get(target_id)
        relationship_text = format_dict_values(relationship)

        if relationship_text:
            important_relationships.append(
                f"{target_id} ({relationship_text})"
            )

    if important_relationships:
        lines.append(
            "  - Important relationships in scene: "
            + "; ".join(important_relationships)
        )

    player_relationship = relationships.get(player_character_id)
    player_relationship_text = format_dict_values(player_relationship)

    if player_relationship_text and character_id != player_character_id:
        lines.append(
            f"  - Attitude toward player ({player_character_id}): "
            f"{player_relationship_text}"
        )

    return lines


def build_player_context(player_input: str | None) -> str:
    """Prepare la partie du prompt qui depend de l'action du joueur."""

    if player_input is None:
        return "This is the opening scene. Start the scene from the current context."

    player_input = player_input.strip()

    if player_input:
        return f"""
The player wrote:
{player_input}

Continue the scene from this input.
""".strip()

    return """
The player did not enter a new action.
Treat this as: wait and observe briefly.
Keep the scene centered on the player character and the current active location.
""".strip()


def build_player_intent_context(scene_context: Dict[str, Any]) -> str:
    """Prepare les indices deterministes d'intention joueur pour le LLM."""

    player_intent_hints = scene_context.get(
        "player_intent_hints",
        {},
    )

    if not isinstance(player_intent_hints, dict):
        return "No explicit player movement detected."

    detected_movement = player_intent_hints.get(
        "detected_movement",
    )

    if not isinstance(detected_movement, str) or not detected_movement:
        return "No explicit player movement detected."

    lines = [
        (
            "The player input clearly indicates movement to location: "
            f"{detected_movement}."
        ),
        (
            "The generated SceneResult must set "
            f'world_updates.new_location to "{detected_movement}".'
        ),
        (
            "The next scene should follow the player character at that "
            "location unless an NPC explicitly follows."
        ),
    ]

    if player_intent_hints.get("leaves_npcs_behind") is True:
        lines.extend(
            [
                "The player explicitly leaves the NPCs behind.",
                (
                    "Do not move NPCs with the player unless the player "
                    "explicitly invites them or a strong immediate "
                    "interruption prevents the departure."
                ),
                (
                    "The next active scene should include the player "
                    "character at the new location, usually without the "
                    "NPCs left behind."
                ),
                (
                    "NPCs left behind may have at most one brief departure "
                    "reaction. Do not continue a back-and-forth conversation "
                    "between NPCs after the player has left."
                ),
            ]
        )

    return "\n".join(lines)


def build_contact_intent_context(scene_context: Dict[str, Any]) -> str:
    """Prepare les indices deterministes de contact pour le LLM."""

    contact_intent_hints = scene_context.get(
        "contact_intent_hints",
        {},
    )

    if not isinstance(contact_intent_hints, dict):
        return "No explicit player contact intent detected."

    recipient_id = contact_intent_hints.get(
        "phone_number_given_to",
    )

    if not isinstance(recipient_id, str) or not recipient_id:
        return "No explicit player contact intent detected."

    return f"""
The player explicitly gives their phone number to: {recipient_id}.
The generated SceneResult must include contact_updates with source "{recipient_id}", target "elina", and phone_number_known true.
The source is the character who gains access to the number, not the character who gives it.
""".strip()


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
  "contact_updates": [
    {
      "source": "",
      "target": "",
      "changes": {
        "phone_number_known": false,
        "phone_numbers_exchanged": false,
        "instagram_connected": false
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
  ],
  "world_updates": {
    "new_location": "",
    "time_advance_minutes": 0,
    "character_movements": {
        "character_id": "location_id"
    }
  }
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
    player_input: str | None = None,
    scene_history: str | None = None,
) -> str:
    """Construit le contexte memoire envoye au LLM."""

    relevant_memories = select_relevant_memories(
        scene_context,
        player_input,
        scene_history,
    )

    if not relevant_memories:
        return "No important memories yet."

    memory_lines = []

    for character_id, memories in relevant_memories.items():
        memory_lines.append(
            f"{character_id} memories:"
        )

        for memory in memories:
            content = memory.get("content", "")
            importance = memory.get("importance", 0)
            age = memory.get("age", 0)

            memory_lines.append(
                f"- {content} "
                f"(importance: {importance}, age: {age})"
            )

        memory_lines.append("")

    return "\n".join(memory_lines)


def build_event_log_context(
    world: Dict[str, Any],
    max_events: int = 5,
) -> str:
    """Construit le resume des derniers evenements importants."""

    event_log = world.get(
        "event_log",
        [],
    )

    if not isinstance(event_log, list) or not event_log:
        return "No important events recorded yet."

    event_lines = []
    recent_events = event_log[-max_events:]

    for event in recent_events:
        if not isinstance(event, dict):
            continue

        day = event.get(
            "day",
            "?",
        )

        time = event.get(
            "time",
            "??:??",
        )

        event_type = event.get(
            "type",
            "event",
        )

        summary = event.get(
            "summary",
            "",
        )

        participants = event.get(
            "participants",
            [],
        )

        if not isinstance(participants, list):
            participants = []

        participant_text = ", ".join(participants)

        if participant_text:
            event_lines.append(
                f"- Day {day}, {time}, {event_type} "
                f"({participant_text}): {summary}"
            )
        else:
            event_lines.append(
                f"- Day {day}, {time}, {event_type}: {summary}"
            )

    if not event_lines:
        return "No important events recorded yet."

    return "\n".join(event_lines)


def build_available_locations(world: Dict[str, Any]) -> str:
    """Construit la liste des lieux disponibles."""

    lines = []

    for location in world["locations"]:
        location_id = location["id"]
        location_name = location["name"]

        lines.append(f"- {location_id} = {location_name}")

    return "\n".join(lines)


def build_list_lines(
    title: str,
    items: Any,
) -> List[str]:
    """Transforme une liste de textes en section lisible."""

    lines = [
        f"{title}:",
    ]

    if not isinstance(items, list):
        return lines

    for item in items:
        if isinstance(item, str) and item.strip():
            lines.append(f"- {item}")

    return lines


def build_scenario_context(
    scenario: Dict[str, Any],
) -> str:
    """Construit le contexte narratif du scenario."""

    title = scenario.get(
        "title",
        "Unknown Scenario",
    )

    premise = scenario.get(
        "premise",
        "",
    )

    tone = scenario.get(
        "tone",
        [],
    )

    canon_rules = scenario.get(
        "canon_rules",
        [],
    )

    character_dynamics = scenario.get(
        "character_dynamics",
        [],
    )

    pacing_rules = scenario.get(
        "pacing_rules",
        [],
    )

    narrative_limits = scenario.get(
        "narrative_limits",
        [],
    )

    lines: List[str] = [
        f"Title: {title}",
        f"Premise: {premise}",
        "",
    ]

    lines.extend(build_list_lines("Tone", tone))
    lines.append("")
    lines.extend(build_list_lines("Canon rules", canon_rules))
    lines.append("")
    lines.extend(build_list_lines("Character dynamics", character_dynamics))
    lines.append("")
    lines.extend(build_list_lines("Pacing rules", pacing_rules))
    lines.append("")
    lines.extend(build_list_lines("Narrative limits", narrative_limits))

    return "\n".join(lines)
