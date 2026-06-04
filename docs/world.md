# 🌍 World

Le world state represente l'etat courant du monde.

Dans `data/universes`, il sert de canon de depart. Pendant une partie, l'etat courant vit dans `data/saves/<universe>/<save_id>/world.json`.

Il ne doit pas decrire tout l'univers en detail. Il doit contenir seulement les informations utiles au moteur pour savoir :

- ou se passe l'histoire ;
- quand elle se passe ;
- quels personnages existent ;
- quels evenements sont actifs ;
- quelle scene est actuellement jouee.

## 🗂️ Structure Actuelle

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
  },
  "character_locations": {
    "elina": "campus",
    "beau": "campus",
    "dean": "campus"
  },
  "event_log": [],
  "messages": [],
  "runtime_directives": []
}
```

## 🕰️ timeline

Contient la date et l'heure courantes.

Le moteur met actuellement a jour l'heure apres chaque tour via `world_engine.py` et `time_engine.py`.

La mise a jour reste simple : elle avance l'heure, applique `world_updates.time_advance_minutes` quand il existe, et augmente `current_day` quand minuit est depasse.

Elle ne gere pas encore les dates calendaires complexes ou les ellipses longues.

## 👤 player_character

Identifiant du personnage controle par le joueur.

```json
"player_character": "elina"
```

Regle importante :

- le LLM ne doit pas controler les pensees, emotions, decisions ou dialogues de ce personnage.

Le validator supprime aussi les dialogues generes pour ce personnage.

## 📍 locations

Liste des lieux connus de l'univers.

```json
{
  "id": "campus",
  "name": "Briar University Campus",
  "description": "Le campus de Briar University."
}
```

Pour le MVP, tout lieu utilise comme scene active doit avoir une `description`, car le prompt builder la lit directement.

## 👥 characters

Liste des identifiants de personnages a charger.

```json
["dean", "beau", "elina"]
```

Les donnees completes sont stockees dans `characters/*.json`.

## 📌 active_events

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

## 🎬 active_scene

Scene actuellement jouee.

```json
{
  "location": "campus",
  "participants": ["beau", "elina", "dean"]
}
```

Le moteur utilise cette section pour construire le `SceneContext`.

La scene active peut changer apres une generation si le `SceneResult` contient un `world_updates.new_location` valide.

Si `world_updates.new_location` est vide mais que `scene.location` contient un lieu valide, le moteur utilise aussi ce lieu pour garder la position du joueur et la scene active synchronisees.

## Positions Des Personnages

`character_locations` indique ou se trouve chaque personnage.

```json
{
  "elina": "dormitory",
  "beau": "campus",
  "dean": "campus"
}
```

Le moteur s'en sert pour recalculer les participants de la scene active.

Regle simple actuelle :

- si le joueur change de lieu, `active_scene.location` change aussi ;
- le joueur est deplace vers ce nouveau lieu ;
- `world_updates.new_location` est prioritaire pour deplacer le joueur ;
- `scene.location` peut servir de secours si `new_location` est vide ;
- les PNJ peuvent etre deplaces via `world_updates.character_movements` ;
- les PNJ peuvent aussi bouger via leur `schedule` ;
- un mouvement narratif garde la priorite sur le schedule pendant le tour ;
- les personnages presents dans la scene active sont proteges du schedule pendant le tour ;
- un PNJ hors scene peut toujours bouger avec son schedule ;
- les participants sont recalcules selon les personnages qui se trouvent dans le lieu actif.

Cette protection evite qu'un personnage disparaisse au milieu d'une conversation simplement parce que son planning indique un autre lieu.

## Journal D'Evenements

`event_log` garde une trace des evenements importants.

Chaque entree contient :

- le jour ;
- la date ;
- l'heure ;
- le type d'evenement ;
- les participants ;
- un resume court.

Les mouvements PNJ produits par les schedules sont aussi enregistres avec le type `npc_schedule_move`.

## Messages

`messages` stocke les SMS hors scene.

Regles actuelles :

- les messages vivent dans le world runtime ;
- le moteur evite les doublons via `trigger` ;
- la commande `messages` / `sms` / `inbox` affiche les messages du joueur ;
- consulter les messages les marque comme lus ;
- la commande `reply dean: texte` ajoute une reponse SMS du joueur ;
- les reponses SMS du joueur sont aussi journalisees dans `event_log` ;
- Dean peut generer une confirmation automatique deterministe pour le rendez-vous patinoire.

## Directives HRP Runtime

`runtime_directives` stocke les consignes ajoutees pendant une partie avec `/hrp`, `/rule` ou `/context`.

Ces directives :

- sont sauvegardees dans le runtime ;
- sont reinjectees dans le prompt ;
- ne modifient pas `scenario.json` ;
- ne peuvent pas annuler les contraintes du moteur.

## 🚧 Ce Que Le World State Ne Contient Pas Encore

Pour le MVP actuel, le world state ne gere pas :

- meteo detaillee ;
- economie ;
- inventaire ;
- systeme de quetes ;
- carte complete ;
- simulation permanente ;
- historique de partie sauvegarde ;
- reponses PNJ generalisees ou generees par LLM aux SMS ;
- dates calendaires avancees.

## 📖 Scenario

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

Le prompt builder consomme ce fichier pour injecter les regles de ton, de canon, de dynamique personnages et de pacing.
