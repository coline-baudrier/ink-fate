"""Application and prompt context for character contact access."""

from typing import Any, Dict


CONTACT_FIELDS = {
    "phone_number_known",
    "phone_numbers_exchanged",
    "instagram_connected",
}


def build_default_contact() -> Dict[str, bool]:
    """Return the default contact state between two characters."""

    return {
        "phone_number_known": False,
        "phone_numbers_exchanged": False,
        "instagram_connected": False,
    }


def apply_contact_updates(
    scene_result: Dict[str, Any],
    characters: Dict[str, Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """Apply persistent contact access updates to characters."""

    contact_updates = scene_result.get(
        "contact_updates",
        [],
    )

    for update in contact_updates:
        source_id = update.get("source")
        target_id = update.get("target")
        changes = update.get("changes", {})

        if source_id not in characters:
            continue

        if target_id not in characters:
            continue

        if not isinstance(changes, dict):
            continue

        source_contact = get_or_create_contact(
            characters,
            source_id,
            target_id,
        )

        for field, value in changes.items():
            if field not in CONTACT_FIELDS:
                continue

            if not isinstance(value, bool):
                continue

            source_contact[field] = value

            if field == "phone_number_known" and value:
                source_contact["phone_number_known"] = True

            if field == "phone_numbers_exchanged" and value:
                mirror_phone_number_exchange(
                    characters,
                    source_id,
                    target_id,
                )

            if field == "instagram_connected" and value:
                mirror_instagram_connection(
                    characters,
                    source_id,
                    target_id,
                )

    return characters


def get_or_create_contact(
    characters: Dict[str, Dict[str, Any]],
    source_id: str,
    target_id: str,
) -> Dict[str, bool]:
    """Return source -> target contact state, creating it if needed."""

    source_character = characters[source_id]
    contacts = source_character.setdefault(
        "contacts",
        {},
    )

    contact = contacts.setdefault(
        target_id,
        build_default_contact(),
    )

    for field, default_value in build_default_contact().items():
        contact.setdefault(field, default_value)

    return contact


def mirror_phone_number_exchange(
    characters: Dict[str, Dict[str, Any]],
    source_id: str,
    target_id: str,
) -> None:
    """A phone number exchange gives both characters the number."""

    source_contact = get_or_create_contact(
        characters,
        source_id,
        target_id,
    )
    target_contact = get_or_create_contact(
        characters,
        target_id,
        source_id,
    )

    source_contact["phone_number_known"] = True
    source_contact["phone_numbers_exchanged"] = True
    target_contact["phone_number_known"] = True
    target_contact["phone_numbers_exchanged"] = True


def mirror_instagram_connection(
    characters: Dict[str, Dict[str, Any]],
    source_id: str,
    target_id: str,
) -> None:
    """An accepted Instagram connection is mutual in this MVP."""

    source_contact = get_or_create_contact(
        characters,
        source_id,
        target_id,
    )
    target_contact = get_or_create_contact(
        characters,
        target_id,
        source_id,
    )

    source_contact["instagram_connected"] = True
    target_contact["instagram_connected"] = True


def build_contact_context(
    scene_context: Dict[str, Any],
) -> str:
    """Build readable contact access context for active participants."""

    lines = []

    for character in scene_context["participants"]:
        character_id = character["id"]
        contacts = character.get(
            "contacts",
            {},
        )

        if not isinstance(contacts, dict):
            continue

        for target_id, contact in contacts.items():
            if not isinstance(contact, dict):
                continue

            phone_number_known = bool(
                contact.get(
                    "phone_number_known",
                    False,
                )
            )
            phone_numbers_exchanged = bool(
                contact.get(
                    "phone_numbers_exchanged",
                    False,
                )
            )
            instagram_connected = bool(
                contact.get(
                    "instagram_connected",
                    False,
                )
            )

            can_text_or_call = (
                phone_number_known
                or phone_numbers_exchanged
            )
            can_dm = instagram_connected

            lines.append(
                f"- {character_id} -> {target_id}: "
                f"phone known: {format_bool(phone_number_known)}, "
                f"numbers exchanged: {format_bool(phone_numbers_exchanged)}, "
                f"instagram connected: {format_bool(instagram_connected)}, "
                f"can text/call: {format_bool(can_text_or_call)}, "
                f"can DM: {format_bool(can_dm)}"
            )

    if not lines:
        return "No contact access recorded yet."

    return "\n".join(lines)


def format_bool(value: bool) -> str:
    """Return a compact prompt-friendly boolean label."""

    if value:
        return "yes"

    return "no"
