# 🗂️ Schema De Donnees

Les donnees d'Ink & Fate sont stockees en JSON pendant le MVP.

Le moteur doit rester independant des univers. Les fichiers JSON decrivent l'univers, les personnages, les lieux et l'etat courant.

## 🌳 Arborescence Actuelle

```md
data/
  universes/
    off-campus/
      world.json
      scenario.json
      characters/
        elina.json
        beau.json
        dean.json
```

## 🌍 world.json

`world.json` represente l'etat global actuel de l'univers.

Structure actuelle :

```json
{
  "universe": {
    "id": "off-campus",
    "name": "Off Campus"
  },
  "timeline": {
    "current_date": "2026-09-01",
    "current_time": "10:00",
    "current_day": 1
  },
  "player_character": "elina",
  "locations": [],
  "characters": [],
  "active_events": [],
  "active_scene": {},
  "character_locations": {},
  "event_log": []
}
```

Champs :

- `universe` : identite de l'univers charge.
- `timeline` : date, heure et jour courant.
- `player_character` : identifiant du personnage controle par le joueur.
- `locations` : lieux disponibles.
- `characters` : identifiants des personnages a charger.
- `active_events` : evenements importants en cours.
- `active_scene` : scene actuellement jouee.
- `character_locations` : position actuelle de chaque personnage.
- `event_log` : journal des evenements importants deja arrives.

## 📍 Location

Un lieu doit avoir :

```json
{
  "id": "campus",
  "name": "Briar University Campus",
  "description": "Le campus de Briar University."
}
```

Champs :

- `id` : identifiant stable utilise par le moteur.
- `name` : nom affiche ou envoye au prompt.
- `description` : contexte narratif du lieu.

Important : le prompt builder lit actuellement `location["description"]`. Tout lieu pouvant devenir actif doit donc avoir une description.

## 🎬 active_scene

La scene active indique ou se passe la scene et quels personnages sont presents.

```json
{
  "location": "campus",
  "participants": ["beau", "elina", "dean"]
}
```

Champs :

- `location` : identifiant d'un lieu existant.
- `participants` : identifiants de personnages charges.

## Positions Des Personnages

`character_locations` stocke le lieu actuel de chaque personnage.

```json
{
  "elina": "dormitory",
  "beau": "campus",
  "dean": "campus"
}
```

Le moteur utilise ces positions pour recalculer `active_scene.participants` apres un changement de lieu.

Regles actuelles :

- les cles sont des IDs de personnages ;
- les valeurs sont des IDs de lieux ;
- le joueur est deplace automatiquement quand `world_updates.new_location` est applique ;
- les PNJ peuvent etre deplaces via `world_updates.character_movements`.

## event_log

`event_log` conserve les evenements importants valides.

```json
{
  "day": 1,
  "date": "2026-09-01",
  "time": "10:15",
  "type": "arrival",
  "participants": ["elina"],
  "summary": "Elina arrive sur le campus."
}
```

Le journal est sauvegarde dans `world.json` et les derniers evenements sont reinjectes dans le prompt.

## 📖 scenario.json

`scenario.json` decrit le point de depart narratif.

```json
{
  "title": "Arrival at Briar",
  "premise": "Elina Maxwell arrives at Briar University.",
  "initial_state": {},
  "initial_tensions": []
}
```

Champs :

- `title` : nom du scenario.
- `premise` : situation initiale.
- `initial_state` : ce que les personnages savent deja.
- `initial_tensions` : tensions narratives de depart.

Le prompt n'utilise pas encore directement `scenario.json`. Les regles canon sont encore ecrites dans `prompt_builder.py`.

## 👤 character.json

Un personnage represente une entite narrative autonome.

Structure actuelle :

```json
{
  "id": "dean",
  "identity": {},
  "personality": {},
  "archetype": "charmer",
  "goals": [],
  "fears": [],
  "desires": [],
  "relationships": {},
  "current_goals": [],
  "private_thoughts": []
}
```

Champs :

- `id` : identifiant stable du personnage.
- `identity` : nom, age et informations publiques.
- `personality` : traits numeriques ou qualitatifs.
- `archetype` : role narratif general.
- `goals` : objectifs longs.
- `fears` : peurs importantes.
- `desires` : envies profondes.
- `relationships` : relations asymetriques vers les autres personnages.
- `current_goals` : objectifs actifs dans la scene ou la journee.
- `private_thoughts` : informations internes a utiliser avec prudence.

Champ courant :

- `memories` : souvenirs persistants.

## 💞 relationship

Une relation est stockee du point de vue d'un personnage vers un autre.

```json
{
  "friendship": 20,
  "trust": 10,
  "respect": 15,
  "attachment": 0,
  "jealousy": 0,
  "attraction": 30
}
```

Regles actuelles :

- les relations sont asymetriques ;
- les valeurs sont entre `0` et `100` ;
- les updates du LLM sont des deltas ;
- les personnages sont sauvegardes apres application des updates.

## 🧠 memory

Les souvenirs sont sauvegardes dans les fichiers personnages.

Structure actuelle simplifiee :

```json
{
  "owner": "dean",
  "content": "Elina seemed confident.",
  "type": "memory",
  "importance": 5,
  "age": 0,
  "tags": ["elina", "first_meeting"]
}
```

## 🧠 Regle Generale

Les JSON representent la verite du moteur.

Le LLM peut proposer des changements, mais seul le moteur applique les donnees apres validation.
