# 📦 SceneResult

Le `SceneResult` est le JSON produit par le LLM.

Le LLM propose. Le moteur decide.

## 🗂️ Structure Actuelle

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
  "memory_updates": []
}
```

## 📝 narration

Texte narratif lu par le joueur.

Le moteur l'affiche avec `renderer.py`.

## 💬 dialogues

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

## 🎭 actions

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

## 📌 events

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
- les evenements ne sont pas encore sauvegardes dans un journal.

## 💞 relationship_updates

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
- les deltas sont limites entre `-5` et `5` ;
- les valeurs finales sont limitees entre `0` et `100`.

## 🧠 memory_updates

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
- `importance` est limitee entre `1` et `10`.

## 🚧 Champs Pas Encore Appliques

Le moteur ne se sert pas encore de :

- `scene.location` pour changer de lieu ;
- `scene.time` pour regler l'heure ;
- `world_updates` ;
- `next_hooks`.

Ces champs pourront etre ajoutes quand le world engine sera plus avance.
