# 🧭 Comment Fonctionne Ink & Fate

Ce document explique simplement comment le projet fonctionne et comment les fichiers se parlent.

## ✨ Idee Generale

Ink & Fate est un moteur narratif IA.

Le joueur ecrit une action. Le moteur construit un prompt, demande au LLM de generer la suite, verifie le JSON recu, affiche la scene, puis sauvegarde les consequences importantes.

```md
Action joueur
-> Prompt
-> LLM
-> SceneResult JSON
-> Validation
-> Relations / Contacts / Memoires / Monde / Event Log / Temps / SMS
-> Sauvegarde runtime
-> Affichage
```

## 🧱 Les Deux Grandes Parties

Le projet est separe en deux grandes zones.

```md
backend/
  code Python du moteur

data/
  donnees de l'univers et des personnages
```

Le code Python est le moteur.

Les fichiers JSON canon de `data/universes` decrivent le depart. Les fichiers runtime dans `data/saves` sont la verite de la partie en cours.

## 🚪 Point D'Entree

### `backend/main.py`

C'est le fichier lance par :

```powershell
py .\backend\main.py
```

Son role est surtout d'orchestrer :

1. charger le monde canon ou runtime ;
2. charger les personnages canon ou runtime ;
3. generer une scene ;
4. lire l'action du joueur ;
5. appliquer les consequences ;
6. sauvegarder l'etat runtime ;
7. afficher la suite.

## 🗂️ Les Donnees

### `data/universes/off-campus/world.json`

Contient l'etat global canon de depart :

- nom de l'univers ;
- date ;
- heure ;
- personnage joueur ;
- lieux ;
- personnages a charger ;
- scene active ;
- position actuelle des personnages.

### `data/universes/off-campus/characters/*.json`

Chaque personnage a son fichier.

Un personnage contient :

- identite ;
- personnalite ;
- objectifs ;
- relations ;
- moyens de contact ;
- souvenirs.

Quand les relations, contacts ou souvenirs changent, ces fichiers sont sauvegardes.

En jeu, ces changements sont sauvegardes dans `data/saves/<universe>/<save_id>/characters`, pas dans les fichiers canon.

### `data/saves/off-campus/<save_id>/`

Contient l'etat de partie :

- `world.json` runtime ;
- personnages runtime ;
- messages ;
- directives HRP ;
- positions, temps courant, event_log.

## 💾 Chargement Et Sauvegarde

### `json_loader.py`

Lit et ecrit les fichiers JSON.

### `character_loader.py`

Charge et sauvegarde les personnages.

Il transforme une liste comme :

```json
["dean", "beau", "elina"]
```

en dictionnaire Python contenant les donnees completes de chaque personnage.

## 🎬 Construire Le Contexte De Scene

### `scene_context.py`

Le monde complet est trop grand pour etre envoye tel quel au LLM.

`scene_context.py` extrait seulement :

- lieu actuel ;
- date ;
- heure ;
- personnages presents.

Les personnages presents viennent de `active_scene["participants"]`, qui peut etre recalculee par `world_engine.py` quand les positions changent.

## 🧪 Generer Une Scene

### `scene_pipeline.py`

C'est le pipeline de generation.

```md
build prompt
-> call OpenAI
-> parse JSON
-> validate SceneResult
```

Il retourne une scene deja filtree.

### `prompt_builder.py`

Construit le texte envoye au LLM.

Il inclut :

- contexte du monde ;
- lieux disponibles ;
- personnage joueur ;
- participants ;
- historique ;
- evenements recents ;
- souvenirs pertinents ;
- statuts relationnels ;
- moyens de contact disponibles ;
- indices deterministes de mouvement/contact ;
- contexte du scenario ;
- directives HRP runtime ;
- action du joueur ;
- format JSON attendu.

### `openai_client.py`

Envoie le prompt a OpenAI et recupere la reponse texte.

### `scene_result_parser.py`

Transforme la reponse texte du LLM en dictionnaire Python.

## 🛡️ Valider La Sortie Du LLM

### `scene_validator.py`

Le LLM peut se tromper.

Ce fichier nettoie le `SceneResult`.

Il supprime ou corrige :

- dialogues avec personnage invalide ;
- dialogues du joueur ;
- actions invalides ;
- evenements invalides ;
- updates relationnels invalides ;
- updates de contact invalides ;
- souvenirs invalides ;
- changements de lieu invalides ;
- types invalides dans les champs secondaires ;
- valeurs relationnelles trop grandes ;
- importance de souvenir hors limites.

## 🖨️ Afficher La Scene

### `renderer.py`

Transforme le `SceneResult` en texte lisible dans le terminal.

Il affiche :

- narration ;
- dialogues.

## 🔁 Appliquer Les Consequences

### `character_state_engine.py`

Applique tous les effets qui concernent les personnages.

Il regroupe :

- les relations ;
- les contacts ;
- les souvenirs ;
- le vieillissement des souvenirs.

Dans `main.py`, cela permet d'appeler une seule fonction :

```python
update_characters_after_scene(...)
```

### `relationship_engine.py`

Applique les `relationship_updates`.

Exemple :

```json
{
  "source": "dean",
  "target": "elina",
  "changes": {
    "attraction": 3
  }
}
```

Cela modifie la relation :

```md
dean -> elina
```

### `contact_engine.py`

Applique les `contact_updates`.

Exemple :

```json
{
  "source": "elina",
  "target": "dean",
  "changes": {
    "phone_number_known": true
  }
}
```

Cela signifie qu'Elina connait le numero de Dean, meme si Dean n'a pas forcement le numero d'Elina.

### `relationship_stages.py`

Transforme les valeurs numeriques des relations en paliers narratifs.

Ces paliers sont envoyes au prompt pour eviter que les relations changent trop vite.

### `memory_engine.py`

Applique les `memory_updates`.

Il ajoute des souvenirs aux personnages.

### `memory_retriever.py`

Selectionne les souvenirs les plus pertinents pour la scene.

Il tient compte de l'importance, de l'age, des tags, de l'action du joueur, de l'historique, du lieu, des participants, des relations et des evenements recents.

### `time_engine.py`

Avance l'heure du monde.

### `world_engine.py`

Regroupe les operations persistantes sur le monde :

- appliquer un changement de lieu propose par `world_updates` ;
- mettre a jour les positions des personnages ;
- recalculer les participants presents dans la scene active ;
- avancer l'heure apres une scene ;
- appliquer les plannings PNJ ;
- proteger les participants actifs pour qu'ils ne soient pas deplaces par leur schedule pendant la scene ;
- enregistrer les mouvements PNJ hors champ ;
- reconstruire le contexte de scene.

### `message_engine.py`

Genere et gere les messages hors scene.

Aujourd'hui, il sait :

- generer un SMS Dean -> Elina si Dean connait son numero, qu'ils ne sont pas au meme lieu et qu'un contexte patinoire/defi existe ;
- eviter les doublons via `trigger` ;
- stocker les messages dans `world.messages` ;
- afficher les messages du joueur via le CLI ;
- marquer les messages comme lus ;
- envoyer une reponse SMS joueur avec `reply dean: texte` ;
- enregistrer cette reponse dans `event_log`.

### `runtime_save.py`

Charge et sauvegarde l'etat runtime.

Il evite de modifier le canon dans `data/universes`.

### `runtime_directives.py`

Gere les commandes HRP :

- `/hrp texte` ;
- `/rule texte` ;
- `/context texte`.

Les directives sont stockees dans `world.runtime_directives` et reinjectees dans le prompt.

### `npc_schedule_engine.py`

Lit les schedules des personnages et deplace les PNJ selon l'heure.

Le personnage joueur n'est pas deplace automatiquement par son schedule.

Si un PNJ a deja ete deplace par la scene, son schedule ne l'ecrase pas pendant le meme tour.

Si un PNJ participe a la scene en cours, son schedule ne le deplace pas non plus pendant ce tour. Cela evite qu'un personnage quitte une conversation sans que la narration l'ait indique.

Les PNJ hors scene peuvent continuer a bouger avec leur schedule, ce qui garde une simulation simple du hors champ.

### `event_log_engine.py`

Ajoute les evenements importants dans `world.event_log`.

Le journal garde :

- le jour ;
- la date ;
- l'heure ;
- le type d'evenement ;
- les participants ;
- un resume court.

## 🧵 Cycle Complet D'Un Tour

Voici ce qui se passe quand le joueur ecrit une action :

```md
1. main.py lit l'action.
2. scene_pipeline.py genere une scene.
3. prompt_builder.py construit le prompt.
4. openai_client.py appelle OpenAI.
5. scene_result_parser.py parse le JSON.
6. scene_validator.py nettoie le SceneResult.
7. character_state_engine.py applique les effets personnages.
8. relationship_engine.py applique les relations.
9. contact_engine.py applique les moyens de contact.
10. memory_engine.py applique et vieillit les souvenirs.
11. world_engine.py applique les consequences monde du tour.
12. event_log_engine.py enregistre les evenements importants.
13. world_engine.py avance le temps.
14. npc_schedule_engine.py applique les plannings PNJ hors scene.
15. message_engine.py genere les SMS hors scene eventuels.
16. runtime_save.py sauvegarde le world et les personnages runtime.
17. renderer.py affiche la scene.
18. main.py ajoute la scene a l'historique.
```

## 💾 Ce Qui Est Persistant

Persistant veut dire : sauvegarde dans un fichier.

Actuellement, sont persistants :

- relations ;
- contacts ;
- souvenirs ;
- heure du monde ;
- lieu actif ;
- position des personnages ;
- journal d'evenements ;
- messages ;
- directives HRP runtime.

Ne sont pas encore persistants :

- historique complet de partie ;
- arcs narratifs.

## 🗺️ Comment Lire Le Projet

Si tu es perdue, lis dans cet ordre :

1. `backend/main.py`
2. `backend/app/core/scene_pipeline.py`
3. `backend/app/core/prompt_builder.py`
4. `backend/app/core/scene_validator.py`
5. `backend/app/core/character_state_engine.py`
6. `backend/app/core/relationship_engine.py`
7. `backend/app/core/contact_engine.py`
8. `backend/app/core/memory_engine.py`
9. `backend/app/core/world_engine.py`
10. `backend/app/core/message_engine.py`
11. `backend/app/core/runtime_save.py`
12. `backend/app/core/runtime_directives.py`

Puis regarde les JSON :

1. `data/universes/off-campus/world.json`
2. `data/universes/off-campus/scenario.json`
3. `data/universes/off-campus/characters/dean.json`
4. `data/universes/off-campus/characters/elina.json`
5. `data/universes/off-campus/characters/beau.json`
6. `data/saves/off-campus/<save_id>/world.json` si une partie existe.

## 🧠 Regle A Garder En Tete

Le LLM propose.

Le moteur decide.

Les JSON runtime stockent la verite de la partie. Les JSON canon stockent le depart propre.
