# Comment Fonctionne Ink & Fate

Ce document explique simplement comment le projet fonctionne et comment les fichiers se parlent.

## Idee Generale

Ink & Fate est un moteur narratif IA.

Le joueur ecrit une action. Le moteur construit un prompt, demande au LLM de generer la suite, verifie le JSON recu, affiche la scene, puis sauvegarde les consequences importantes.

```md
Action joueur
-> Prompt
-> LLM
-> SceneResult JSON
-> Validation
-> Affichage
-> Relations / Memoires / Temps
-> Sauvegarde JSON
```

## Les Deux Grandes Parties

Le projet est separe en deux grandes zones.

```md
backend/
  code Python du moteur

data/
  donnees de l'univers et des personnages
```

Le code Python est le moteur.

Les fichiers JSON sont la verite du monde.

## Point D'Entree

### backend/main.py

C'est le fichier lance par :

```powershell
py .\backend\main.py
```

Il ne devrait pas contenir toute la logique. Son role est surtout d'orchestrer :

1. charger le monde ;
2. charger les personnages ;
3. generer une scene ;
4. lire l'action du joueur ;
5. appliquer les consequences ;
6. sauvegarder ;
7. afficher la suite.

## Les Donnees

### data/universes/off-campus/world.json

Contient l'etat global :

- nom de l'univers ;
- date ;
- heure ;
- personnage joueur ;
- lieux ;
- personnages a charger ;
- scene active.

### data/universes/off-campus/characters/*.json

Chaque personnage a son fichier.

Un personnage contient :

- identite ;
- personnalite ;
- objectifs ;
- relations ;
- souvenirs.

Quand les relations ou souvenirs changent, ces fichiers sont sauvegardes.

## Chargement Et Sauvegarde

### json_loader.py

Lit et ecrit les fichiers JSON.

Il est utilise par presque tous les modules qui ont besoin de charger ou sauvegarder des donnees.

### character_loader.py

Charge et sauvegarde les personnages.

Il transforme une liste comme :

```json
["dean", "beau", "elina"]
```

en dictionnaire Python contenant les donnees completes de chaque personnage.

## Construire Le Contexte De Scene

### scene_context.py

Le monde complet est trop grand pour etre envoye tel quel au LLM.

`scene_context.py` extrait seulement ce qui est utile pour la scene :

- lieu actuel ;
- date ;
- heure ;
- personnages presents.

Ce contexte est ensuite donne au prompt builder.

## Generer Une Scene

### scene_pipeline.py

C'est le pipeline de generation.

Il fait :

```md
build prompt
-> call OpenAI
-> parse JSON
-> validate SceneResult
```

Il retourne une scene deja filtree.

### prompt_builder.py

Construit le texte envoye au LLM.

Il inclut :

- le contexte du monde ;
- le personnage joueur ;
- les participants ;
- l'historique ;
- les souvenirs importants ;
- l'action du joueur ;
- les regles narratives ;
- le format JSON attendu.

### openai_client.py

Envoie le prompt a OpenAI et recupere la reponse texte.

### scene_result_parser.py

Transforme la reponse texte du LLM en dictionnaire Python.

Si le LLM ne renvoie pas un JSON valide, c'est ici que ca casse.

## Valider La Sortie Du LLM

### scene_validator.py

Le LLM peut se tromper.

Ce fichier nettoie le `SceneResult`.

Il supprime ou corrige :

- dialogues avec personnage invalide ;
- dialogues du joueur ;
- actions invalides ;
- evenements invalides ;
- updates relationnels invalides ;
- souvenirs invalides ;
- valeurs relationnelles trop grandes ;
- importance de souvenir hors limites.

Cette etape est importante parce que le moteur ne doit pas faire confiance aveuglement au LLM.

## Afficher La Scene

### renderer.py

Transforme le `SceneResult` en texte lisible dans le terminal.

Il affiche :

- narration ;
- dialogues.

## Appliquer Les Consequences

### relationship_engine.py

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

Les valeurs finales restent entre `0` et `100`.

### memory_engine.py

Applique les `memory_updates`.

Il ajoute des souvenirs aux personnages, puis vieillit les souvenirs.

Exemple :

```json
{
  "owner": "dean",
  "content": "Elina challenged him directly.",
  "importance": 5
}
```

Ce souvenir est ajoute dans `dean.json`.

### time_engine.py

Avance l'heure du monde.

Actuellement, le temps avance de quelques minutes apres chaque tour.

### world_engine.py

Regroupe les operations simples sur le monde :

- avancer le monde apres une scene ;
- sauvegarder `world.json` ;
- reconstruire le contexte de scene.

## Cycle Complet D'Un Tour

Voici ce qui se passe quand le joueur ecrit une action :

```md
1. main.py lit l'action.
2. scene_pipeline.py genere une scene.
3. prompt_builder.py construit le prompt.
4. openai_client.py appelle OpenAI.
5. scene_result_parser.py parse le JSON.
6. scene_validator.py nettoie le SceneResult.
7. relationship_engine.py applique les relations.
8. memory_engine.py applique les souvenirs.
9. world_engine.py avance et sauvegarde le monde.
10. character_loader.py sauvegarde les personnages.
11. renderer.py affiche la scene.
12. main.py ajoute la scene a l'historique.
```

## Ce Qui Est Persistant

Persistant veut dire : sauvegarde dans un fichier.

Actuellement, sont persistants :

- relations ;
- souvenirs ;
- heure du monde.

Ne sont pas encore persistants :

- historique complet de partie ;
- journal d'evenements ;
- changements de scene active ;
- arcs narratifs.

## Comment Lire Le Projet

Si tu es perdue, lis dans cet ordre :

1. `backend/main.py`
2. `backend/app/core/scene_pipeline.py`
3. `backend/app/core/prompt_builder.py`
4. `backend/app/core/scene_validator.py`
5. `backend/app/core/relationship_engine.py`
6. `backend/app/core/memory_engine.py`
7. `backend/app/core/world_engine.py`

Puis regarde les JSON :

1. `data/universes/off-campus/world.json`
2. `data/universes/off-campus/characters/dean.json`
3. `data/universes/off-campus/characters/elina.json`
4. `data/universes/off-campus/characters/beau.json`

## Regle A Garder En Tete

Le LLM propose.

Le moteur decide.

Les JSON stockent la verite.
