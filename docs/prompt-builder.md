# 🧵 Prompt Builder

Le prompt builder construit le contexte envoye au LLM.

Il ne doit jamais envoyer une demande vague comme :

```md
Continue l'histoire.
```

Il doit envoyer un contexte structure qui permet au LLM de generer une scene coherente et exploitable.

## 🎯 Objectif

Transformer :

```json
{
  "world": {},
  "scene_context": {},
  "player_input": "",
  "scene_history": ""
}
```

en prompt narratif clair, stable et complet.

## 🔁 Pipeline Actuel

```md
World
-> SceneContext
-> Available Locations
-> Active Participants
-> Scene History
-> Recent Events
-> Relevant Memories
-> Player Input
-> Narrative Rules
-> Canon Rules
-> JSON Rules
-> Expected SceneResult Format
-> LLM
```

## 📦 Contenu Du Prompt Actuel

Le prompt contient :

- role du LLM ;
- univers ;
- date et heure ;
- lieu actuel ;
- description du lieu ;
- liste des lieux disponibles ;
- personnage joueur ;
- personnages presents ;
- historique de scene ;
- evenements recents ;
- souvenirs pertinents ;
- action du joueur ;
- regles narratives ;
- regles canon du scenario actuel ;
- regles JSON ;
- format JSON attendu.

## 🕰️ Historique

Le prompt recoit l'historique de scene.

Cela permet au LLM de repondre a la suite de ce qui vient de se passer, au lieu de recommencer la scene depuis le debut.

```md
SCENE HISTORY
Previous scene:
...
```

## Evenements Recents

Le prompt recoit aussi les derniers evenements importants de `world.event_log`.

Cela aide le LLM a tenir compte de ce qui a deja ete marque comme important par le moteur, meme si l'historique de scene devient long.

```md
RECENT EVENTS
- Day 1, 10:05, arrival (elina): Elina arrives on campus.
```

## ✍️ Action Joueur

Si le joueur ecrit une action, elle est injectee dans le prompt :

```md
The player wrote:
Je leve les yeux au ciel.

Continue the scene from this input.
```

Si aucune action n'est fournie, le prompt genere la scene d'ouverture.

## 🛡️ Regles Joueur

Le prompt rappelle que :

- le joueur controle `elina` ;
- le LLM ne doit pas ecrire de dialogue pour `elina` ;
- le LLM ne doit pas decider les pensees, emotions ou choix de `elina` ;
- si le joueur ecrit du dialogue, il est considere comme deja prononce par `elina`.

## ✨ Regles Narratives Actuelles

Le prompt donne aussi des consignes specifiques pour eviter que toutes les reponses passent par Beau :

- Dean doit pouvoir repondre directement a Elina ;
- le LLM doit suivre qui le joueur adresse ;
- si Elina challenge Dean, Dean doit repondre a Elina ;
- Dean peut taquiner Beau, mais la reaction principale doit viser Elina.

Ces regles sont utiles pour le MVP, mais elles sont encore tres liees a l'univers `off-campus`.

## Changements De Monde

Le prompt demande aussi au LLM de remplir `world_updates`.

Objectif :

- proposer un nouveau lieu seulement si le joueur bouge clairement ;
- utiliser des IDs de lieux valides ;
- deplacer un PNJ seulement si la scene le justifie ;
- laisser les champs vides quand rien ne change.

Le validator et le world engine gardent le dernier mot : le LLM propose, le moteur applique seulement ce qui est valide.

## 🗂️ Format Attendu

Le prompt demande actuellement :

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
  ],
  "memory_updates": [],
  "world_updates": {
    "new_location": "",
    "time_advance_minutes": 0,
    "character_movements": {}
  }
}
```

## 🚧 Limites Actuelles

- Les regles canon sont encore ecrites en dur dans `prompt_builder.py`.
- Les relations existantes ne sont pas encore injectees dans le prompt.
- Les souvenirs sont injectes, mais la selection reste simple.
- Les evenements recents sont injectes, mais la selection reste simple.
- Les descriptions de lieux doivent exister dans `world.json`.
- Les regles canon sont encore tres liees a l'univers `off-campus`.

## 🔮 Direction Future

Plus tard, le prompt builder devrait lire davantage de donnees depuis :

- `scenario.json` ;
- les personnages ;
- les relations ;
- les souvenirs pertinents ;
- les evenements actifs et le journal d'evenements.
