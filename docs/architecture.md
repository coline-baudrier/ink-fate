# Architecture

- **Character** : un personnage du monde, avec une identité, une personnalité, des relations, des souvenirs, des objectifs, des décisions ;
- **Relationship** : ce qu'un personnage ressent envers un autre, avec des relations séparés pour faire des updates et des évènements ;
- **Memory** : partie la plus importante parce que les souvenirs vont s'accumuler, on ne pourra pas tout envoyer à l'IA mais on pourra aller chercher les souvenirs les plus importants ;
- **Event** : un fait qui s'est réellement produit, c'est à dire un objectif, pas un sentiment ;
- **Scene** : ce qui est actuellement joué, c'est temporaire, elle existe pendant plusieurs minutes du jeu, mais disparaît ensuite ;
- **Location** : un lieu ;
- **World State** : c'est le coeur du système, il contient la date, l'heure, les personnages en action, la scène en cours, les évènements actifs ;
- **Story Arc** : on veut par exemple de la romance, rivalité, amitié, conflit mais sans les imposer ;

---

# Exemples d'architecture

## Character

```json
{
  "id": "dean",
  "identity": {},
  "personality": {},
  "goals": [],
  "current_goals": [],
  "fears": [],
  "desires": [],
  "relationships": {},
  "memories": [],
  "private_thoughts": []
}
```

## Relationship

```json
{
  "source": "dean",
  "target": "elina",

  "friendship": 20,
  "trust": 5,
  "respect": 15,
  "attraction": 30,
  "attachment": 0,
  "jealousy": 0
}
```

## Memory

```json
  "id": "memory_001",
  "owner": "dean",
  "date": "2026-09-01",
  "importance": 80,
  "content": "Elina stood up to him during their first meeting."
```

## Event

```json
  "id": "event_001",
  "type": "first_meeting",
  "participants": [
    "dean",
    "elina"
  ],
  "date": "2026-09-01"
```

## Scene

```json
  "id": "scene_001",
  "location": "campus",
  "participants": [
    "dean",
    "beau",
    "elina"
  ],
  "date": "2026-09-01",
  "time": "10:00"
```

## Location

```json
  "id": "campus",
  "name": "Briar Campus",
  "description": "..."
```

## World State

```json
{
  "current_date": "",
  "current_time": "",
  "characters": [],
  "active_scene": {},
  "active_events": []
}
```

```
WorldState
↓
Prompt Builder
↓
LLM
↓
Scene Result
↓
World Update
↓
New WorldState
```

## Story Arc

```json
{
  "id": "arc_001",
  "type": "romance",
  "characters": ["dean", "elina"],
  "status": "potential"
}
```

puis :

```json
{
  "status": "active"
}
```

puis :

```json
{
  "status": "completed"
}
```

ou :

```json
{
  "status": "failed"
}
```
