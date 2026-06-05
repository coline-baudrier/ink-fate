import asyncio
import json
import re
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.api.schemas import (
    ActionRequest,
    ActionResponse,
    GameStartResponse,
    MessageEntry,
    SmsRequest,
    SmsResponse,
    StoryEntry,
)
from app.core.character_state_engine import update_characters_after_scene
from app.core.json_loader import load_json
from app.core.message_engine import (
    append_pending_messages,
    apply_player_sms_reply,
    generate_pending_messages,
    get_player_messages,
)
from app.core.prompt_builder import scene_history_to_text
from app.core.relationship_engine import apply_daily_relationship_decay
from app.core.renderer import render_scene_result, scene_result_to_entries
from app.core.runtime_save import (
    DEFAULT_SAVE_ID,
    build_runtime_save_path,
    load_runtime_characters,
    load_runtime_world,
    save_runtime_state,
)
from app.core.scene_context import build_scene_context
from app.core.scene_pipeline import generate_scene
from app.core.world_engine import update_world_after_turn

router = APIRouter(prefix="/game", tags=["game"])

PROJECT_ROOT = Path(__file__).resolve().parents[3]
UNIVERSE_PATH = PROJECT_ROOT / "data" / "universes" / "off-campus"

SCENE_HISTORY_MAX_STORED = 20


def _load_state(
    save_id: str = DEFAULT_SAVE_ID,
) -> tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any], Path]:
    """Charge l'etat complet du jeu depuis le disque."""

    runtime_save_path = build_runtime_save_path(
        PROJECT_ROOT,
        "off-campus",
        save_id,
    )
    world = load_runtime_world(
        UNIVERSE_PATH / "world.json",
        runtime_save_path,
    )
    scenario = load_json(UNIVERSE_PATH / "scenario.json")
    character_ids = world.get("characters", [])
    if not isinstance(character_ids, list):
        character_ids = []

    characters = load_runtime_characters(
        UNIVERSE_PATH / "characters",
        character_ids,
        runtime_save_path,
    )
    scene_context = build_scene_context(world, characters)

    return world, scenario, characters, scene_context, runtime_save_path


def _append_turn(
    turns: list[dict],
    player_input: str | None,
    scene_text: str,
    entries: list[dict],
) -> list[dict]:
    """Ajoute un tour et tronque l'historique."""

    turns.append(
        {
            "player_input": player_input,
            "scene_text": scene_text,
            "entries": entries,
        }
    )

    return turns[-SCENE_HISTORY_MAX_STORED:]


def _message_to_entry(message: Dict[str, Any]) -> MessageEntry:
    """Convertit un message world en MessageEntry."""

    return MessageEntry(
        id=message.get("id", ""),
        sender=message.get("from", ""),
        recipient=message.get("to", ""),
        content=message.get("content", ""),
        status=message.get("status", "unread"),
        day=message.get("sent_at_day", 1),
        time=message.get("sent_at_time", "00:00"),
    )


def _get_player_message_entries(
    world: Dict[str, Any],
) -> list[MessageEntry]:
    """Retourne les messages adresses au joueur."""

    player_id = world.get("player_character", "")
    all_messages = get_player_messages(world)

    return [
        _message_to_entry(m)
        for m in all_messages
        if m.get("to") == player_id
    ]


@router.post("/start", response_model=GameStartResponse)
def start_game() -> GameStartResponse:
    """Charge ou demarre une partie. Renvoie la derniere scene connue."""

    world, scenario, characters, scene_context, runtime_save_path = _load_state()
    scene_history_turns: list[dict] = world.get("scene_history", [])

    if scene_history_turns:
        last_turn = scene_history_turns[-1]
        raw_entries = last_turn.get("entries") or []

        if not raw_entries and last_turn.get("scene_text"):
            raw_entries = [
                {
                    "id": "last_n0",
                    "type": "narration",
                    "character": None,
                    "text": last_turn["scene_text"],
                }
            ]

        entries: list[StoryEntry] = []

        if last_turn.get("player_input"):
            entries.append(
                StoryEntry(
                    id="last_player",
                    type="player",
                    character=world.get("player_character", "elina").title(),
                    text=last_turn["player_input"],
                )
            )

        entries += [StoryEntry(**e) for e in raw_entries]

    else:
        opening_scene = generate_scene(world, scenario, scene_context)
        raw_entries = scene_result_to_entries(opening_scene, "opening")
        scene_history_turns = _append_turn(
            scene_history_turns,
            None,
            render_scene_result(opening_scene),
            raw_entries,
        )
        world["scene_history"] = scene_history_turns
        save_runtime_state(runtime_save_path, world, characters)
        entries = [StoryEntry(**e) for e in raw_entries]

    messages = _get_player_message_entries(world)

    player_id = world.get("player_character", "elina")
    player_char = characters.get(player_id, {})
    known_contacts = [
        cid
        for cid, contact in player_char.get("contacts", {}).items()
        if isinstance(contact, dict)
        and (contact.get("phone_number_known") or contact.get("phone_numbers_exchanged"))
    ]

    return GameStartResponse(
        scenario=world["universe"]["name"],
        player_character=player_id,
        entries=entries,
        messages=messages,
        contacts=known_contacts,
        current_date=world["timeline"].get("current_date", ""),
        current_time=world["timeline"].get("current_time", ""),
    )


@router.post("/action", response_model=ActionResponse)
def player_action(request: ActionRequest) -> ActionResponse:
    """Traite une action joueur et renvoie la scene suivante."""

    player_input = request.text.strip()

    if not player_input:
        raise HTTPException(status_code=400, detail="Player input cannot be empty.")

    world, scenario, characters, scene_context, runtime_save_path = _load_state()
    scene_history_turns: list[dict] = world.get("scene_history", [])

    next_scene = generate_scene(
        world,
        scenario,
        scene_context,
        player_input,
        scene_history_turns,
    )

    characters = update_characters_after_scene(next_scene, characters)

    day_before = world["timeline"]["current_day"]
    world = update_world_after_turn(world, characters, next_scene, scenario)
    days_passed = world["timeline"]["current_day"] - day_before

    if days_passed > 0:
        characters = apply_daily_relationship_decay(characters, days_passed)

    new_raw_messages = generate_pending_messages(
        world,
        characters,
        next_scene,
        scenario,
        {
            "player_input": player_input,
            "scene_history": scene_history_to_text(scene_history_turns),
        },
    )
    world = append_pending_messages(world, new_raw_messages, scenario)

    turn_id = f"turn_{len(scene_history_turns)}"
    raw_entries = scene_result_to_entries(next_scene, turn_id)
    scene_history_turns = _append_turn(
        scene_history_turns,
        player_input,
        render_scene_result(next_scene),
        raw_entries,
    )
    world["scene_history"] = scene_history_turns

    save_runtime_state(runtime_save_path, world, characters)

    player_id = world.get("player_character", "")
    player_entry = StoryEntry(
        id=f"{turn_id}_player",
        type="player",
        character=player_id.title(),
        text=player_input,
    )
    scene_entries = [StoryEntry(**e) for e in raw_entries]

    new_message_entries = [
        _message_to_entry(m)
        for m in new_raw_messages
        if m.get("to") == player_id
    ]

    return ActionResponse(
        entries=[player_entry] + scene_entries,
        new_messages=new_message_entries,
    )


@router.post("/action/stream")
async def player_action_stream(request: ActionRequest) -> StreamingResponse:
    """Traite une action joueur et stream la scene via SSE."""

    player_input = request.text.strip()
    if not player_input:
        raise HTTPException(status_code=400, detail="Player input cannot be empty.")

    world, scenario, characters, scene_context, runtime_save_path = _load_state()
    scene_history_turns: list[dict] = world.get("scene_history", [])

    def compute() -> tuple[list[dict], list[MessageEntry]]:
        next_scene = generate_scene(world, scenario, scene_context, player_input, scene_history_turns)
        updated_chars = update_characters_after_scene(next_scene, characters)
        day_before = world["timeline"]["current_day"]
        updated_world = update_world_after_turn(world, updated_chars, next_scene, scenario)
        days_passed = updated_world["timeline"]["current_day"] - day_before
        if days_passed > 0:
            updated_chars = apply_daily_relationship_decay(updated_chars, days_passed)

        # Detect "> texto" syntax and record the outgoing SMS in the world BEFORE
        # generate_pending_messages so NPCs can generate a reply in the same turn.
        player_id = updated_world.get("player_character", "")
        sms_outgoing: list[dict] = []
        sms_match = re.search(r">\s+(.+)", player_input)
        if sms_match:
            sms_text = sms_match.group(1).strip()
            participants = next_scene.get("scene", {}).get("participants", [])
            recipient = None
            # Try to find recipient name mentioned before the '>'
            before_arrow = player_input[: player_input.index(">")].lower()
            for char_id in updated_world.get("characters", []):
                if char_id != player_id and char_id in before_arrow:
                    recipient = char_id
                    break
            # Fall back to first non-player scene participant
            if not recipient:
                recipient = next((p for p in participants if p != player_id), None)
            if recipient:
                turn_id_sms = f"turn_{len(scene_history_turns)}"
                outgoing_msg = {
                    "id": f"{turn_id_sms}_sms_out",
                    "from": player_id,
                    "to": recipient,
                    "content": sms_text,
                    "status": "sent",
                    "sent_at_day": updated_world["timeline"]["current_day"],
                    "sent_at_time": updated_world["timeline"].get("current_time", "00:00"),
                }
                updated_world.setdefault("messages", []).append(outgoing_msg)
                sms_outgoing.append(outgoing_msg)

        new_raw_msgs = generate_pending_messages(
            updated_world,
            updated_chars,
            next_scene,
            scenario,
            {"player_input": player_input, "scene_history": scene_history_to_text(scene_history_turns)},
        )
        updated_world = append_pending_messages(updated_world, new_raw_msgs, scenario)
        turn_id = f"turn_{len(scene_history_turns)}"
        raw_entries = scene_result_to_entries(next_scene, turn_id)
        new_turns = _append_turn(
            scene_history_turns, player_input, render_scene_result(next_scene), raw_entries
        )
        updated_world["scene_history"] = new_turns
        save_runtime_state(runtime_save_path, updated_world, updated_chars)
        # Outgoing SMS first so they appear before any NPC reply
        msgs = [_message_to_entry(m) for m in sms_outgoing]
        msgs += [_message_to_entry(m) for m in new_raw_msgs if m.get("to") == player_id]
        timeline = updated_world.get("timeline", {})
        return raw_entries, msgs, timeline.get("current_date", ""), timeline.get("current_time", "")

    raw_entries, new_message_entries, updated_date, updated_time = await asyncio.to_thread(compute)
    import logging
    logging.getLogger("uvicorn").info(f"[stream] {len(raw_entries)} entries à envoyer")

    async def event_gen():
        for entry in raw_entries:
            yield f"data: {json.dumps({'type': 'entry', 'entry': entry})}\n\n"
            await asyncio.sleep(0.18)
        yield f"data: {json.dumps({'type': 'done', 'new_messages': [m.model_dump() for m in new_message_entries], 'current_date': updated_date, 'current_time': updated_time})}\n\n"

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@router.post("/reset")
def reset_game() -> dict:
    """Supprime la sauvegarde runtime et repart du world canon."""

    runtime_save_path = build_runtime_save_path(PROJECT_ROOT, "off-campus", DEFAULT_SAVE_ID)

    from app.core.runtime_save import clear_runtime_save
    clear_runtime_save(runtime_save_path)

    return {"reset": True}


@router.get("/messages", response_model=list[MessageEntry])
def get_messages() -> list[MessageEntry]:
    """Retourne tous les messages adresses au joueur."""

    world, _, _, _, _ = _load_state()

    return _get_player_message_entries(world)


@router.post("/sms", response_model=SmsResponse)
def send_sms(request: SmsRequest) -> SmsResponse:
    """Envoie un SMS du joueur a un personnage."""

    world, _, characters, _, runtime_save_path = _load_state()

    sms_command = {
        "to": request.to,
        "content": request.text,
    }

    world, result = apply_player_sms_reply(world, characters, sms_command)
    save_runtime_state(runtime_save_path, world, characters)

    npc_replies = [
        _message_to_entry(r)
        for r in result.get("npc_replies", [])
        if isinstance(r, dict)
    ]

    raw_player_msg = result.get("message")
    player_message = _message_to_entry(raw_player_msg) if isinstance(raw_player_msg, dict) else None

    return SmsResponse(
        sent=result.get("sent", False),
        player_message=player_message,
        npc_replies=npc_replies,
    )
