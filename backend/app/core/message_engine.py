"""Message Engine MVP.

Ce moteur ajoute des messages hors scene uniquement quand une opportunite
narrative claire existe deja. Il reste deterministe pour eviter le spam et les
effets de bord difficiles a deboguer.
"""

from typing import Any, Callable, Dict, List
import os
import re
import unicodedata

from app.core.planned_event_engine import (
    append_planned_event,
    build_skating_lesson_planned_event,
)
from app.core.story_arc_state_engine import apply_story_arc_state_from_messages


SKATING_FOLLOWUP_TRIGGER = "skating_lesson_followup"
SKATING_REPLY_CONFIRMATION_TRIGGER = "skating_lesson_reply_confirmation"
GENERIC_SMS_REPLY_TRIGGER_PREFIX = "generic_sms_reply"
SKATING_FOLLOWUP_CONTENT = (
    "Demain matin. Patinoire. 7h. "
    "Si tu survis a la premiere heure, je te paie un cafe."
)
SKATING_REPLY_CONFIRMATION_CONTENT = (
    "Parfait. Mets quelque chose de chaud. "
    "Je promets de ne pas rire avant ta deuxieme chute."
)
LLM_SMS_ENV_VAR = "INK_FATE_ENABLE_LLM_SMS"
MAX_SMS_CONTENT_LENGTH = 240

SKATING_CONTEXT_KEYWORDS = [
    "patin",
    "patinoire",
    "hockey",
    "defi",
    "lesson",
    "skating",
]

SMS_REPLY_PATTERN = re.compile(
    r"^(?:reply|sms|text)\s+([A-Za-z0-9_-]+)\s*:\s*(.+)$",
    re.IGNORECASE,
)


def generate_pending_messages(
    world: Dict[str, Any],
    characters: Dict[str, Dict[str, Any]],
    scene_result: Dict[str, Any],
    scenario: Dict[str, Any] | None = None,
    extra_context: Dict[str, Any] | None = None,
    llm_generate_text: Callable[[str], str] | None = None,
) -> List[Dict[str, Any]]:
    """Genere les messages hors scene a ajouter au monde."""

    messages: List[Dict[str, Any]] = []
    timeline = world.get(
        "timeline",
        {},
    )

    for trigger_config in get_message_trigger_configs(scenario):
        if not should_generate_configured_message(
            world,
            characters,
            scene_result,
            trigger_config,
            extra_context,
        ):
            continue

        sender = trigger_config["from"]
        recipient = trigger_config["to"]
        trigger = trigger_config["trigger"]

        messages.append(
            {
                "id": build_message_id(
                    sender,
                    recipient,
                    trigger,
                    timeline,
                ),
                "from": sender,
                "to": recipient,
                "channel": trigger_config["channel"],
                "content": build_configured_pending_message_content(
                    world,
                    characters,
                    scene_result,
                    trigger_config,
                    extra_context,
                    llm_generate_text,
                ),
                "sent_at_day": timeline.get("current_day", 1),
                "sent_at_time": timeline.get("current_time", "??:??"),
                "status": "unread",
                "trigger": trigger,
            }
        )

    return messages


def get_message_trigger_configs(
    scenario: Dict[str, Any] | None,
) -> List[Dict[str, Any]]:
    """Retourne les triggers de messages scenario avec fallback MVP."""

    default_config = get_message_trigger_config(
        scenario,
        SKATING_FOLLOWUP_TRIGGER,
    )

    configs_by_trigger = {
        default_config["trigger"]: default_config,
    }

    if not isinstance(scenario, dict):
        return list(configs_by_trigger.values())

    message_triggers = scenario.get(
        "message_triggers",
        [],
    )

    if not isinstance(message_triggers, list):
        return list(configs_by_trigger.values())

    for message_trigger in message_triggers:
        config = normalize_message_trigger_config(message_trigger)

        if not config:
            continue

        configs_by_trigger[config["trigger"]] = config

    return list(configs_by_trigger.values())


def should_generate_configured_message(
    world: Dict[str, Any],
    characters: Dict[str, Dict[str, Any]],
    scene_result: Dict[str, Any],
    trigger_config: Dict[str, Any],
    extra_context: Dict[str, Any] | None = None,
) -> bool:
    """Verifie les conditions communes d'un SMS PNJ configure."""

    player_character = world.get(
        "player_character",
    )
    sender = trigger_config.get(
        "from",
    )
    recipient = trigger_config.get(
        "to",
    )
    trigger = trigger_config.get(
        "trigger",
    )
    channel = trigger_config.get(
        "channel",
    )

    if not isinstance(player_character, str):
        return False

    if recipient != player_character:
        return False

    if not isinstance(sender, str) or sender not in characters:
        return False

    if not isinstance(recipient, str) or recipient not in characters:
        return False

    if sender == recipient:
        return False

    if channel != "sms":
        return False

    if not isinstance(trigger, str) or not trigger:
        return False

    if not character_can_text_recipient(
        characters,
        sender,
        recipient,
    ):
        return False

    if characters_share_location(
        world,
        sender,
        recipient,
    ):
        return False

    if has_existing_message(
        world,
        sender,
        recipient,
        trigger,
    ):
        return False

    return scene_result_contains_message_context(
        scene_result,
        trigger_config.get("keywords", []),
        extra_context,
    )


def build_configured_pending_message_content(
    world: Dict[str, Any],
    characters: Dict[str, Dict[str, Any]],
    scene_result: Dict[str, Any],
    trigger_config: Dict[str, Any],
    extra_context: Dict[str, Any] | None = None,
    llm_generate_text: Callable[[str], str] | None = None,
) -> str:
    """Construit le contenu d'un SMS PNJ initie hors scene."""

    fallback_content = trigger_config.get(
        "content",
        "",
    )

    if not isinstance(fallback_content, str):
        fallback_content = ""

    generator = resolve_llm_sms_generator(
        llm_generate_text,
    )

    if generator is None:
        return fallback_content

    prompt = build_configured_pending_message_prompt(
        world,
        characters,
        scene_result,
        trigger_config,
        extra_context,
    )

    try:
        generated_content = generator(prompt)
    except Exception:
        return fallback_content

    return sanitize_llm_sms_content(
        generated_content,
        fallback_content,
    )


def build_configured_pending_message_prompt(
    world: Dict[str, Any],
    characters: Dict[str, Dict[str, Any]],
    scene_result: Dict[str, Any],
    trigger_config: Dict[str, Any],
    extra_context: Dict[str, Any] | None = None,
) -> str:
    """Construit un prompt court pour un SMS PNJ initie par trigger."""

    sender = trigger_config["from"]
    recipient = trigger_config["to"]
    sender_character = characters.get(
        sender,
        {},
    )
    recipient_character = characters.get(
        recipient,
        {},
    )
    sender_name = build_character_display_name(
        sender_character,
        sender,
    )
    recipient_name = build_character_display_name(
        recipient_character,
        recipient,
    )
    sender_context = build_sms_character_context(
        sender,
        sender_character,
        recipient,
    )
    recent_messages = build_recent_sms_context(
        world,
        sender,
        recipient,
    )
    recent_scene_context = build_pending_message_scene_context(
        scene_result,
        extra_context,
    )

    return f"""
You are writing one in-character SMS for Ink & Fate.

The sender is {sender_name} ({sender}).
The recipient is {recipient_name} ({recipient}), the player character.

SENDER CONTEXT
{sender_context}

RECENT SMS CONTEXT
{recent_messages}

RECENT NARRATIVE CONTEXT
{recent_scene_context}

TRIGGER
- Trigger ID: {trigger_config["trigger"]}
- Fallback intent: {trigger_config["content"]}

SMS RULES
- Write only the SMS content.
- Write in French.
- Do not include speaker labels.
- Do not wrap the message in quotes.
- Do not use markdown.
- Do not write actions, narration, thoughts, or stage directions.
- Do not decide what the player thinks, feels, says, or does next.
- Keep it concise: one or two short sentences.
- Make the message concrete and character-specific.
- Follow the sender's speech style, behavior rules, goals and relationship to the recipient.
""".strip()


def build_pending_message_scene_context(
    scene_result: Dict[str, Any],
    extra_context: Dict[str, Any] | None = None,
    max_items: int = 6,
) -> str:
    """Resume le contexte qui a declenche un SMS hors scene."""

    texts = collect_scene_context_text(scene_result)
    texts.extend(
        collect_extra_context_text(extra_context)
    )
    cleaned_texts = [
        text.strip()
        for text in texts
        if isinstance(text, str) and text.strip()
    ]

    if not cleaned_texts:
        return "No recent narrative context."

    return "\n".join(
        f"- {text[:220]}"
        for text in cleaned_texts[-max_items:]
    )


def append_pending_messages(
    world: Dict[str, Any],
    messages: List[Dict[str, Any]],
    scenario: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Ajoute les nouveaux messages dans world.messages."""

    world.setdefault(
        "messages",
        [],
    )

    if messages:
        world["messages"].extend(messages)
        world = apply_story_arc_state_from_messages(
            world,
            messages,
            scenario,
        )

    return world


def get_player_messages(
    world: Dict[str, Any],
    player_character: str | None = None,
) -> List[Dict[str, Any]]:
    """Retourne les messages stockes envoyes au personnage joueur."""

    if player_character is None:
        player_character = world.get(
            "player_character",
        )

    if not isinstance(player_character, str):
        return []

    messages = world.get(
        "messages",
        [],
    )

    if not isinstance(messages, list):
        return []

    return [
        message
        for message in messages
        if isinstance(message, dict)
        and message.get("to") == player_character
    ]


def mark_player_messages_read(
    world: Dict[str, Any],
    player_character: str | None = None,
) -> Dict[str, Any]:
    """Marque comme lus les messages stockes envoyes au joueur."""

    if player_character is None:
        player_character = world.get(
            "player_character",
        )

    if not isinstance(player_character, str):
        return world

    messages = world.get(
        "messages",
        [],
    )

    if not isinstance(messages, list):
        return world

    for message in messages:
        if not isinstance(message, dict):
            continue

        if message.get("to") != player_character:
            continue

        if message.get("status") == "unread":
            message["status"] = "read"

    return world


def parse_sms_reply_command(
    player_input: str | None,
) -> Dict[str, str] | None:
    """Parse une commande de reponse SMS."""

    if not isinstance(player_input, str):
        return None

    match = SMS_REPLY_PATTERN.match(
        player_input.strip(),
    )

    if not match:
        return None

    recipient = match.group(1).strip()
    content = match.group(2).strip()

    if not recipient or not content:
        return None

    return {
        "to": recipient,
        "content": content,
    }


def apply_player_sms_reply(
    world: Dict[str, Any],
    characters: Dict[str, Dict[str, Any]],
    reply: Dict[str, str],
    llm_generate_text: Callable[[str], str] | None = None,
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """Ajoute un SMS joueur et l'evenement associe si la reponse est valide."""

    if not can_player_send_sms_reply(
        world,
        characters,
        reply,
    ):
        return world, {
            "sent": False,
            "reason": "cannot_text_recipient",
        }

    player_character = world["player_character"]
    recipient = reply["to"]
    content = reply["content"]
    timeline = world.get(
        "timeline",
        {},
    )

    message = {
        "id": build_message_id(
            player_character,
            recipient,
            "player_reply",
            timeline,
        ),
        "from": player_character,
        "to": recipient,
        "channel": "sms",
        "content": content,
        "sent_at_day": timeline.get("current_day", 1),
        "sent_at_time": timeline.get("current_time", "??:??"),
        "status": "sent",
        "trigger": "player_reply",
    }

    world = append_pending_messages(
        world,
        [
            message,
        ],
    )
    world = append_sms_reply_event(
        world,
        message,
    )
    world = append_sms_reply_narrative_events(
        world,
        message,
    )
    npc_replies = generate_npc_sms_reply(
        world,
        characters,
        message,
        llm_generate_text,
    )
    world = append_pending_messages(
        world,
        npc_replies,
    )
    characters = apply_sms_reply_memories(
        characters,
        message,
        npc_replies,
    )

    return world, {
        "sent": True,
        "message": message,
        "npc_replies": npc_replies,
    }


def append_sms_reply_narrative_events(
    world: Dict[str, Any],
    message: Dict[str, Any],
) -> Dict[str, Any]:
    """Ajoute des evenements narratifs deduits d'un SMS joueur."""

    if should_create_skating_planned_meeting_event(
        world,
        message,
    ):
        if not has_existing_event(
            world,
            "planned_meeting",
            "skating_lesson_planned_meeting",
        ):
            append_event_log_entry(
                world,
                {
                    "type": "planned_meeting",
                    "participants": [
                        "dean",
                        "elina",
                    ],
                    "summary": (
                        "Dean and Elina agreed by SMS to meet at the rink "
                        "tomorrow at 7."
                    ),
                    "trigger": "skating_lesson_planned_meeting",
                },
            )

        world = append_planned_event(
            world,
            build_skating_lesson_planned_event(
                world,
                "sms",
            ),
        )

    return world


def should_create_skating_planned_meeting_event(
    world: Dict[str, Any],
    message: Dict[str, Any],
) -> bool:
    """Detecte l'accord SMS qui transforme le defi patinoire en rendez-vous."""

    if message.get("from") != "elina":
        return False

    if message.get("to") != "dean":
        return False

    if message.get("channel") != "sms":
        return False

    if not has_existing_message(
        world,
        "dean",
        "elina",
        SKATING_FOLLOWUP_TRIGGER,
    ):
        return False

    return message_confirms_skating_plan(
        message,
    )


def append_event_log_entry(
    world: Dict[str, Any],
    event: Dict[str, Any],
) -> Dict[str, Any]:
    """Ajoute une entree event_log avec la timeline courante."""

    event_log = world.setdefault(
        "event_log",
        [],
    )

    if not isinstance(event_log, list):
        world["event_log"] = []
        event_log = world["event_log"]

    timeline = world.get(
        "timeline",
        {},
    )
    event_log.append(
        {
            "day": timeline.get("current_day", 1),
            "date": timeline.get("current_date", ""),
            "time": timeline.get("current_time", "??:??"),
            **event,
        }
    )

    return world


def has_existing_event(
    world: Dict[str, Any],
    event_type: str,
    trigger: str,
) -> bool:
    """Evite de creer deux fois le meme evenement narratif SMS."""

    event_log = world.get(
        "event_log",
        [],
    )

    if not isinstance(event_log, list):
        return False

    for event in event_log:
        if not isinstance(event, dict):
            continue

        if event.get("type") != event_type:
            continue

        if event.get("trigger") != trigger:
            continue

        return True

    return False


def apply_sms_reply_memories(
    characters: Dict[str, Dict[str, Any]],
    player_message: Dict[str, Any],
    npc_replies: List[Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """Ajoute un souvenir simple au PNJ qui repond par SMS."""

    for reply in npc_replies:
        if not isinstance(reply, dict):
            continue

        owner_id = reply.get(
            "from",
        )

        if not isinstance(owner_id, str):
            continue

        character = characters.get(
            owner_id,
        )

        if not isinstance(character, dict):
            continue

        memory = build_sms_reply_memory(
            player_message,
            reply,
        )
        append_character_memory(
            character,
            memory,
        )

    return characters


def build_sms_reply_memory(
    player_message: Dict[str, Any],
    npc_reply: Dict[str, Any],
) -> Dict[str, Any]:
    """Construit un souvenir PNJ lie a un echange SMS."""

    player_id = ensure_message_string(
        player_message.get("from"),
        "the player",
    )
    player_content = ensure_message_string(
        player_message.get("content"),
        "",
    )
    reply_content = ensure_message_string(
        npc_reply.get("content"),
        "",
    )

    content = (
        f"{player_id} texted: {player_content} "
        f"Reply sent: {reply_content}"
    )

    return {
        "owner": ensure_message_string(
            npc_reply.get("from"),
            "",
        ),
        "type": "event",
        "content": content[:280],
        "importance": 4,
        "age": 0,
        "tags": [
            "sms",
            player_id,
        ],
    }


def append_character_memory(
    character: Dict[str, Any],
    memory: Dict[str, Any],
) -> None:
    """Ajoute un souvenir a un personnage sans doublon exact."""

    memories = character.get(
        "memories",
        [],
    )

    if not isinstance(memories, list):
        memories = []

    new_content = normalize_text(
        memory.get(
            "content",
            "",
        )
    )

    for existing_memory in memories:
        if not isinstance(existing_memory, dict):
            continue

        if normalize_text(
            existing_memory.get(
                "content",
                "",
            )
        ) == new_content:
            character["memories"] = memories
            return

    memories.append(memory)
    character["memories"] = memories


def can_player_send_sms_reply(
    world: Dict[str, Any],
    characters: Dict[str, Dict[str, Any]],
    reply: Dict[str, str],
) -> bool:
    """Verifie si le joueur peut envoyer ce SMS."""

    player_character = world.get(
        "player_character",
    )

    if not isinstance(player_character, str):
        return False

    recipient = reply.get(
        "to",
    )
    content = reply.get(
        "content",
    )

    if not isinstance(recipient, str) or not recipient:
        return False

    if recipient not in characters:
        return False

    if recipient == player_character:
        return False

    if not isinstance(content, str) or not content.strip():
        return False

    return (
        player_knows_recipient_phone(
            characters,
            player_character,
            recipient,
        )
        or recipient_has_messaged_player(
            world,
            recipient,
            player_character,
        )
    )


def player_knows_recipient_phone(
    characters: Dict[str, Dict[str, Any]],
    player_character: str,
    recipient: str,
) -> bool:
    """Retourne True si le joueur connait le numero du destinataire."""

    player = characters.get(
        player_character,
        {},
    )

    contacts = player.get(
        "contacts",
        {},
    )

    if not isinstance(contacts, dict):
        return False

    recipient_contact = contacts.get(
        recipient,
        {},
    )

    if not isinstance(recipient_contact, dict):
        return False

    return (
        recipient_contact.get("phone_number_known") is True
        or recipient_contact.get("phone_numbers_exchanged") is True
    )


def recipient_has_messaged_player(
    world: Dict[str, Any],
    recipient: str,
    player_character: str,
) -> bool:
    """Autorise une reponse si le destinataire a deja envoye un SMS au joueur."""

    messages = world.get(
        "messages",
        [],
    )

    if not isinstance(messages, list):
        return False

    for message in messages:
        if not isinstance(message, dict):
            continue

        if message.get("from") != recipient:
            continue

        if message.get("to") != player_character:
            continue

        if message.get("channel") != "sms":
            continue

        return True

    return False


def append_sms_reply_event(
    world: Dict[str, Any],
    message: Dict[str, Any],
) -> Dict[str, Any]:
    """Ajoute un evenement text_message pour une reponse SMS joueur."""

    event_log = world.setdefault(
        "event_log",
        [],
    )

    if not isinstance(event_log, list):
        world["event_log"] = []
        event_log = world["event_log"]

    timeline = world.get(
        "timeline",
        {},
    )
    sender = message.get(
        "from",
        "",
    )
    recipient = message.get(
        "to",
        "",
    )

    event_log.append(
        {
            "day": timeline.get("current_day", 1),
            "date": timeline.get("current_date", ""),
            "time": timeline.get("current_time", "??:??"),
            "type": "text_message",
            "participants": [
                sender,
                recipient,
            ],
            "summary": (
                f"{sender} texts {recipient}: "
                f"{message.get('content', '')}"
            ),
        }
    )

    return world


def generate_npc_sms_reply(
    world: Dict[str, Any],
    characters: Dict[str, Dict[str, Any]],
    player_message: Dict[str, Any],
    llm_generate_text: Callable[[str], str] | None = None,
) -> List[Dict[str, Any]]:
    """Genere une reponse PNJ a un SMS joueur."""

    if should_generate_dean_skating_reply_confirmation(
        world,
        characters,
        player_message,
    ):
        timeline = world.get(
            "timeline",
            {},
        )
        content = build_npc_sms_reply_content(
            world,
            characters,
            player_message,
            "dean",
            "elina",
            SKATING_REPLY_CONFIRMATION_CONTENT,
            llm_generate_text,
        )

        return [
            {
                "id": build_message_id(
                    "dean",
                    "elina",
                    SKATING_REPLY_CONFIRMATION_TRIGGER,
                    timeline,
                ),
                "from": "dean",
                "to": "elina",
                "channel": "sms",
                "content": content,
                "sent_at_day": timeline.get("current_day", 1),
                "sent_at_time": timeline.get("current_time", "??:??"),
                "status": "unread",
                "trigger": SKATING_REPLY_CONFIRMATION_TRIGGER,
            }
        ]

    return generate_generic_npc_sms_reply(
        world,
        characters,
        player_message,
        llm_generate_text,
    )


def generate_generic_npc_sms_reply(
    world: Dict[str, Any],
    characters: Dict[str, Dict[str, Any]],
    player_message: Dict[str, Any],
    llm_generate_text: Callable[[str], str] | None = None,
) -> List[Dict[str, Any]]:
    """Genere une reponse SMS LLM generique si un PNJ peut repondre."""

    if not should_generate_generic_npc_sms_reply(
        world,
        characters,
        player_message,
        llm_generate_text,
    ):
        return []

    sender = player_message["to"]
    recipient = player_message["from"]
    timeline = world.get(
        "timeline",
        {},
    )
    trigger = build_generic_sms_reply_trigger(
        player_message,
    )
    content = build_npc_sms_reply_content(
        world,
        characters,
        player_message,
        sender,
        recipient,
        "",
        llm_generate_text,
    )

    if not content:
        return []

    return [
        {
            "id": build_message_id(
                sender,
                recipient,
                trigger,
                timeline,
            ),
            "from": sender,
            "to": recipient,
            "channel": "sms",
            "content": content,
            "sent_at_day": timeline.get("current_day", 1),
            "sent_at_time": timeline.get("current_time", "??:??"),
            "status": "unread",
            "trigger": trigger,
        }
    ]


def should_generate_generic_npc_sms_reply(
    world: Dict[str, Any],
    characters: Dict[str, Dict[str, Any]],
    player_message: Dict[str, Any],
    llm_generate_text: Callable[[str], str] | None = None,
) -> bool:
    """Verifie si une reponse SMS PNJ LLM generique est autorisee."""

    if resolve_llm_sms_generator(llm_generate_text) is None:
        return False

    player_character = world.get(
        "player_character",
    )

    if not isinstance(player_character, str):
        return False

    sender = player_message.get(
        "from",
    )
    recipient = player_message.get(
        "to",
    )

    if sender != player_character:
        return False

    if not isinstance(recipient, str) or recipient not in characters:
        return False

    if recipient == player_character:
        return False

    if player_message.get("channel") != "sms":
        return False

    content = player_message.get(
        "content",
        "",
    )

    if not is_meaningful_sms_for_generic_reply(content):
        return False

    trigger = build_generic_sms_reply_trigger(
        player_message,
    )

    return not has_existing_message(
        world,
        recipient,
        player_character,
        trigger,
    )


def is_meaningful_sms_for_generic_reply(
    content: Any,
) -> bool:
    """Evite de repondre aux accusés de reception trop pauvres."""

    if not isinstance(content, str):
        return False

    normalized_content = normalize_text(content).strip()

    if len(normalized_content) < 8:
        return False

    low_signal_messages = {
        "ok",
        "oui",
        "non",
        "vu",
        "merci",
        "daccord",
        "d accord",
        "a plus",
    }

    return normalized_content not in low_signal_messages


def build_generic_sms_reply_trigger(
    player_message: Dict[str, Any],
) -> str:
    """Construit un trigger anti-doublon pour une reponse SMS generique."""

    sender = ensure_message_string(
        player_message.get("from"),
        "unknown",
    )
    recipient = ensure_message_string(
        player_message.get("to"),
        "unknown",
    )
    content = ensure_message_string(
        player_message.get("content"),
        "",
    )
    safe_time = str(
        player_message.get(
            "sent_at_time",
            "unknown",
        )
    ).replace(
        ":",
        "",
    )
    timeline_key = (
        f"d{player_message.get('sent_at_day', '?')}-"
        f"{safe_time}"
    )
    content_key = normalize_text(content)
    content_key = re.sub(
        r"[^a-z0-9]+",
        "_",
        content_key,
    ).strip("_")
    content_key = content_key[:32] or "message"

    return (
        f"{GENERIC_SMS_REPLY_TRIGGER_PREFIX}_"
        f"{recipient}_to_{sender}_{timeline_key}_{content_key}"
    )


def ensure_message_string(
    value: Any,
    fallback: str,
) -> str:
    """Retourne une chaine simple pour les IDs/triggers de messages."""

    if not isinstance(value, str):
        return fallback

    value = value.strip()

    return value or fallback


def build_npc_sms_reply_content(
    world: Dict[str, Any],
    characters: Dict[str, Dict[str, Any]],
    player_message: Dict[str, Any],
    sender: str,
    recipient: str,
    fallback_content: str,
    llm_generate_text: Callable[[str], str] | None = None,
) -> str:
    """Construit le contenu SMS PNJ, avec LLM optionnel et fallback stable."""

    generator = resolve_llm_sms_generator(
        llm_generate_text,
    )

    if generator is None:
        return fallback_content

    prompt = build_npc_sms_reply_prompt(
        world,
        characters,
        player_message,
        sender,
        recipient,
    )

    try:
        generated_content = generator(prompt)
    except Exception:
        return fallback_content

    return sanitize_llm_sms_content(
        generated_content,
        fallback_content,
    )


def resolve_llm_sms_generator(
    llm_generate_text: Callable[[str], str] | None = None,
) -> Callable[[str], str] | None:
    """Retourne le generateur LLM SMS si l'option est active."""

    if llm_generate_text is not None:
        return llm_generate_text

    if os.getenv(LLM_SMS_ENV_VAR) != "1":
        return None

    if not os.getenv("OPENAI_API_KEY"):
        return None

    try:
        from app.core.openai_client import generate_text
    except Exception:
        return None

    return generate_text


def build_npc_sms_reply_prompt(
    world: Dict[str, Any],
    characters: Dict[str, Dict[str, Any]],
    player_message: Dict[str, Any],
    sender: str,
    recipient: str,
) -> str:
    """Construit un prompt court pour ecrire un SMS PNJ."""

    sender_character = characters.get(
        sender,
        {},
    )
    recipient_character = characters.get(
        recipient,
        {},
    )

    sender_name = build_character_display_name(
        sender_character,
        sender,
    )
    recipient_name = build_character_display_name(
        recipient_character,
        recipient,
    )
    sender_context = build_sms_character_context(
        sender,
        sender_character,
        recipient,
    )
    recent_messages = build_recent_sms_context(
        world,
        sender,
        recipient,
    )

    player_content = player_message.get(
        "content",
        "",
    )

    return f"""
You are writing one in-character SMS for Ink & Fate.

The sender is {sender_name} ({sender}).
The recipient is {recipient_name} ({recipient}), the player character.

SENDER CONTEXT
{sender_context}

RECENT SMS CONTEXT
{recent_messages}

PLAYER SMS
{recipient}: {player_content}

SMS RULES
- Write only the SMS content.
- Write in French.
- Do not include speaker labels.
- Do not wrap the message in quotes.
- Do not use markdown.
- Do not write actions, narration, thoughts, or stage directions.
- Do not decide what the player thinks, feels, says, or does next.
- Keep it concise: one or two short sentences.
- Make the message concrete and character-specific.
- Follow the sender's speech style, behavior rules, goals and relationship to the recipient.
""".strip()


def build_character_display_name(
    character: Dict[str, Any],
    fallback: str,
) -> str:
    """Retourne un nom lisible pour le prompt SMS."""

    identity = character.get(
        "identity",
        {},
    )

    if not isinstance(identity, dict):
        return fallback

    first_name = identity.get(
        "first_name",
        "",
    )
    last_name = identity.get(
        "last_name",
        "",
    )
    full_name = f"{first_name} {last_name}".strip()

    return full_name or fallback


def build_sms_character_context(
    character_id: str,
    character: Dict[str, Any],
    recipient_id: str,
) -> str:
    """Resume le personnage pour guider une reponse SMS LLM."""

    lines = [
        f"- Character ID: {character_id}",
    ]

    for label, key in [
        ("Archetype", "archetype"),
        ("Current goals", "current_goals"),
        ("Speech style", "speech_style"),
        ("Behavior rules", "behavior_rules"),
        ("Desires", "desires"),
        ("Fears", "fears"),
    ]:
        value = character.get(
            key,
        )
        formatted_value = format_sms_context_value(
            value,
        )

        if formatted_value:
            lines.append(f"- {label}: {formatted_value}")

    relationships = character.get(
        "relationships",
        {},
    )

    if isinstance(relationships, dict):
        recipient_relationship = relationships.get(
            recipient_id,
        )

        if isinstance(recipient_relationship, dict):
            lines.append(
                "- Relationship to recipient: "
                f"{format_sms_context_value(recipient_relationship)}"
            )

    return "\n".join(lines)


def format_sms_context_value(
    value: Any,
) -> str:
    """Formate une valeur simple pour un prompt SMS compact."""

    if isinstance(value, str):
        return value

    if isinstance(value, list):
        return "; ".join(
            item
            for item in value
            if isinstance(item, str) and item.strip()
        )

    if isinstance(value, dict):
        parts = []

        for key, item in value.items():
            if isinstance(item, (str, int, float, bool)):
                parts.append(f"{key}={item}")

        return ", ".join(parts)

    return ""


def build_recent_sms_context(
    world: Dict[str, Any],
    first_character_id: str,
    second_character_id: str,
    max_messages: int = 6,
) -> str:
    """Resume les derniers SMS entre deux personnages."""

    messages = world.get(
        "messages",
        [],
    )

    if not isinstance(messages, list):
        return "No previous SMS."

    relevant_messages = []

    for message in messages:
        if not isinstance(message, dict):
            continue

        sender = message.get(
            "from",
        )
        recipient = message.get(
            "to",
        )

        if {
            sender,
            recipient,
        } != {
            first_character_id,
            second_character_id,
        }:
            continue

        content = message.get(
            "content",
            "",
        )

        if isinstance(content, str) and content.strip():
            relevant_messages.append(
                f"- {sender} to {recipient}: {content}"
            )

    if not relevant_messages:
        return "No previous SMS."

    return "\n".join(
        relevant_messages[-max_messages:],
    )


def sanitize_llm_sms_content(
    generated_content: Any,
    fallback_content: str,
) -> str:
    """Nettoie une sortie LLM SMS sans casser les apostrophes francaises."""

    if not isinstance(generated_content, str):
        return fallback_content

    content = generated_content.strip()

    if not content:
        return fallback_content

    content = remove_markdown_fences(
        content,
    )
    content = content.strip()
    content = strip_wrapping_quotes(
        content,
    )
    content = content.strip()

    if not content:
        return fallback_content

    if "\n" in content:
        content = " ".join(
            line.strip()
            for line in content.splitlines()
            if line.strip()
        )

    if ":" in content:
        label, possible_content = content.split(
            ":",
            1,
        )

        if normalize_text(label).strip() in [
            "dean",
            "dean di laurentis",
        ]:
            content = possible_content.strip()

    content = strip_wrapping_quotes(
        content.strip(),
    )

    if not content:
        return fallback_content

    if len(content) > MAX_SMS_CONTENT_LENGTH:
        content = content[:MAX_SMS_CONTENT_LENGTH].rstrip()

    return content


def remove_markdown_fences(
    content: str,
) -> str:
    """Retire des fences markdown simples si le modele en ajoute."""

    if content.startswith("```") and content.endswith("```"):
        lines = content.splitlines()

        if len(lines) >= 3:
            return "\n".join(lines[1:-1])

    return content


def strip_wrapping_quotes(
    content: str,
) -> str:
    """Retire seulement les guillemets englobants."""

    wrapping_pairs = [
        ('"', '"'),
        ("'", "'"),
        ("«", "»"),
        ("“", "”"),
        ("‘", "’"),
    ]

    for opening, closing in wrapping_pairs:
        if content.startswith(opening) and content.endswith(closing):
            return content[1:-1]

    return content


def should_generate_dean_skating_reply_confirmation(
    world: Dict[str, Any],
    characters: Dict[str, Dict[str, Any]],
    player_message: Dict[str, Any],
) -> bool:
    """Verifie si Dean doit confirmer le rendez-vous patinoire par SMS."""

    if world.get("player_character") != "elina":
        return False

    if player_message.get("from") != "elina":
        return False

    if player_message.get("to") != "dean":
        return False

    if player_message.get("channel") != "sms":
        return False

    if not dean_knows_elina_phone_number(characters):
        return False

    if not has_existing_message(
        world,
        "dean",
        "elina",
        SKATING_FOLLOWUP_TRIGGER,
    ):
        return False

    if has_existing_message(
        world,
        "dean",
        "elina",
        SKATING_REPLY_CONFIRMATION_TRIGGER,
    ):
        return False

    return message_confirms_skating_plan(
        player_message,
    )


def message_confirms_skating_plan(
    message: Dict[str, Any],
) -> bool:
    """Detecte une confirmation simple du joueur pour le plan patinoire."""

    content = message.get(
        "content",
        "",
    )

    if not isinstance(content, str):
        return False

    normalized_content = normalize_text(content)
    confirmation_keywords = [
        "ok",
        "oui",
        "daccord",
        "d accord",
        "a demain",
        "7h",
        "sept",
        "je confirme",
        "j arrive",
        "partante",
        "deal",
    ]

    return any(
        keyword in normalized_content
        for keyword in confirmation_keywords
    )


def should_generate_dean_skating_followup(
    world: Dict[str, Any],
    characters: Dict[str, Dict[str, Any]],
    scene_result: Dict[str, Any],
    trigger_config: Dict[str, Any] | None = None,
    extra_context: Dict[str, Any] | None = None,
) -> bool:
    """Verifie les conditions MVP pour un SMS Dean -> Elina."""

    if trigger_config is None:
        trigger_config = get_default_skating_followup_config()

    if world.get("player_character") != "elina":
        return False

    if "dean" not in characters or "elina" not in characters:
        return False

    return should_generate_configured_message(
        world,
        characters,
        scene_result,
        trigger_config,
        extra_context,
    )


def get_message_trigger_config(
    scenario: Dict[str, Any] | None,
    trigger: str,
) -> Dict[str, Any]:
    """Lit la configuration d'un message depuis le scenario."""

    default_config = get_default_skating_followup_config()

    if not isinstance(scenario, dict):
        return default_config

    message_triggers = scenario.get(
        "message_triggers",
        [],
    )

    if not isinstance(message_triggers, list):
        return default_config

    for message_trigger in message_triggers:
        if not isinstance(message_trigger, dict):
            continue

        if message_trigger.get("trigger") != trigger:
            continue

        config = {
            **default_config,
            **message_trigger,
        }

        if not isinstance(config.get("keywords"), list):
            config["keywords"] = default_config["keywords"]

        if not isinstance(config.get("content"), str):
            config["content"] = default_config["content"]

        return config

    return default_config


def normalize_message_trigger_config(
    message_trigger: Any,
) -> Dict[str, Any] | None:
    """Valide une configuration de message hors scene."""

    if not isinstance(message_trigger, dict):
        return None

    trigger = message_trigger.get(
        "trigger",
    )
    sender = message_trigger.get(
        "from",
    )
    recipient = message_trigger.get(
        "to",
    )
    channel = message_trigger.get(
        "channel",
        "sms",
    )
    content = message_trigger.get(
        "content",
    )
    keywords = message_trigger.get(
        "keywords",
        [],
    )

    if not all(
        isinstance(value, str) and value.strip()
        for value in [
            trigger,
            sender,
            recipient,
            channel,
            content,
        ]
    ):
        return None

    if not isinstance(keywords, list):
        return None

    cleaned_keywords = [
        keyword
        for keyword in keywords
        if isinstance(keyword, str) and keyword.strip()
    ]

    if not cleaned_keywords:
        return None

    return {
        "trigger": trigger.strip(),
        "from": sender.strip(),
        "to": recipient.strip(),
        "channel": channel.strip(),
        "content": content.strip(),
        "keywords": cleaned_keywords,
    }


def get_default_skating_followup_config() -> Dict[str, Any]:
    """Retourne la configuration par defaut du follow-up patinage."""

    return {
        "trigger": SKATING_FOLLOWUP_TRIGGER,
        "from": "dean",
        "to": "elina",
        "channel": "sms",
        "content": SKATING_FOLLOWUP_CONTENT,
        "keywords": SKATING_CONTEXT_KEYWORDS,
    }


def dean_knows_elina_phone_number(
    characters: Dict[str, Dict[str, Any]],
) -> bool:
    """Retourne True si Dean connait le numero d'Elina."""

    dean = characters.get(
        "dean",
        {},
    )
    contacts = dean.get(
        "contacts",
        {},
    )

    if not isinstance(contacts, dict):
        return False

    elina_contact = contacts.get(
        "elina",
        {},
    )

    if not isinstance(elina_contact, dict):
        return False

    return elina_contact.get("phone_number_known") is True


def character_can_text_recipient(
    characters: Dict[str, Dict[str, Any]],
    sender: str,
    recipient: str,
) -> bool:
    """Retourne True si sender connait un canal SMS vers recipient."""

    character = characters.get(
        sender,
        {},
    )

    if not isinstance(character, dict):
        return False

    contacts = character.get(
        "contacts",
        {},
    )

    if not isinstance(contacts, dict):
        return False

    recipient_contact = contacts.get(
        recipient,
        {},
    )

    if not isinstance(recipient_contact, dict):
        return False

    return (
        recipient_contact.get("phone_number_known") is True
        or recipient_contact.get("phone_numbers_exchanged") is True
    )


def characters_share_location(
    world: Dict[str, Any],
    first_character_id: str,
    second_character_id: str,
) -> bool:
    """Verifie si deux personnages sont actuellement au meme endroit."""

    character_locations = world.get(
        "character_locations",
        {},
    )

    if not isinstance(character_locations, dict):
        return False

    first_location = character_locations.get(first_character_id)
    second_location = character_locations.get(second_character_id)

    if not isinstance(first_location, str):
        return False

    if not isinstance(second_location, str):
        return False

    return first_location == second_location


def has_existing_message(
    world: Dict[str, Any],
    sender: str,
    recipient: str,
    trigger: str,
) -> bool:
    """Evite de creer plusieurs fois le meme message narratif."""

    messages = world.get(
        "messages",
        [],
    )

    if not isinstance(messages, list):
        return False

    for message in messages:
        if not isinstance(message, dict):
            continue

        if message.get("from") != sender:
            continue

        if message.get("to") != recipient:
            continue

        if message.get("trigger") != trigger:
            continue

        return True

    return False


def scene_result_contains_message_context(
    scene_result: Dict[str, Any],
    keywords: List[str] | None = None,
    extra_context: Dict[str, Any] | None = None,
) -> bool:
    """Detecte une opportunite claire selon les mots-cles du trigger."""

    if keywords is None:
        keywords = []

    if not keywords:
        return False

    context_values = collect_scene_context_text(scene_result)
    context_values.extend(
        collect_extra_context_text(extra_context)
    )
    context_text = " ".join(context_values)
    normalized_context = normalize_text(context_text)

    return any(
        normalize_text(keyword) in normalized_context
        for keyword in keywords
        if isinstance(keyword, str)
    )


def scene_result_contains_skating_context(
    scene_result: Dict[str, Any],
    keywords: List[str] | None = None,
    extra_context: Dict[str, Any] | None = None,
) -> bool:
    """Detecte une opportunite claire liee au patinage ou au defi."""

    if keywords is None:
        keywords = SKATING_CONTEXT_KEYWORDS

    return scene_result_contains_message_context(
        scene_result,
        keywords,
        extra_context,
    )


def collect_scene_context_text(
    scene_result: Dict[str, Any],
) -> List[str]:
    """Recupere les textes recents utiles pour detecter un contexte."""

    texts = []

    for field_name in ["narration"]:
        values = scene_result.get(
            field_name,
            [],
        )

        if isinstance(values, list):
            texts.extend(
                value
                for value in values
                if isinstance(value, str)
            )

    for field_name in ["memory_updates", "events", "dialogues"]:
        values = scene_result.get(
            field_name,
            [],
        )

        if not isinstance(values, list):
            continue

        for value in values:
            if not isinstance(value, dict):
                continue

            texts.extend(
                text_value
                for text_value in value.values()
                if isinstance(text_value, str)
            )

    return texts


def collect_extra_context_text(
    extra_context: Dict[str, Any] | None,
) -> List[str]:
    """Recupere du contexte externe au SceneResult, comme le player_input."""

    if not isinstance(extra_context, dict):
        return []

    texts = []

    for key in [
        "player_input",
        "scene_history",
    ]:
        value = extra_context.get(key)

        if isinstance(value, str):
            texts.append(value)

    return texts


def build_message_id(
    sender: str,
    recipient: str,
    trigger: str,
    timeline: Dict[str, Any],
) -> str:
    """Construit un identifiant stable et lisible."""

    day = timeline.get(
        "current_day",
        1,
    )
    time = timeline.get(
        "current_time",
        "unknown",
    )
    safe_time = str(time).replace(
        ":",
        "",
    )

    return f"{sender}-{recipient}-{trigger}-d{day}-{safe_time}"


def normalize_text(value: str) -> str:
    """Normalise les accents et la casse pour la detection de mots-cles."""

    normalized = value.lower()
    normalized = unicodedata.normalize(
        "NFKD",
        normalized,
    )
    normalized = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )

    return normalized
