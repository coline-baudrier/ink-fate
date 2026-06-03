# Prompt Builder

Le prompt builder construit le contexte envoye au LLM.

Il ne doit jamais envoyer une demande vague comme :

```md
Continue l'histoire.
```

Il doit envoyer un contexte structure qui permet au LLM de generer une scene coherente et exploitable.

## Objectif

Transformer :

```json
{
  "world_state": {},
  "scene_context": {},
  "player_input": "",
  "relevant_memories": []
}
```

en prompt narratif clair, stable et complet.

## Pipeline

```md
WorldState
-> Active Scene
-> Relevant Characters
-> Relevant Relationships
-> Relevant Memories
-> Player Input
-> Narrative Rules
-> Expected SceneResult Format
-> LLM
```

## Contenu Du Prompt

Le prompt doit contenir :

- role du LLM ;
- univers ;
- date et heure ;
- lieu actuel ;
- description du lieu ;
- personnages presents ;
- objectifs actuels des personnages ;
- relations utiles ;
- souvenirs pertinents ;
- action du joueur ;
- regles narratives ;
- format JSON attendu.

## Regle De Cout Et De Clarte

Le prompt builder ne doit jamais envoyer toute la base.

Il doit selectionner uniquement :

- les personnages presents ;
- les relations pertinentes ;
- les souvenirs pertinents ;
- les evenements utiles a la scene.

Envoyer trop d'informations augmente les couts, brouille le contexte et augmente les incoherences.

## Regles Narratives

Le prompt doit rappeler au LLM :

```md
- Ecrire en francais.
- Respecter la personnalite des personnages.
- Garder des emotions credibles.
- Ne pas forcer la romance.
- Ne pas inventer de lore majeur.
- Ne pas controler le personnage joueur.
- Ne pas narrer les pensees du joueur.
- Ne pas ecrire de dialogue pour le joueur.
- Retourner uniquement un JSON valide.
```

## Role Systemique Du LLM

Le role de base :

```md
You are the narrative engine of Ink & Fate.

Your role is to generate coherent, emotionally believable and character-consistent scenes inside a living narrative world.

Characters must behave according to their personality, memories, goals, emotions and relationships.

You must always return a valid JSON SceneResult object.
```

## Etat Courant

Exemple :

```json
{
  "date": "2026-09-01",
  "time": "10:00",
  "location": "campus"
}
```

## Scene Active

Exemple :

```json
{
  "participants": ["dean", "beau", "elina"]
}
```

## Contexte Personnage

Le prompt doit contenir seulement les personnages utiles a la scene.

Exemple :

```json
{
  "id": "dean",
  "identity": {
    "first_name": "Dean",
    "last_name": "Di Laurentis"
  },
  "personality": {
    "charisma": 95,
    "humor": 95,
    "loyalty": 90
  },
  "current_goals": ["tease_beau"]
}
```

## Souvenirs Pertinents

Exemple :

```json
[
  {
    "owner": "dean",
    "content": "Beau is protective of Elina.",
    "tags": ["beau", "elina"]
  }
]
```

Pour le MVP, la recuperation peut rester simple.

Plus tard, elle devra tenir compte :

- du personnage present ;
- des tags ;
- de l'importance ;
- de la recence ;
- du type de souvenir.

## Action Joueur

Exemple :

```md
Player action:
Je reprends ma valise et je leve les yeux au ciel.
```

Le LLM peut decrire les actions visibles du joueur, mais il ne doit pas ajouter de pensees, emotions ou dialogues non fournis.

## Format Attendu

Le prompt doit inclure le format `SceneResult`.

```json
{
  "scene": {
    "location": "",
    "time": "",
    "participants": []
  },
  "narration": [],
  "dialogues": [],
  "actions": [],
  "events": [],
  "world_updates": {},
  "memory_updates": [],
  "relationship_updates": [],
  "next_hooks": []
}
```

## Determinisme

Le prompt builder doit etre aussi deterministe que possible.

Pour un meme etat du monde et une meme action joueur, la structure logique du prompt doit rester stable. Cela rend le moteur plus facile a tester, valider et corriger.
