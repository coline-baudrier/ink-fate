# Prompt builder

Son but est de construire le contexte parfait pour le LLM. Il ne doit jamais recevoir "Continue l'histoire", il doit plutôt recevoir :

- l'état du mode ;
- les personnages concernés ;
- leurs relations ;
- leurs souvenirs pertinents ;
- la scène actuelle ;
- la réponse du joueur ;
- les règles narratives ;
- le format JSON attendu.
  La pipeline générale :

```
WorldState
↓
Scene
↓
Relevant Characters
↓
Relevant Memories
↓
Player Input
↓
Prompt Builder
↓
LLM
↓
SceneResult
```

Le but est qu'il transforme :

```json
{
  "world_state": {},
  "scene": {},
  "player_input": ""
}
```

en un prompte narratif propre et cohérent.

---

# System Promt

Le rôle fondamental du LLM :

```
You are the narrative engine of Ink & Fate.

Your role is to generate coherent, emotionally believable and character-consistent scenes inside a living narrative world.

Characters must behave according to:
- their personality
- their memories
- their goals
- their emotions
- their relationships

The world continues to evolve even outside the player's presence.

You must always return a valid JSON SceneResult object.
```

---

# Narrative Rules

Par exemple :

```
Rules:
- Stay consistent with character personalities
- Avoid sudden emotional changes
- Relationships evolve gradually
- Do not force romance
- Characters may disagree, avoid, lie or misunderstand
- Keep scenes emotionally believable
- Only generate important events
```

---

# Current State World

Par exemple :

```json
{
  "date": "2026-09-01",
  "time": "10:00",
  "location": "campus"
}
```

---

# Active Scene

```json
{
  "participants": ["dean", "beau", "elina"]
}
```

---

# Character Context

Seulement les personnages présents, c'est important pour les coûts :

```json
{
  "id": "dean",

  "personality": {
    "charisma": 95,
    "humor": 90,
    "loyalty": 90
  },

  "current_goals": ["tease_beau"]
}
```

---

# Relevant Memories

Seulement les souvenirs pertinents :

```json
[
  {
    "owner": "dean",
    "content": "Beau is protective of Elina."
  }
]
```

---

# IMPORTANT

Le prompt builder **ne doit jamais renvoyer toute la base**. Sinon les coûts seront énormes, le contexte sera brouillon, il y aura des incohérences.

---

# Player Input

Exemple :

```
Player action:
"I take my suitcase back and roll my eyes at Dean."
```

---

# Expected Output Format

Très important, le LLM doit voir :

```json
{
  "scene": {},
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

## Narrative Prompt

```
Off Campus universe.
Contemporary college romance.
Emotionally grounded interactions.
```

## Engine Prompt

```
Always return valid JSON.
Never skip required fields.
```

Le prompt builder doit devenir **déterministe**, même entrée -> même structure logique, sinon le moteur devient impossible à stabiliser.
