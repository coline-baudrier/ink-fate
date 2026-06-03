# SceneResult

Le `SceneResult` est le contrat de sortie du LLM.

Le LLM ne doit pas repondre avec du texte libre. Il doit produire un JSON exploitable par le moteur.

## Philosophie

Le LLM met en scene.

Le moteur decide ce qui devient vrai.

Le `SceneResult` est une proposition structuree. Avant application, il est parse, filtre, puis transforme en updates autorises.

## Structure Actuelle MVP

Le prompt demande actuellement ce format :

```json
{
  "scene": {
    "location": "",
    "time": "",
    "participants": []
  },
  "narration": [],
  "dialogues": [
    {
      "speaker": "",
      "text": ""
    }
  ],
  "actions": [
    {
      "character": "",
      "type": "",
      "target": ""
    }
  ],
  "events": [
    {
      "type": "",
      "participants": []
    }
  ],
  "relationship_updates": [
    {
      "source": "",
      "target": "",
      "changes": {
        "attraction": 0,
        "respect": 0
      }
    }
  ]
}
```

## narration

Fragments narratifs lus par le joueur.

Regles :

- la narration peut decrire le monde, les PNJ et les actions visibles du joueur ;
- elle ne doit jamais decrire les pensees, emotions ou decisions internes du joueur ;
- elle doit rester coherente avec le ton de l'univers.

## dialogues

Dialogues separes de la narration.

```json
[
  {
    "speaker": "dean",
    "text": "Alors, c'est toi la fameuse petite soeur de Beau ?"
  }
]
```

Regles :

- `speaker` doit etre un personnage existant ;
- le LLM ne doit pas ecrire de dialogue pour le personnage joueur ;
- le validator supprime tout dialogue dont le speaker est invalide ;
- le validator supprime tout dialogue du personnage joueur.

## actions

Actions objectives qui peuvent etre comprises par le moteur.

```json
[
  {
    "character": "dean",
    "type": "notice",
    "target": "elina"
  }
]
```

Regles :

- `character` doit exister ;
- une action mal formee est ignoree ;
- une action avec personnage invalide est supprimee.

## events

Evenements importants proposes par le LLM.

```json
[
  {
    "type": "first_meeting",
    "participants": ["dean", "elina"]
  }
]
```

Regles :

- les participants doivent exister ;
- les participants invalides sont retires ;
- un evenement sans participant valide est supprime ;
- les evenements ne sont pas encore sauvegardes dans un historique persistant.

## relationship_updates

Changements relationnels proposes.

```json
[
  {
    "source": "dean",
    "target": "elina",
    "changes": {
      "attraction": 3,
      "respect": 1
    }
  }
]
```

Regles :

- les valeurs sont des deltas, pas des valeurs absolues ;
- `source` et `target` doivent exister ;
- les deltas non numeriques sont ignores ;
- les deltas sont limites entre `-5` et `5` ;
- les valeurs finales de relation sont limitees entre `0` et `100` ;
- les changements valides sont sauvegardes dans les fichiers personnages.

## Champs Futurs

Ces champs sont prevus dans la vision, mais pas encore utilises par le code actuel :

- `world_updates` ;
- `memory_updates` ;
- `next_hooks`.

Ils pourront etre ajoutes quand le moteur aura un `world_update_engine` et un `memory_engine`.

## Validation Actuelle

Avant application, le moteur verifie actuellement :

- listes et dictionnaires de base ;
- dialogues valides ;
- pas de dialogue joueur ;
- actions valides ;
- evenements valides ;
- updates relationnels avec personnages valides ;
- deltas relationnels limites.

Validation restante a ajouter :

- champs obligatoires de `scene` ;
- lieux existants ;
- types exacts de chaque champ ;
- rapport d'erreur ou de nettoyage ;
- validation des futurs souvenirs.
