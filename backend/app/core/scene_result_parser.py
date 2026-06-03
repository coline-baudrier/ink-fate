import json
from typing import Any, Dict


def parse_scene_result(response_text: str) -> Dict[str, Any]:
    """Parse la reponse JSON du LLM et retourne un dictionnaire Python."""

    try:
        # json.loads transforme une chaine JSON en objet Python.
        return json.loads(response_text)
    except json.JSONDecodeError as error:
        print()
        print("JSON parsing error:")
        print(error)

        raise
