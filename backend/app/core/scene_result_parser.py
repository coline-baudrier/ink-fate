import json
from typing import Any, Dict

# Fonction pour parser la réponse JSON du LLM et retourne un dictionnaire Python
def parse_scene_result(response_text: str,) -> Dict[str, Any]:
    try: 
        # Transforme le JSON texte en dictionnaire Python
        result = json.loads(response_text)

        return result
    
    except json.JSONDecodeErro as error:

        print()
        print("JSON parsing error : ")
        print(error)

        raise
