from backend.app.core.runtime_directives import (
    add_runtime_directive,
    build_runtime_directives_context,
    clear_runtime_directives,
    get_runtime_directives,
    parse_runtime_directive_command,
)


def test_parse_runtime_directive_command_from_hrp():
    assert parse_runtime_directive_command(
        "/hrp Dean doit rester plus subtil."
    ) == {
        "type": "note",
        "content": "Dean doit rester plus subtil.",
        "scope": "session",
    }


def test_parse_runtime_directive_command_from_rule():
    assert parse_runtime_directive_command(
        "/rule Le ton doit rester slow burn."
    ) == {
        "type": "rule",
        "content": "Le ton doit rester slow burn.",
        "scope": "session",
    }


def test_parse_runtime_directive_command_from_context():
    assert parse_runtime_directive_command(
        "/context Elina est fatiguee mais le cache."
    ) == {
        "type": "context",
        "content": "Elina est fatiguee mais le cache.",
        "scope": "session",
    }


def test_parse_runtime_directive_command_ignores_empty_or_rp_input():
    assert parse_runtime_directive_command("/hrp") is None
    assert parse_runtime_directive_command("Je vais au dortoir.") is None
    assert parse_runtime_directive_command(None) is None


def test_add_runtime_directive_stores_valid_directive():
    world = {}

    world = add_runtime_directive(
        world,
        {
            "type": "rule",
            "content": "Favoriser une tension plus subtile.",
            "scope": "session",
        },
    )

    assert world["runtime_directives"] == [
        {
            "type": "rule",
            "content": "Favoriser une tension plus subtile.",
            "scope": "session",
        }
    ]


def test_add_runtime_directive_avoids_duplicates():
    world = {
        "runtime_directives": [
            {
                "type": "rule",
                "content": "Rester slow burn.",
                "scope": "session",
            }
        ]
    }

    world = add_runtime_directive(
        world,
        {
            "type": "rule",
            "content": "Rester slow burn.",
            "scope": "session",
        },
    )

    assert len(world["runtime_directives"]) == 1


def test_get_runtime_directives_filters_invalid_entries():
    world = {
        "runtime_directives": [
            {
                "type": "rule",
                "content": "Rester subtil.",
                "scope": "session",
            },
            {
                "type": "unknown",
                "content": "Invalid.",
            },
            "invalid",
        ]
    }

    assert get_runtime_directives(world) == [
        {
            "type": "rule",
            "content": "Rester subtil.",
            "scope": "session",
        }
    ]


def test_clear_runtime_directives():
    world = {
        "runtime_directives": [
            {
                "type": "rule",
                "content": "Rester subtil.",
            }
        ]
    }

    assert clear_runtime_directives(world)["runtime_directives"] == []


def test_build_runtime_directives_context_without_directives():
    assert build_runtime_directives_context({}) == "No runtime GM directives."


def test_build_runtime_directives_context_with_directives():
    world = {
        "runtime_directives": [
            {
                "type": "context",
                "content": "Elina est fatiguee.",
                "scope": "session",
            }
        ]
    }

    assert build_runtime_directives_context(world) == (
        "- context (session): Elina est fatiguee."
    )
