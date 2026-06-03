# World

Le world state represente l'etat courant du monde.

Il ne doit pas decrire tout l'univers en detail. Il doit contenir seulement les informations utiles au moteur pour savoir :

- ou se passe l'histoire ;
- quand elle se passe ;
- quels personnages existent ;
- quels evenements sont actifs ;
- quelle scene est actuellement jouee.

## Structure Actuelle

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
  "characters": ["dean", "beau", "elina"],
  "active_events": [],
  "active_scene": {
    "location": "campus",
    "participants": ["beau", "elina", "dean"]
  }
}
```

## timeline

Contient la date et l'heure courantes.

Le moteur ne met pas encore a jour la timeline apres les scenes. Cette fonctionnalite appartient au futur `world_update_engine`.

## player_character

Identifiant du personnage controle par le joueur.

```json
"player_character": "elina"
```

Regle importante :

- le LLM ne doit pas controler les pensees, emotions, decisions ou dialogues de ce personnage.

Le validator supprime aussi les dialogues generes pour ce personnage.

## locations

Liste des lieux connus de l'univers.

```json
{
  "id": "campus",
  "name": "Briar University Campus",
  "description": "Le campus de Briar University."
}
```

Pour le MVP, tout lieu utilise comme scene active doit avoir une `description`, car le prompt builder la lit directement.

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

Ces evenements ne sont pas encore injectes explicitement dans le prompt, mais ils font partie du world state cible.

## active_scene

Scene actuellement jouee.

```json
{
  "location": "campus",
  "participants": ["beau", "elina", "dean"]
}
```

Le moteur utilise cette section pour construire le `SceneContext`.

La scene active n'est pas encore modifiee apres une generation.

## Ce Que Le World State Ne Contient Pas Encore

Pour le MVP actuel, le world state ne gere pas :

- meteo detaillee ;
- economie ;
- inventaire ;
- systeme de quetes ;
- carte complete ;
- simulation permanente ;
- historique de partie sauvegarde ;
- souvenirs persistants ;
- updates de temps appliquees.

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

Pour l'instant, ce fichier sert surtout de reference de conception. Le prompt builder ne le consomme pas encore directement.
