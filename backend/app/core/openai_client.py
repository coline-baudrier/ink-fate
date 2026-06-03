import os

from dotenv import load_dotenv
from openai import OpenAI


# Charge automatiquement les variables du fichier .env.
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY is missing")

client = OpenAI(api_key=api_key)


def generate_text(prompt: str) -> str:
    """Envoie un prompt au modele OpenAI et retourne la reponse texte."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        # Plus la temperature est basse, plus la reponse est stable.
        temperature=0.4,
    )

    return response.choices[0].message.content
