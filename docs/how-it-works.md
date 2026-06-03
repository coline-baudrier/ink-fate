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
-> Relations / Memoires / Monde / Event Log / Temps
-> Sauvegarde JSON
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

Les fichiers JSON sont la verite du monde.

## 🚪 Point D'Entree

### `backend/main.py`

C'est le fichier lance par :

```powershell
py .\backend\main.py
```

Son role est surtout d'orchestrer :

1. charger le monde ;
2. charger les personnages ;
3. generer une scene ;
4. lire l'action du joueur ;
5. appliquer les consequences ;
6. sauvegarder ;
7. afficher la suite.

## 🗂️ Les Donnees

### `data/universes/off-campus/world.json`

Contient l'etat global :

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
- souvenirs.

Quand les relations ou souvenirs changent, ces fichiers sont sauvegardes.

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
- souvenirs importants ;
- action du joueur ;
- regles narratives ;
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
- souvenirs invalides ;
- changements de lieu invalides ;
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

### `memory_engine.py`

Applique les `memory_updates`.

Il ajoute des souvenirs aux personnages.

### `time_engine.py`

Avance l'heure du monde.

### `world_engine.py`

Regroupe les operations persistantes sur le monde :

- appliquer un changement de lieu propose par `world_updates` ;
- mettre a jour les positions des personnages ;
- recalculer les participants presents dans la scene active ;
- avancer l'heure apres une scene ;
- sauvegarder `world.json` ;
- reconstruire le contexte de scene.

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
9. memory_engine.py applique et vieillit les souvenirs.
10. world_engine.py applique les changements de lieu.
11. event_log_engine.py enregistre les evenements importants.
12. world_engine.py avance et sauvegarde le monde.
13. character_loader.py sauvegarde les personnages.
14. renderer.py affiche la scene.
15. main.py ajoute la scene a l'historique.
```

## 💾 Ce Qui Est Persistant

Persistant veut dire : sauvegarde dans un fichier.

Actuellement, sont persistants :

- relations ;
- souvenirs ;
- heure du monde ;
- lieu actif ;
- position des personnages ;
- journal d'evenements.

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
7. `backend/app/core/memory_engine.py`
8. `backend/app/core/world_engine.py`

Puis regarde les JSON :

1. `data/universes/off-campus/world.json`
2. `data/universes/off-campus/characters/dean.json`
3. `data/universes/off-campus/characters/elina.json`
4. `data/universes/off-campus/characters/beau.json`

## 🧠 Regle A Garder En Tete

Le LLM propose.

Le moteur decide.

Les JSON stockent la verite.
