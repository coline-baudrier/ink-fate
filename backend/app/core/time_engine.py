from typing import Any, Dict


def advance_time(
    world: Dict[str, Any],
    minutes: int = 5,
) -> Dict[str, Any]:
    """
    Avance l'heure du monde et le jour si minuit est depasse.
    """

    current_time = world["timeline"]["current_time"]

    hours, mins = current_time.split(":")

    total_minutes = (
        int(hours) * 60
        + int(mins)
    )

    total_minutes += minutes

    days_passed = total_minutes // (24 * 60)
    new_hours = (total_minutes // 60) % 24
    new_minutes = total_minutes % 60

    world["timeline"]["current_time"] = (
        f"{new_hours:02}:{new_minutes:02}"
    )

    if days_passed > 0:
        current_day = world["timeline"].get(
            "current_day",
            1,
        )

        world["timeline"]["current_day"] = (
            current_day + days_passed
        )

    return world
