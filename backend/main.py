"""Point d'entree du prototype CLI Ink & Fate.

Ce fichier orchestre la boucle principale :
charger les donnees, generer une scene, lire l'action du joueur,
appliquer les relations et afficher le resultat.
"""

from pathlib import Path
from typing import Any, Dict
import argparse
import os

from app.core.json_loader import load_json
from app.core.renderer import render_scene_result, scene_result_to_entries
from app.core.runtime_directives import (
    add_runtime_directive,
    clear_runtime_directives,
    get_runtime_directives,
    parse_runtime_directive_command,
)
from app.core.runtime_save import (
    DEFAULT_SAVE_ID,
    build_runtime_save_path,
    clear_runtime_save,
    load_runtime_characters,
    load_runtime_world,
    normalize_save_id,
    save_runtime_state,
)
from app.core.scene_context import build_scene_context
from app.core.prompt_builder import scene_history_to_text
from app.core.scene_pipeline import generate_scene
from app.core.message_engine import (
    append_pending_messages,
    apply_player_sms_reply,
    generate_pending_messages,
    get_player_messages,
    mark_player_messages_read,
    parse_sms_reply_command,
)
from app.core.world_engine import (
    rebuild_scene_context,
    update_world_after_turn,
)
from app.core.character_state_engine import update_characters_after_scene
from app.core.relationship_engine import apply_daily_relationship_decay

PROJECT_ROOT = Path(__file__).resolve().parents[1]
UNIVERSE_PATH = PROJECT_ROOT / "data" / "universes" / "off-campus"

SCENE_HISTORY_MAX_STORED = 20


def _append_scene_turn(
    turns: list[dict],
    player_input: str | None,
    scene_text: str,
    entries: list[dict] | None = None,
) -> list[dict]:
    """Ajoute un tour a l'historique et tronque a SCENE_HISTORY_MAX_STORED."""

    turn: dict = {
        "player_input": player_input,
        "scene_text": scene_text,
    }

    if entries is not None:
        turn["entries"] = entries

    turns.append(turn)

    return turns[-SCENE_HISTORY_MAX_STORED:]


def parse_args() -> argparse.Namespace:
    """Lit les options CLI du prototype."""

    parser = argparse.ArgumentParser(
        description="Ink & Fate CLI prototype",
    )
    parser.add_argument(
        "--save-id",
        default=None,
        help="Runtime save id to load and write.",
    )

    return parser.parse_args()


def resolve_save_id(
    cli_save_id: str | None = None,
) -> str:
    """Determine la sauvegarde runtime a utiliser."""

    if cli_save_id:
        return normalize_save_id(cli_save_id)

    env_save_id = os.getenv(
        "INK_FATE_SAVE_ID",
        DEFAULT_SAVE_ID,
    )

    return normalize_save_id(env_save_id)


def print_project_header(
    world: Dict[str, Any],
    save_id: str,
) -> None:
    """Affiche le titre du projet et le nom de l'univers charge."""

    print("Ink & Fate")
    print("----------")
    print(f"Universe: {world['universe']['name']}")
    print(f"Save: {save_id}")


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


def print_new_player_messages(
    messages: list[Dict[str, Any]],
    world: Dict[str, Any],
) -> None:
    """Affiche les nouveaux messages non lus envoyes au joueur."""

    player_character = world["player_character"]

    for message in messages:
        if message.get("to") != player_character:
            continue

        if message.get("status") != "unread":
            continue

        sender = message.get(
            "from",
            "Unknown",
        )
        content = message.get(
            "content",
            "",
        )

        print()
        print(f"New message from {sender.title()}:")
        print(f'"{content}"')


def print_player_message_inbox(
    world: Dict[str, Any],
) -> None:
    """Affiche les messages deja stockes pour le personnage joueur."""

    messages = get_player_messages(world)

    print()
    print("Messages")
    print("--------")

    if not messages:
        print("No messages yet.")
        return

    for message in messages:
        sender = message.get(
            "from",
            "Unknown",
        )
        status = message.get(
            "status",
            "unknown",
        )
        sent_day = message.get(
            "sent_at_day",
            "?",
        )
        sent_time = message.get(
            "sent_at_time",
            "??:??",
        )
        content = message.get(
            "content",
            "",
        )

        print(f"[{status}] Day {sent_day}, {sent_time} - {sender.title()}:")
        print(f'"{content}"')


def print_runtime_directives(
    world: Dict[str, Any],
) -> None:
    """Affiche les directives HRP actives."""

    directives = get_runtime_directives(world)

    print()
    print("Runtime directives")
    print("------------------")

    if not directives:
        print("No runtime directives.")
        return

    for index, directive in enumerate(
        directives,
        start=1,
    ):
        directive_type = directive.get(
            "type",
            "note",
        )
        content = directive.get(
            "content",
            "",
        )

        print(f"{index}. [{directive_type}] {content}")


def print_sms_reply_result(
    result: Dict[str, Any],
) -> None:
    """Affiche le resultat d'une commande de reponse SMS."""

    print()

    if result.get("sent") is not True:
        print("SMS not sent: no valid SMS access to that character.")
        return

    message = result.get(
        "message",
        {},
    )

    recipient = message.get(
        "to",
        "Unknown",
    )
    content = message.get(
        "content",
        "",
    )

    print(f"SMS sent to {recipient.title()}:")
    print(f'"{content}"')

    npc_replies = result.get(
        "npc_replies",
        [],
    )

    if isinstance(npc_replies, list):
        for reply in npc_replies:
            if not isinstance(reply, dict):
                continue

            sender = reply.get(
                "from",
                "Unknown",
            )
            reply_content = reply.get(
                "content",
                "",
            )

            print()
            print(f"New message from {sender.title()}:")
            print(f'"{reply_content}"')


def main() -> None:
    """Lance le prototype CLI."""

    args = parse_args()
    save_id = resolve_save_id(args.save_id)
    runtime_save_path = build_runtime_save_path(
        PROJECT_ROOT,
        "off-campus",
        save_id,
    )

    # Chargement initial : canon si aucune sauvegarde runtime n'existe.
    world = load_runtime_world(
        UNIVERSE_PATH / "world.json",
        runtime_save_path,
    )
    scenario = load_json(UNIVERSE_PATH / "scenario.json")

    character_ids = world["characters"]

    characters = load_runtime_characters(
        UNIVERSE_PATH / "characters",
        character_ids,
        runtime_save_path,
    )

    scene_context = build_scene_context(
        world,
        characters,
    )

    print_project_header(
        world,
        save_id,
    )
    print_loaded_characters(characters)
    print_active_scene(scene_context)

    scene_history_turns: list[dict] = world.get(
        "scene_history",
        [],
    )

    if scene_history_turns:
        last_scene_text = scene_history_turns[-1].get("scene_text", "")
        print()
        print("Last scene")
        print("----------")
        print(last_scene_text)
    else:
        opening_scene = generate_scene(
            world,
            scenario,
            scene_context,
        )

        print_rendered_scene(
            "Opening scene",
            opening_scene,
        )

        scene_history_turns = _append_scene_turn(
            scene_history_turns,
            None,
            render_scene_result(opening_scene),
            scene_result_to_entries(opening_scene, "opening"),
        )
        world["scene_history"] = scene_history_turns
        save_runtime_state(
            runtime_save_path,
            world,
            characters,
        )

    while True:
        print()
        player_input = input("Your action > ")

        if player_input.lower() in ["quit", "exit"]:
            print("Fin de la session.")
            break

        if player_input.lower() in ["messages", "sms", "inbox"]:
            print_player_message_inbox(world)
            world = mark_player_messages_read(world)
            save_runtime_state(
                runtime_save_path,
                world,
                characters,
            )
            continue

        if player_input.lower() in ["directives", "rules", "hrp"]:
            print_runtime_directives(world)
            continue

        if player_input.lower() in ["clear_directives", "clear rules"]:
            world = clear_runtime_directives(world)
            save_runtime_state(
                runtime_save_path,
                world,
                characters,
            )
            print("Runtime directives cleared.")
            continue

        sms_reply = parse_sms_reply_command(player_input)

        if sms_reply:
            world, sms_result = apply_player_sms_reply(
                world,
                characters,
                sms_reply,
            )
            save_runtime_state(
                runtime_save_path,
                world,
                characters,
            )
            print_sms_reply_result(sms_result)
            continue

        runtime_directive = parse_runtime_directive_command(player_input)

        if runtime_directive:
            world = add_runtime_directive(
                world,
                runtime_directive,
            )
            save_runtime_state(
                runtime_save_path,
                world,
                characters,
            )
            print("Runtime directive added.")
            continue

        if player_input.lower() in ["reset"]:
            clear_runtime_save(
                runtime_save_path,
            )

            print(
                f"Sauvegarde runtime '{save_id}' supprimee. "
                "Le canon reste intact."
            )
            break

        next_scene = generate_scene(
            world,
            scenario,
            scene_context,
            player_input,
            scene_history_turns,
        )

        characters = update_characters_after_scene(
            next_scene,
            characters,
        )

        day_before = world["timeline"]["current_day"]

        world = update_world_after_turn(
            world,
            characters,
            next_scene,
            scenario,
        )

        days_passed = world["timeline"]["current_day"] - day_before

        if days_passed > 0:
            characters = apply_daily_relationship_decay(
                characters,
                days_passed,
            )

        new_messages = generate_pending_messages(
            world,
            characters,
            next_scene,
            scenario,
            {
                "player_input": player_input,
                "scene_history": scene_history_to_text(scene_history_turns),
            },
        )
        world = append_pending_messages(
            world,
            new_messages,
            scenario,
        )

        turn_id = f"turn_{len(scene_history_turns)}"
        scene_history_turns = _append_scene_turn(
            scene_history_turns,
            player_input,
            render_scene_result(next_scene),
            scene_result_to_entries(next_scene, turn_id),
        )
        world["scene_history"] = scene_history_turns

        save_runtime_state(
            runtime_save_path,
            world,
            characters,
        )

        scene_context = rebuild_scene_context(
            world,
            characters,
        )

        print_rendered_scene(
            "Next scene",
            next_scene,
        )

        print_new_player_messages(
            new_messages,
            world,
        )


if __name__ == "__main__":
    main()
