# Permet de charger les variables du fichier .env
from dotenv import load_dotenv
# Permet d'accéder aux variables d'environnement
import os
# SDK openai
from openai import OpenAI

# Chargement automatique du fichier .env
load_dotenv()

# Récupération de la clef API
api_key = os.getenv("OPENAI_API_KEY")

# On vérifie qu'elle existe
if not api_key: raise ValueError("OPENAI_API_KEY is missing")

# Création du client OpenAI
client = OpenAI(api_key=api_key)

def generate_text(prompt: str) -> str: 
    # Envoie un prompt au modèle OpenAI et retourne la réponse texte
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        # Temperature : plus c'est haut plus c'est créatif, plus c'est bas plus c'est stable
        temperature=0.4
    )

    return response.choices[0].message.content