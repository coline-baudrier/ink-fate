# Schema De Donnees

Les donnees d'Ink & Fate sont stockees en JSON pendant le MVP.

Le moteur doit rester independant des univers. Les fichiers JSON decrivent l'univers, les personnages, les lieux et l'etat courant.

## Arborescence Actuelle

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

## world.json

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
  "active_scene": {}
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

## Location

Un lieu doit avoir au minimum :

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

Pour le MVP, `description` devrait etre present sur tous les lieux utilises dans une scene.

## active_scene

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

## scenario.json

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

## character.json

Un personnage represente une entite narrative autonome.

Structure cible minimale :

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
  "private_thoughts": [],
  "memories": []
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
- `memories` : souvenirs persistants, a ajouter progressivement.

## relationship

Une relation est stockee du point de vue d'un personnage vers un autre.

```json
{
  "friendship": 20,
  "trust": 10,
  "respect": 15,
  "attraction": 30,
  "attachment": 0,
  "jealousy": 0
}
```

Les relations sont asymetriques :

- `dean -> elina` peut avoir une attraction forte ;
- `elina -> dean` peut avoir une attraction faible.

## memory

Un souvenir represente l'interpretation personnelle d'un evenement.

```json
{
  "id": "memory_001",
  "owner": "dean",
  "type": "episodic",
  "importance": 40,
  "content": "Elina seemed confident.",
  "tags": ["elina", "first_meeting"]
}
```

Champs :

- `id` : identifiant du souvenir.
- `owner` : personnage qui possede le souvenir.
- `type` : `core`, `episodic`, `emotional` ou `secret`.
- `importance` : valeur entre 1 et 100.
- `content` : formulation subjective du souvenir.
- `tags` : aide a la recuperation contextuelle.

## Regle Generale

Les JSON representent la verite du moteur.

Le LLM peut proposer des changements, mais seul le moteur applique les donnees apres validation.
