# SceneResult

Le `SceneResult` est le JSON produit par le LLM.

Le LLM propose. Le moteur decide.

## Structure Actuelle

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
  "relationship_updates": [],
  "memory_updates": [],
  "world_updates": {
    "new_location": "",
    "time_advance_minutes": 0,
    "character_movements": {}
  }
}
```

## scene

Informations principales de la scene.

Regles actuelles :

- `scene.location` doit etre un lieu existant, sinon le moteur garde le lieu actif ;
- `scene.time` doit etre une heure valide au format `HH:MM`, sinon le moteur garde l'heure courante ;
- `scene.participants` ne garde que les personnages existants ;
- si les participants sont invalides ou absents, le moteur garde les participants de la scene active.

## narration

Texte narratif lu par le joueur.

Le moteur l'affiche avec `renderer.py`.

## dialogues

Dialogues des PNJ.

```json
{
  "speaker": "dean",
  "text": "Alors, tu comptes me provoquer toute la journee ?"
}
```

Regles actuelles :

- le speaker doit etre un personnage existant ;
- le speaker ne doit pas etre le personnage joueur ;
- les dialogues invalides sont supprimes.

## actions

Actions objectives proposees par le LLM.

```json
{
  "character": "dean",
  "type": "tease",
  "target": "elina"
}
```

Regle actuelle :

- `character` doit etre un personnage existant.

## events

Evenements importants proposes.

```json
{
  "type": "first_meeting",
  "participants": ["dean", "elina"]
}
```

Regles actuelles :

- les participants invalides sont retires ;
- un evenement sans participant valide est supprime ;
- les evenements valides sont sauvegardes dans `world.event_log`.

## relationship_updates

Deltas relationnels proposes.

```json
{
  "source": "dean",
  "target": "elina",
  "changes": {
    "attraction": 3,
    "respect": 1
  }
}
```

Regles actuelles :

- `source` et `target` doivent exister ;
- les valeurs doivent etre des entiers ;
- les deltas sont limites selon la dimension relationnelle ;
- les valeurs finales sont limitees entre `0` et `100`.

Limites actuelles :

```md
attraction: -2 a +2
respect: -3 a +3
friendship: -2 a +2
trust: -1 a +2
attachment: -1 a +1
jealousy: -2 a +2
autre dimension: -2 a +2
```

## memory_updates

Souvenirs proposes.

```json
{
  "owner": "dean",
  "type": "memory",
  "content": "Elina challenged him directly.",
  "importance": 5,
  "age": 0,
  "tags": ["elina", "challenge"]
}
```

Regles actuelles :

- `owner` doit etre un personnage existant ;
- `content` doit etre une chaine non vide ;
- `importance` est limitee entre `1` et `10` ;
- un souvenir cree pendant le tour courant ne vieillit pas immediatement.

## world_updates

`world_updates` permet au LLM de proposer des changements persistants dans `world.json`.

```json
{
  "new_location": "library",
  "time_advance_minutes": 10,
  "character_movements": {
    "dean": "library"
  }
}
```

Regles actuelles :

- `new_location` doit etre vide si le joueur ne change pas clairement de lieu ;
- `new_location` doit etre un ID de lieu existant ;
- si `new_location` est valide, le moteur change `active_scene.location` ;
- le personnage joueur est deplace vers le nouveau lieu ;
- `character_movements` sert a deplacer des PNJ ;
- les mouvements de PNJ vers des lieux invalides sont supprimes ;
- `time_advance_minutes` peut remplacer l'avance de temps par defaut ;
- les participants de la scene sont recalcules selon les positions actuelles.

## Champs Encore Partiels

Le moteur ne se sert pas encore de :

- `scene.location` pour appliquer directement un changement de lieu ;
- `scene.time` pour regler directement l'heure ;
- `next_hooks`.

Pour changer le monde, le moteur utilise actuellement `world_updates`.
