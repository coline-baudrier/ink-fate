# World

Le world state represente l'etat courant du monde.

Il ne doit pas decrire tout l'univers en detail. Il doit contenir seulement les informations utiles au moteur pour savoir :

- ou se passe l'histoire ;
- quand elle se passe ;
- quels personnages existent ;
- quels evenements sont actifs ;
- quelle scene est actuellement jouee.

## Structure

Structure actuelle :

```json
{
  "universe": {
    "id": "",
    "name": ""
  },
  "timeline": {
    "current_date": "",
    "current_time": "",
    "current_day": null
  },
  "player_character": "",
  "locations": [
    {
      "id": "",
      "name": "",
      "description": ""
    }
  ],
  "characters": [],
  "active_events": [
    {
      "id": "",
      "title": "",
      "status": ""
    }
  ],
  "active_scene": {
    "location": "",
    "participants": []
  }
}
```

## universe

Identifie l'univers charge.

```json
{
  "id": "off-campus",
  "name": "Off Campus"
}
```

## timeline

Contient la date et l'heure courantes.

```json
{
  "current_date": "2026-09-01",
  "current_time": "10:00",
  "current_day": 1
}
```

Le moteur peut faire avancer le temps apres une scene ou une ellipse.

## player_character

Identifiant du personnage controle par le joueur.

```json
"player_character": "elina"
```

Regle importante :

- le LLM ne doit pas controler les pensees, emotions, decisions ou dialogues de ce personnage.

## locations

Liste des lieux connus de l'univers.

```json
{
  "id": "campus",
  "name": "Briar University Campus",
  "description": "Le campus de Briar University."
}
```

Pour le MVP, chaque lieu utilise dans une scene devrait avoir une description.

## characters

Liste des identifiants de personnages a charger.

```json
["dean", "beau", "elina"]
```

Les donnees completes sont stockees dans `characters/*.json`.

## active_events

Evenements importants en cours.

```json
[
  {
    "id": "arrival_day",
    "title": "Elina arrives at Briar",
    "status": "active"
  }
]
```

Un evenement actif aide le prompt a comprendre la situation actuelle.

## active_scene

Scene actuellement jouee.

```json
{
  "location": "campus",
  "participants": ["beau", "elina", "dean"]
}
```

Le moteur utilise cette section pour construire le `SceneContext`.

## Ce Que Le World State Ne Contient Pas

Pour le MVP, le world state ne gere pas :

- meteo detaillee ;
- economie ;
- inventaire ;
- systeme de quetes ;
- carte complete ;
- simulation permanente.

Ces elements pourront etre ajoutes plus tard seulement s'ils servent vraiment la narration.

## Scenario

Le scenario ne contient pas l'histoire complete.

Il contient seulement :

- la situation de depart ;
- ce que chaque personnage sait ;
- les tensions existantes.

Exemple :

```json
{
  "title": "Arrival at Briar",
  "premise": "Elina Maxwell arrives at Briar University.",
  "initial_state": {
    "beau_knows": ["Elina is arriving today"],
    "dean_knows": ["Beau has a younger sister"],
    "elina_knows": ["Beau studies at Briar"]
  },
  "initial_tensions": [
    {
      "description": "Dean enjoys teasing Beau."
    }
  ]
}
```

## Scenarios Futurs

Plus tard, un univers pourra avoir plusieurs scenarios.

```md
off-campus/
  characters/
  world.json
  scenarios/
    arrival.json
    summer_break.json
    graduation.json
    rival_team.json
```

Pour le MVP, un seul fichier `scenario.json` suffit.
