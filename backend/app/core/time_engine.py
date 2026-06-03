from typing import Any, Dict


def advance_time(
    world: Dict[str, Any],
    minutes: int = 5,
) -> Dict[str, Any]:
    """
    Avance l'heure du monde.
    """

    current_time = world["timeline"]["current_time"]

    hours, mins = current_time.split(":")

    total_minutes = (
        int(hours) * 60
        + int(mins)
    )

    total_minutes += minutes

    new_hours = (total_minutes // 60) % 24
    new_minutes = total_minutes % 60

    world["timeline"]["current_time"] = (
        f"{new_hours:02}:{new_minutes:02}"
    )

    return world