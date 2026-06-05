"""Construction du prompt envoye au LLM.

Le prompt explique au modele le contexte de la scene, l'action du joueur,
les regles narratives et le format JSON attendu.
"""

from typing import Any, Dict, List
from app.core.contact_engine import build_contact_context

SCENE_HISTORY_MAX_PROMPT = 4
from app.core.memory_retriever import select_relevant_memories
from app.core.planned_event_engine import build_planned_events_context
from app.core.relationship_stages import build_relationship_context
from app.core.runtime_directives import build_runtime_directives_context
from app.core.story_arc_state_engine import build_story_arc_state_context
from app.core.story_arc_engine import build_story_arcs_context


def scene_history_to_text(scene_history: list[dict] | None) -> str | None:
    """Convertit une liste de tours en texte plat pour le scoring mémoire."""

    if not scene_history:
        return None

    lines = []

    for turn in scene_history[-SCENE_HISTORY_MAX_PROMPT:]:
        player_input = turn.get("player_input")
        scene_text = turn.get("scene_text", "")

        if player_input:
            lines.append(player_input)

        if scene_text:
            lines.append(scene_text)

    return "\n".join(lines) if lines else None


def build_structured_scene_prompt(
    world: Dict[str, Any],
    scenario: Dict[str, Any],
    scene_context: Dict[str, Any],
    player_input: str | None = None,
    scene_history: list[dict] | None = None,
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
        scene_history_to_text(scene_history),
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
    absent_characters_context = build_absent_characters_context(world, scene_context)
    phone_inbox_context = build_phone_inbox_context(world)
    active_tasks_context = build_active_tasks_context(world, scene_context)
    scene_props_context = build_scene_props_context(world, location.get("id", ""))

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

ESTABLISHED SCENE DETAILS (physical details already set in this location)
{scene_props_context}
- Do not contradict these established details.
- If you introduce a new specific physical detail that should persist (a piece of furniture, a named object, a decoration), add a short one-line description to world_updates.new_scene_props. Do not add general atmosphere — only specific anchors that matter.

AVAILABLE LOCATIONS
{available_locations}

PLAYER CHARACTER — ABSOLUTE RULE
{player_character_id} belongs exclusively to the player. The narrator has NO authorisation to generate:
- thoughts, feelings, emotions, intentions, decisions, conclusions
- internal perceptions or memories
- movements, future actions, or any action not explicitly written by the player

The narrator may only write {player_character_id} in TWO cases:
  1. To echo an action the player explicitly wrote. Player: *Je hausse les épaules.* → Allowed: "{player_character_id} hausse les épaules."
  2. To describe an immediate physical consequence of the player's action. Player: *Je m'assois.* → Allowed: "Le matelas s'enfonce légèrement."

ALL of the following are FORBIDDEN — delete any sentence that contains one:
  ❌ "{player_character_id} sait que..." / "comprend que..." / "réalise que..." / "se demande si..."
  ❌ "{player_character_id} pense que..." / "ressent..." / "est amusée..." / "est agacée..."
  ❌ "{player_character_id} décide de..." / "choisit de..." / "s'apprête à..." / "a envie de..."
  ❌ "{player_character_id} quitte..." / "se dirige vers..." / "tourne les talons." / "regagne sa chambre."
  ❌ "elle sait que..." / "elle pense que..." / "elle ressent..." / "elle se demande..."

VALIDATION — before outputting, check every narration sentence: if it attributes a thought, emotion, intention, decision, or movement to {player_character_id}, DELETE IT. No exceptions.
When in doubt: DO NOT WRITE {player_character_id}. Write only the NPCs.

ACTIVE PARTICIPANTS
{participant_lines}
- Only the character IDs listed above are physically present in the current active scene.
- scene.participants and dialogues.speaker must stay limited to current active participants, except for NPCs explicitly moved into the scene by character_movements.
- Not every participant needs to speak every scene. A character who has nothing new, surprising, or meaningful to contribute should remain silent or receive only a brief non-verbal mention in narration. Avoid reflexive or predictable reactions (e.g., a sibling always stepping in to defend, a friend always agreeing). Silence and presence are valid narrative choices.

CHARACTER SHEET PRIORITY
Each participant's sheet above is canonical truth — not inspiration. The following fields are always considered real facts: identity, age, studies, university activity, sport team, occupation, goals, relationships, schedule, current activity, speech style, behavioural rules.
Before generating any NPC dialogue:
  1. Identify the character's sheet data relevant to the current moment.
  2. Generate their response from that data — not from invention.
  3. A character cannot ignore their own sheet. A character cannot answer with invention when their sheet contains the answer.
- If the player asks a factual question ("Qu'est-ce que tu étudies ?", "Tu joues dans quelle équipe ?"), the NPC MUST answer with the real fact from their sheet FIRST. Personality, humour or deflection can follow, but NEVER replace the answer.
- A joke is not an answer. An evasion is not an answer. Vague atmosphere is not an answer.
- Mandatory order: (1) answer the question → (2) add personality / humour / flirt if appropriate.
- An unanswered player question is a narration error.

ABSENT CHARACTERS
{absent_characters_context}
- These characters are physically elsewhere. They cannot enter this scene, see what happens here, or hear what is said.
- Do not write narration, dialogue, reactions, thoughts or physical presence for any absent character.
- Do not describe an absent character reacting to an SMS, looking at their phone, receiving news, or doing anything in response to events in this scene.
- Narration must describe only what the player character can directly observe in their current location.

ACTIVE TASKS
{active_tasks_context}
- NPCs assigned to an active task are primarily focused on it. Their presence in the scene should reflect the task — they carry boxes, arrange things, give instructions, check progress.
- At least once per scene where an assigned NPC appears, show them doing something concrete for the task — not just commenting on other characters.
- When a task clearly advances, update it via world_updates.task_updates with the new progress (0–100) and a short note describing the current state.
- A task at 100% should be set to status: "completed".

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

PHONE INBOX (unread messages waiting for the player)
{phone_inbox_context}
- If the player's action involves checking their phone, reading messages, or texting, and PHONE INBOX is not empty, the scene MUST reveal those messages — show what the player reads on screen.
- If PHONE INBOX is empty, the phone has no new messages to show.

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
- NPC INDIVIDUAL ENGAGEMENT: Each NPC reasons from their own perspective, their own knowledge, and their own current activity — never from a global awareness of the scene. Before having an NPC react, follow the player, or initiate contact, ask: does this specific NPC have a reason to act given their current_goals, their position, and what they personally know? A character occupied with their own activity (helping someone move, studying, working) should not abandon it without a compelling reason specific to them. When the player moves away from a group, the NPC most likely to follow is the one with no active engagement, not the one with the highest relationship score.
- NPC TASK PRIORITY: An NPC assigned to an active task (see ACTIVE TASKS) is primarily there to do that task. Their contribution to the scene is often a physical action, not a quip. They should not become a commentator on the player-NPC dynamic. A character helping with a task can exchange one or two lines with the player, but their hands keep working.
- NPC TASK CONTINUITY: Each NPC has a "Current activity" line. This is a commitment — the NPC must continue this activity across turns. Do NOT have an NPC silently drop their task to become a passive observer or audience member for a nearby conversation. An NPC can briefly comment on the conversation while their hands keep working (e.g., Garrett sets a box down to say something, then picks up another). Only change an NPC's current_activity in world_updates.character_activity_updates when: the task genuinely advances to a new stage, the NPC explicitly decides to stop, or a significant event forces a change. A nearby interesting conversation is NOT sufficient reason to abandon a task.
- NPC SOCIAL DISTANCE: A character who has just met the player has friendship and respect scores near zero. They do not joke at the player's expense, do not adopt a warm or teasing tone, do not express personal opinions about the player's choices or character. They are politely neutral to mildly curious at best. Familiarity is earned slowly through repeated interaction and reflected in rising relationship scores — it does not happen in the first scene.
- NPC KNOWLEDGE BOUNDARY: Each NPC knows only what they have directly witnessed or been explicitly told within the story. They do not have access to system context, player metadata, or scenario notes. They cannot use the player's name unless they have actually learned it in the fiction.
- NPC ACTIVE MEMORY: Before generating each NPC's dialogue or action, consult their Current activity, goals, schedule, relationships and player_knowledge. NPCs must speak and act from their real life — studies, sport, work, projects, obligations, relationships. Dialogue that consists only of jokes and social reactions is a failure: each character has an existence outside the player. A university character should naturally reference their team, their courses, their plans — not just react to what the player says.
- PLAYER QUESTION = MANDATORY ANSWER: When the player asks a direct question to an NPC, that NPC MUST provide a real answer before doing anything else. Identify: (1) the question, (2) the NPC it is addressed to, (3) the answer from their sheet. Output the answer first. Only then add tone, humour, or follow-up. Replacing an answer with a quip, a vague remark, or silence is a narration error.

SCENE DIRECTION
- The player_input is a trigger, not the whole scene.
- Move the scene forward through a mix of reaction, non-player character initiative and consequence.
- Favor concrete micro-actions: a look, a gesture, a movement, a decision, an invitation or a moment of tension.
- Avoid generic responses like "I will call you soon" when a character can propose something more specific and embodied.
- Generate a scene that makes the player want to answer immediately.
- If player_input is empty during an ongoing scene, treat it as the player waiting or observing briefly, not as permission to shift focus away from the player.
- ACTION + CONSEQUENCE: When the player performs a physical action (handing something, carrying something, helping with a task), the scene must show a physical consequence — what changes in the world, what gets done, what moves. A joke or quip in response to a physical action is decoration, not a consequence. Show the consequence first, then allow one line of humor if the character and tone call for it.
- Do not convert action scenes into dialogue scenes. If the player helps with a move, the move advances. If the player carries a box, something gets done. The world responds to effort.

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
- CRITICAL — narration must NEVER quote what any character says. All spoken words belong exclusively in the dialogues array. Writing "Hannah répond : '...'" or any quoted speech inside a narration paragraph is forbidden. Narration describes only physical actions, movement, atmosphere, and environment.
- Use the location ID for scene.location.
- The player character ID is elina. This is a technical identifier for the JSON structure only.
- Never include "elina" as a speaker in dialogues.
- Never generate dialogue for elina.
- If the player writes dialogue, treat it as already spoken by elina and only generate reactions from other characters.
- CRITICAL — NPC name knowledge: Each participant has a "What X knows about elina" line. If it says "does NOT know their name", that NPC must NEVER use the player's name, first or last, in dialogue or narration. They must refer to the player as "tu", "elle", "la fille", a physical description, or simply by no name at all. Using the player's name before an introduction has occurred is a diegetic error.
- When an NPC learns the player's name during the scene (e.g., the player introduces herself, someone reads her name on a box, a third character introduces her), include that NPC in npc_knowledge_updates with knows_name: true and known_name set to the name they actually heard.
- memory_updates must use character IDs.
- memory owner must be one of the active participants.
- importance must be an integer between 1 and 10.
- Only create memories for narratively meaningful moments.
- Do not create memories for every line of dialogue.
- Each participant's "Position in location" tells you exactly where they are within the current location. A character in their room cannot see or hear what happens in the hallway or stairwell unless they open their door. Respect these spatial constraints when writing narration and reactions.
- character_activity_updates maps character IDs to a short free-text description of what they are now doing. Update an NPC's activity when their task genuinely advances to a new stage (e.g., "finit de porter les cartons, commence à démonter les étagères") or when they clearly start a new activity. Do not update if they are still doing the same thing as before. If no activity changed, use an empty object.
- Use character_position_updates when a character clearly moves within the location (e.g., opens their door and steps into the hallway, moves from the hallway to the stairwell, sits down somewhere specific). Map character IDs to a short free-text description of their new position within the current location. If no character moves within the location, use an empty object.
- task_updates maps task IDs to progress objects. Only include a task if it clearly advanced in this scene. Set progress (integer 0–100), a brief note (string) describing the current state, and optionally status: "completed" when the task reaches 100%.
- new_scene_props is a list of short strings describing specific physical details you introduced in this scene that should persist (a named piece of furniture, a specific object, a detail of the room). Only add genuinely new and specific details — not general atmosphere. If nothing new was introduced, use an empty list.
- CRITICAL — world_updates.new_location must be empty unless the player's input explicitly contains movement language (e.g., "je vais à", "je pars", "je monte", "je descends", "je quitte", "je rentre", "je me dirige vers"). Asking a question, answering, helping with a task, or staying silent is NOT movement. Do not infer that the player wants to leave just because the scene feels complete.
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
- Do not fill narration with ambient descriptions (background students, general campus noise, weather, the passing crowd) unless they create direct narrative tension or introduce new information. If nothing meaningful happens in the environment, omit it.

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
        position = character.get("_position_in_location", "")
        if position:
            lines.append(f"  - Position in location: {position}")
        activity = character.get("_current_activity", "")
        if activity:
            lines.append(f"  - Current activity: {activity}")
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


def build_absent_characters_context(
    world: Dict[str, Any],
    scene_context: Dict[str, Any],
) -> str:
    """Liste les personnages absents de la scene active et leur position actuelle."""

    participant_ids = {
        p.get("id", "")
        for p in scene_context.get("participants", [])
        if isinstance(p, dict)
    }

    player_character_id = world.get("player_character", "")
    character_locations = world.get("character_locations", {})

    location_names: Dict[str, str] = {
        loc["id"]: loc["name"]
        for loc in world.get("locations", [])
        if isinstance(loc, dict)
    }

    lines = []
    for char_id in world.get("characters", []):
        if char_id == player_character_id:
            continue
        if char_id in participant_ids:
            continue
        location_id = character_locations.get(char_id, "unknown")
        location_name = location_names.get(location_id, location_id)
        lines.append(f"- {char_id}: currently at {location_name} — not present, cannot see or hear what happens here")

    return "\n".join(lines) if lines else "(none)"


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

    append_optional_line(
        lines,
        "Appearance",
        safe_string(character.get("appearance")),
    )

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

    # What this NPC knows about the player character (diegetic knowledge only)
    character_id = character.get("id", "")
    if character_id and character_id != player_character_id:
        pk = character.get("player_knowledge", {})
        if isinstance(pk, dict):
            knows_name = pk.get("knows_name", False)
            known_name = pk.get("known_name")
            if knows_name and known_name:
                lines.append(
                    f"  - What {character_id} knows about {player_character_id}:"
                    f" knows their name is \"{known_name}\""
                )
            else:
                lines.append(
                    f"  - What {character_id} knows about {player_character_id}:"
                    f" does NOT know their name yet (no introduction has occurred)"
                )

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
            "IMPORTANT: scene.location must remain the CURRENT departure location, "
            "not the destination. "
            "The player is still leaving — show the farewell moment here. "
            "world_updates.new_location updates the world state for the next turn. "
            "scene.participants should include all characters present at the departure."
        ),
        (
            "The next scene (next player turn) will follow the player character at "
            f"{detected_movement} unless an NPC explicitly follows."
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
  "npc_knowledge_updates": {
    "character_id": {
      "knows_name": true,
      "known_name": "name they actually heard"
    }
  },
  "world_updates": {
    "new_location": "",
    "time_advance_minutes": 0,
    "character_movements": {
        "character_id": "location_id"
    },
    "character_position_updates": {
        "character_id": "free-text position within current location"
    },
    "character_activity_updates": {
        "character_id": "short description of what this NPC is now doing"
    },
    "task_updates": {
        "task_id": { "progress": 0, "note": "", "status": "active" }
    },
    "new_scene_props": []
  }
}
""".strip()


def build_scene_history_context(scene_history: list[dict] | None) -> str:
    """Prepare l'historique de scene a envoyer au LLM (max SCENE_HISTORY_MAX_PROMPT tours)."""

    if not scene_history:
        return "No previous scene yet."

    recent_turns = scene_history[-SCENE_HISTORY_MAX_PROMPT:]
    lines = []

    for turn in recent_turns:
        player_input = turn.get("player_input")
        scene_text = turn.get("scene_text", "")

        if player_input:
            lines.append(f"Player: {player_input}")
            lines.append("")

        if scene_text:
            lines.append(scene_text)
            lines.append("")

    result = "\n".join(lines).strip()

    return result if result else "No previous scene yet."


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


def build_phone_inbox_context(world: Dict[str, Any]) -> str:
    """Retourne les SMS non lus recus par le joueur, pour le contexte de scene."""

    player_id = world.get("player_character", "")
    messages = world.get("messages", [])

    if not isinstance(messages, list):
        return ""

    unread = [
        m for m in messages
        if isinstance(m, dict)
        and m.get("to") == player_id
        and m.get("status") in ("unread", "pending_delivery", "delivered")
    ]

    if not unread:
        return ""

    lines = []
    for m in unread[-5:]:  # 5 most recent unread
        sender = m.get("from", "?")
        content = m.get("content", "")
        day = m.get("sent_at_day", "?")
        time = m.get("sent_at_time", "")
        lines.append(f"- From {sender} (day {day}{', ' + time if time else ''}): {content}")

    return "\n".join(lines)


def build_active_tasks_context(
    world: Dict[str, Any],
    scene_context: Dict[str, Any],
) -> str:
    """Retourne les tâches actives pertinentes pour la scène courante."""

    tasks = world.get("active_tasks", [])
    if not isinstance(tasks, list) or not tasks:
        return "(none)"

    current_location = scene_context.get("location", {}).get("id", "")
    participant_ids = {
        p.get("id", "")
        for p in scene_context.get("participants", [])
        if isinstance(p, dict)
    }

    lines = []
    for task in tasks:
        if not isinstance(task, dict):
            continue
        if task.get("status") not in ("active",):
            continue
        task_loc = task.get("location", "")
        assigned = task.get("assigned_participants", [])
        if not isinstance(assigned, list):
            assigned = []

        # Only show if task is at current location AND an assigned participant is present
        if task_loc and task_loc != current_location:
            continue
        if assigned and not any(p in participant_ids for p in assigned):
            continue

        tid = task.get("id", "")
        title = task.get("title", "")
        desc = task.get("description", "")
        progress = task.get("progress", 0)
        note = task.get("note", "")
        assigned_str = ", ".join(assigned) if assigned else "?"

        line = f"- [{tid}] {title} — {assigned_str} — {progress}% done"
        if note:
            line += f" — {note}"
        if desc:
            line += f"\n  {desc}"
        lines.append(line)

    return "\n".join(lines) if lines else "(none)"


def build_scene_props_context(world: Dict[str, Any], location_id: str) -> str:
    """Retourne les détails physiques établis dans le lieu courant."""

    props = world.get("scene_props", {}).get(location_id, [])
    if not isinstance(props, list) or not props:
        return "(none established yet)"

    return "\n".join(f"- {p}" for p in props)


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
