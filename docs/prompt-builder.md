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
-> Planned Events
-> Relevant Memories
-> Relationship Status
-> Contact Access
-> Player Intent Hints
-> Contact Intent Hints
-> Player Input
-> Scenario Context
-> Story Arcs
-> Observed Arc State
-> Runtime GM Directives
-> NPC Autonomy Rules
-> Scene Direction
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
- evenements planifies ;
- souvenirs pertinents ;
- statuts relationnels ;
- moyens de contact disponibles ;
- indices deterministes de mouvement joueur ;
- indices deterministes de contact ;
- action du joueur ;
- contexte de scenario ;
- arcs narratifs actifs ;
- etat observe des arcs narratifs ;
- directives HRP runtime ;
- regles d'autonomie PNJ ;
- direction de scene ;
- regles de pacing ;
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

## Evenements Planifies

Le prompt recoit les rendez-vous concrets stockes dans `world.planned_events`.

```md
PLANNED EVENTS
- Day 2, 07:00, location ice_rink (dean, elina): Dean and Elina agreed to meet at the rink for a skating lesson.
```

Ces evenements aident le LLM a se souvenir des promesses et rendez-vous sans forcer immediatement la prochaine scene.

## Arcs Narratifs

Le prompt recoit les arcs actifs de `scenario.story_arcs`.

```md
STORY ARCS
- Arc: dean_elina_slow_burn
  - Current phase: initial_tension
  - Available beats: playful_challenge; missed_connection
  - Blocked beats: love_confession; official_couple
```

Les arcs servent de boussole dramatique. Les beats disponibles sont des opportunites, pas des obligations. Le joueur peut refuser, retarder, detourner ou casser une dynamique.

## Etat Observe Des Arcs

Le prompt recoit aussi `world.arc_state`, qui resume les beats et signaux deja observes pendant la partie.

```md
OBSERVED ARC STATE
- Arc state: dean_elina_slow_burn
  - Runtime phase: initial_tension
  - Played beats: playful_challenge; text_followup
  - Observed signals: playful_challenge_seen; text_followup_seen
```

Cet etat aide le LLM a eviter de rejouer la meme tension sans raison. Il ne force pas la prochaine scene : il rappelle seulement ce qui a deja eu un poids dramatique.

## Souvenirs Pertinents

Le prompt recoit des souvenirs choisis par `memory_retriever.py`.

La selection tient compte de l'importance, de l'age, des tags, de l'action du joueur, de l'historique recent, du lieu, des participants, des relations et des evenements.

## Statuts Relationnels

Le prompt recoit aussi un resume des relations entre participants actifs.

Exemple :

```md
RELATIONSHIP STATUS
- dean -> elina:
  - attraction: 20/100 (emerging attraction)
  - trust: 5/100 (guarded)
```

Cela aide le LLM a ne pas faire monter la romance trop vite.

## Moyens De Contact

Le prompt recoit aussi un resume des moyens de contact disponibles.

```md
CONTACT ACCESS
- elina -> dean: phone known: no, numbers exchanged: no, instagram connected: no, can text/call: no, can DM: no
```

Ce bloc aide le LLM a savoir si un personnage peut envoyer un texto, appeler ou DM un autre personnage.

## ✍️ Action Joueur

Si le joueur ecrit une action, elle est injectee dans le prompt :

```md
The player wrote:
Je leve les yeux au ciel.

Continue the scene from this input.
```

Si aucune action n'est fournie, le prompt genere la scene d'ouverture.

Si l'entree est vide pendant une scene existante, le moteur la traite comme une attente breve ou une observation. Le prompt demande de rester centre sur le personnage joueur et le lieu actif.

## Indices Deterministes

Avant l'appel LLM, le pipeline peut detecter :

- un deplacement clair du joueur vers un lieu connu ;
- le fait que le joueur laisse explicitement les PNJ derriere ;
- le fait que le joueur donne son numero a un personnage.

Ces indices sont injectes dans `PLAYER INTENT HINTS` et `CONTACT INTENT HINTS`.

Ils ne remplacent pas l'IA narrative, mais fiabilisent les consequences structurelles que le LLM oublie parfois.

## Directives HRP Runtime

Les commandes `/hrp`, `/rule` et `/context` ajoutent des directives dans `world.runtime_directives`.

Le prompt les injecte dans :

```md
RUNTIME GM DIRECTIVES
```

Ces directives orientent le ton ou le contexte de la partie, sans modifier `scenario.json` et sans pouvoir annuler les regles du moteur.

## 🛡️ Regles Joueur

Le prompt rappelle que :

- le joueur controle `elina` ;
- le LLM ne doit pas ecrire de dialogue pour `elina` ;
- le LLM ne doit pas decider les pensees, emotions ou choix de `elina` ;
- si le joueur ecrit du dialogue, il est considere comme deja prononce par `elina`.

## ✨ Regles Narratives Actuelles

Le prompt donne aussi des consignes pour :

- rendre les PNJ plus autonomes ;
- pousser les PNJ a agir selon leurs objectifs, desirs, peurs et relations ;
- garder la scene ouverte pour une reponse joueur ;
- eviter les scenes centrees uniquement sur les PNJ ;
- suivre le personnage joueur quand il quitte un groupe ;
- limiter les reactions PNJ quand le joueur les laisse explicitement derriere.
- guider l'histoire avec des arcs souples sans forcer une fin.

Les dynamiques specifiques a Off Campus vivent dans `scenario.json`, pas dans les fiches personnages.

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
  "contact_updates": [
    {
      "source": "",
      "target": "",
      "changes": {
        "phone_number_known": false,
        "phone_numbers_exchanged": false,
        "instagram_connected": false
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

- Les regles canon sont lues depuis `scenario.json`.
- Les relations existantes sont injectees sous forme de paliers narratifs.
- Les souvenirs sont injectes avec une selection par score.
- Les evenements recents sont injectes, mais la selection reste simple.
- Les descriptions de lieux doivent exister dans le world charge.
- Les reponses SMS joueur sont gerees comme commandes runtime, sans appel LLM dedie.
- Les arcs narratifs et leur etat observe sont injectes dans le prompt, mais les phases ne progressent pas encore automatiquement en runtime.

## 🔮 Direction Future

Plus tard, le prompt builder devrait lire davantage de donnees depuis :

- les personnages ;
- les relations avec une selection plus fine ;
- les souvenirs avec un scoring plus riche ;
- les evenements actifs et le journal d'evenements ;
- les messages recents et les futures reponses PNJ par SMS ;
- une progression runtime des arcs narratifs.
