"""Directives HRP runtime ajoutees pendant une partie.

Ces directives sont stockees dans le world runtime. Elles servent a orienter
le prompt sans modifier le scenario canon.
"""

from typing import Any, Dict, List


DIRECTIVE_COMMANDS = {
    "/hrp": "note",
    "/rule": "rule",
    "/context": "context",
}


def parse_runtime_directive_command(
    player_input: str | None,
) -> Dict[str, str] | None:
    """Parse une commande HRP et retourne une directive runtime."""

    if not isinstance(player_input, str):
        return None

    stripped_input = player_input.strip()

    if not stripped_input:
        return None

    for command, directive_type in DIRECTIVE_COMMANDS.items():
        if stripped_input == command:
            return None

        prefix = f"{command} "

        if not stripped_input.startswith(prefix):
            continue

        content = stripped_input[len(prefix):].strip()

        if not content:
            return None

        return {
            "type": directive_type,
            "content": content,
            "scope": "session",
        }

    return None


def add_runtime_directive(
    world: Dict[str, Any],
    directive: Dict[str, str],
    max_directives: int = 20,
) -> Dict[str, Any]:
    """Ajoute une directive HRP dans le world runtime."""

    if not is_valid_runtime_directive(directive):
        return world

    directives = world.get(
        "runtime_directives",
        [],
    )

    if not isinstance(directives, list):
        directives = []

    if has_duplicate_directive(
        directives,
        directive,
    ):
        world["runtime_directives"] = directives
        return world

    directives.append(
        {
            "type": directive["type"],
            "content": directive["content"],
            "scope": directive.get("scope", "session"),
        }
    )

    world["runtime_directives"] = directives[-max_directives:]

    return world


def clear_runtime_directives(
    world: Dict[str, Any],
) -> Dict[str, Any]:
    """Supprime les directives HRP de la partie runtime."""

    world["runtime_directives"] = []

    return world


def get_runtime_directives(
    world: Dict[str, Any],
) -> List[Dict[str, str]]:
    """Retourne les directives runtime valides."""

    directives = world.get(
        "runtime_directives",
        [],
    )

    if not isinstance(directives, list):
        return []

    return [
        directive
        for directive in directives
        if is_valid_runtime_directive(directive)
    ]


def build_runtime_directives_context(
    world: Dict[str, Any],
) -> str:
    """Construit la section de prompt des directives runtime."""

    directives = get_runtime_directives(world)

    if not directives:
        return "No runtime GM directives."

    lines = []

    for directive in directives:
        directive_type = directive["type"]
        content = directive["content"]
        scope = directive.get(
            "scope",
            "session",
        )

        lines.append(
            f"- {directive_type} ({scope}): {content}"
        )

    return "\n".join(lines)


def has_duplicate_directive(
    directives: List[Any],
    directive: Dict[str, str],
) -> bool:
    """Evite d'ajouter deux fois la meme directive."""

    for existing_directive in directives:
        if not isinstance(existing_directive, dict):
            continue

        if existing_directive.get("type") != directive.get("type"):
            continue

        if existing_directive.get("content") != directive.get("content"):
            continue

        return True

    return False


def is_valid_runtime_directive(
    directive: Any,
) -> bool:
    """Valide une directive HRP simple."""

    if not isinstance(directive, dict):
        return False

    directive_type = directive.get(
        "type",
    )
    content = directive.get(
        "content",
    )

    if directive_type not in DIRECTIVE_COMMANDS.values():
        return False

    return isinstance(content, str) and bool(content.strip())
