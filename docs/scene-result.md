# Scene Result

Le LLM ne doit jamais répondre avec un simple bloc de texte libre.

Il doit produire une structure exploitable par le moteur.

Cette structure contient :

- la narration ;
- les dialogues ;
- les actions ;
- les événements ;
- les conséquences ;
- les mises à jour du monde.

---

# Philosophie

Le moteur **décide ce qui est vrai**, le LLM **met en scène ce qu'il se passe**.

---

# Structure V1

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

## Scene

Contexte de la scène actuelle :

```json
{
  "location": "campus",
  "time": "10:15",
  "participants": ["dean", "beau", "elina"]
}
```

## Narration

Texte narratif pur, ce que le joueur lit comment dans un roman :

```json
["Dean notices Elina immediately.", "A grin slowly appears on his face."]
```

## Dialogue

Dialogues séparés :

```json
[
  {
    "speaker": "dean",
    "text": "So you're Beau's little sister?"
  }
]
```

On sépare la narration et le dialogue pour prévoir la suite :

- mode roman ;
- mode NV ;
- mode messagerie ;
- doublage ;
- animation.

## Actions

Ce sont les actions objectives :

```json
[
  {
    "character": "dean",
    "type": "take_luggage",
    "target": "elina"
  }
]
```

Parce que "Dean grabs the suitcase" est joli pour un humain mais inutilisable proprement pour le moteur.

## Events

Les évènements réellement enregistrés :

```json
[
  {
    "type": "first_meeting",
    "participants": ["dean", "elina"]
  }
]
```

Tous les dialogues ne sont pas des évènements, sinon on va créer 20000 évènements inutiles, alors que l'évènement doit **être narrativement utile**.

## World updates

Ce qui change dans le monde :

```json
{
  "time_advanced_minutes": 10,

  "new_scene_state": {
    "location": "campus"
  }
}
```

## Memory updates

Ce sont les souvenirs créés, ils sont très importants :

```json
[
  {
    "owner": "dean",
    "type": "episodic",
    "importance": 40,
    "content": "Elina seemed confident.",
    "tags": ["elina", "first_meeting"]
  }
]
```

## Relationship updates

Les modifications relationnelles :

```json
[
  {
    "source": "dean",
    "target": "elina",

    "changes": {
      "attraction": 10,
      "respect": 5
    }
  }
]
```

Le LLM ne renvoie pas `"attraction": 70` mais `"attraction": +10`, le moteur garde la vérité.

## Next hooks

Les possibilités narratives ouvertes :

```json
[
  "Dean may try to see Elina again later.",
  "Beau noticed Dean's interest.",
  "Elina can choose how to react to Dean."
]
```

Ces hooks servent à :

- guider le moteur ;
- maintenir les arcs narratifs ;
- aider la génération future.

---

# Exemple concret

```json
{
  "scene": {
    "location": "campus",
    "time": "10:15",
    "participants": ["dean", "beau", "elina"]
  },
  "narration": ["Dean notices Elina immediately."],
  "dialogues": [
    {
      "speaker": "dean",
      "text": "So you're Beau's little sister?"
    }
  ],
  "actions": [
    {
      "character": "dean",
      "type": "take_luggage",
      "target": "elina"
    }
  ],
  "events": [
    {
      "type": "first_meeting",
      "participants": ["dean", "elina"]
    }
  ],
  "relationship_updates": [
    {
      "source": "dean",
      "target": "elina",
      "changes": {
        "attraction": 10,
        "curiosity": 15
      }
    }
  ]
}
```

---
