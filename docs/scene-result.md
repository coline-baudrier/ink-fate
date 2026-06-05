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
  "contact_updates": [],
  "memory_updates": [],
  "npc_knowledge_updates": {},
  "world_updates": {
    "new_location": "",
    "time_advance_minutes": 0,
    "character_movements": {},
    "character_position_updates": {},
    "character_activity_updates": {},
    "task_updates": {},
    "new_scene_props": []
  }
}
```

## scene

Informations principales de la scene.

Regles actuelles :

- `scene.location` doit etre une chaine et un lieu existant, sinon le moteur garde le lieu actif ;
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

- `character` doit etre un personnage existant ;
- `type` doit etre une chaine non vide ;
- `target` peut etre vide ;
- si `target` est rempli, il doit etre un personnage existant ;
- les champs texte sont nettoyes avant application.

## events

Evenements importants proposes.

```json
{
  "type": "first_meeting",
  "participants": ["dean", "elina"]
}
```

Regles actuelles :

- `type` doit etre une chaine non vide ;
- les participants invalides sont retires ;
- un evenement sans participant valide est supprime ;
- `summary` doit etre une chaine non vide si le LLM en fournit un ;
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
- les booleens et textes numeriques invalides sont ignores ;
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

## contact_updates

`contact_updates` permet au LLM de signaler qu'un personnage gagne un moyen de joindre un autre personnage.

Exemple : Elina obtient le numero de Dean via Beau, sans donner son numero a Dean.

```json
{
  "source": "elina",
  "target": "dean",
  "changes": {
    "phone_number_known": true
  }
}
```

Exemple : Elina et Dean echangent vraiment leurs numeros.

```json
{
  "source": "elina",
  "target": "dean",
  "changes": {
    "phone_numbers_exchanged": true
  }
}
```

Regles :

- `source` et `target` doivent etre des IDs de personnages ;
- `changes` accepte seulement des booleens ;
- `phone_number_known` est asymetrique ;
- `phone_numbers_exchanged` est applique dans les deux sens par le moteur ;
- `instagram_connected` est applique dans les deux sens par le moteur ;
- une discussion en face a face ne suffit pas a creer un contact.

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
- `type` devient `"memory"` s'il est absent ou vide ;
- `age` doit etre un entier positif ou nul ;
- `tags` est nettoye pour ne garder que les chaines non vides ;
- `importance` est limitee entre `1` et `10` ;
- un souvenir cree pendant le tour courant ne vieillit pas immediatement.

## world_updates

`world_updates` permet au LLM de proposer des changements persistants dans le world runtime.

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
- si `new_location` est vide mais que `scene.location` indique un lieu valide, le moteur peut aussi s'en servir comme lieu de scene ;
- le personnage joueur est deplace vers le nouveau lieu ;
- `character_movements` sert a deplacer des PNJ ;
- `character_movements` ne doit pas deplacer le personnage joueur ;
- les mouvements de PNJ vers des lieux invalides sont supprimes ;
- les mouvements du personnage joueur dans `character_movements` sont ignores ;
- `time_advance_minutes` doit etre un entier entre `0` et `180` ;
- `time_advance_minutes` peut remplacer l'avance de temps par defaut ;
- les participants de la scene sont recalcules selon les positions actuelles.

Notes moteur :

- si le joueur indique clairement un deplacement vers un lieu connu, le Player Intent Parser peut forcer `new_location` si le LLM l'oublie ;
- si le joueur indique qu'il laisse les PNJ derriere, le moteur retire les mouvements PNJ incoherents vers la destination du joueur ;
- dans ce cas, les dialogues PNJ sont limites a une reaction breve pour eviter une scene prolongee sans le joueur.

## npc_knowledge_updates

Mise a jour de ce qu'un PNJ sait sur le personnage joueur.

Utilise quand un PNJ apprend le nom du joueur pendant la scene (introduction, badge, tiers qui presente).

```json
{
  "hannah": {
    "knows_name": true,
    "known_name": "Elina"
  }
}
```

Regles :

- la cle est un ID de PNJ existant ;
- `knows_name` doit etre un booleen ;
- `known_name` est le nom tel qu'il a ete entendu dans la fiction ;
- le moteur persiste cette connaissance dans le personnage runtime ;
- une fois que `knows_name` est `true`, le PNJ peut utiliser le prenom du joueur dans les scenes suivantes.

## world_updates — champs supplementaires

En plus de `new_location`, `time_advance_minutes` et `character_movements`, `world_updates` accepte quatre champs supplementaires.

### character_position_updates

Position fine d'un personnage a l'interieur du lieu courant.

```json
{
  "hannah": "dans le couloir devant sa chambre",
  "garrett": "au bout du couloir pres de l'ascenseur"
}
```

Utilise quand un personnage se deplace au sein du meme lieu (ouvre sa porte, descend un etage, s'installe a un bureau).
Ne pas remplir si personne ne bouge.

### character_activity_updates

Activite en cours d'un personnage, persistee pour les scenes suivantes.

```json
{
  "garrett": "finit de vider les cartons, commence a monter les etageres"
}
```

Utilise quand l'activite d'un PNJ change reellement (tache qui avance, debut d'une nouvelle occupation).
Ne pas mettre a jour si le PNJ fait la meme chose qu'avant.

### task_updates

Avancee d'une tache partagee presente dans `world.active_tasks`.

```json
{
  "demenagement_garrett": {
    "progress": 60,
    "note": "cartons dans la chambre, etageres a monter",
    "status": "active"
  }
}
```

- `progress` : entier de 0 a 100 ;
- `note` : description courte de l'etat courant ;
- `status` : `"active"` ou `"completed"` (a 100%).

N'inclure une tache que si elle a clairement avance pendant la scene.

### new_scene_props

Details physiques nouveaux et persistants introduits dans le lieu courant.

```json
["une grande fenetre donnant sur la cour", "un bureau en bois sombre contre le mur"]
```

Seulement pour des details specifiques et ancres (un meuble precis, un objet nomme, un element structurel).
Ne pas ajouter d'atmosphere generale. Si rien de nouveau n'est introduit, liste vide.

## Champs Encore Partiels

Le moteur ne se sert pas encore de :

- `scene.time` pour regler directement l'heure ;
- `next_hooks`.

Le `SceneResult` ne contient pas directement les SMS hors scene. Les messages sont generes apres application du tour par `message_engine.py`, a partir du world runtime, des personnages runtime, du scenario et du contexte recent.

Pour changer le monde, le moteur utilise d'abord `world_updates`.
`scene.location` sert seulement de securite si le LLM a place le bon lieu dans la scene mais a oublie `world_updates.new_location`.
