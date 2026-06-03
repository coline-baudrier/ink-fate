# Architecture

Cette documentation decrit l'architecture actuelle du prototype Ink & Fate.

## Principe Central

Le moteur garde la verite.

Le LLM genere des propositions narratives structurees. Le moteur parse, valide, filtre, applique seulement ce qui est autorise, puis sauvegarde les donnees modifiees.

```md
WorldState
-> SceneContext
-> PromptBuilder
-> LLM
-> SceneResultParser
-> SceneValidator
-> Renderer
-> RelationshipEngine
-> JSON Save
```

## Architecture Actuelle

```md
backend/
  main.py
  app/
    core/
      json_loader.py
      character_loader.py
      scene_context.py
      prompt_builder.py
      openai_client.py
      scene_result_parser.py
      scene_validator.py
      renderer.py
      relationship_engine.py

data/
  universes/
    off-campus/
      world.json
      scenario.json
      characters/
        elina.json
        beau.json
        dean.json
```

## Modules

### backend/main.py

Point d'entree CLI du prototype.

Responsabilites actuelles :

- charger `world.json` ;
- charger les personnages ;
- construire la scene active ;
- generer la scene d'ouverture ;
- lire les actions joueur dans une boucle ;
- envoyer l'historique au prompt ;
- valider partiellement le `SceneResult` ;
- afficher le rendu ;
- appliquer les updates relationnels ;
- sauvegarder les personnages modifies.

### app/core/json_loader.py

Charge et sauvegarde des fichiers JSON.

Responsabilites :

- verifier qu'un fichier existe ;
- charger du JSON ;
- sauvegarder du JSON lisible.

### app/core/character_loader.py

Charge et sauvegarde les personnages.

Responsabilites :

- charger un personnage depuis son fichier JSON ;
- charger plusieurs personnages a partir de leurs ids ;
- sauvegarder chaque personnage dans son fichier.

### app/core/scene_context.py

Construit le contexte utile pour la scene active.

Responsabilites :

- lire `active_scene` ;
- trouver le lieu courant ;
- recuperer les participants ;
- ajouter la date et l'heure courantes.

### app/core/prompt_builder.py

Construit le prompt envoye au LLM.

Responsabilites :

- injecter l'univers ;
- injecter le lieu ;
- injecter les participants ;
- injecter l'historique de scene ;
- injecter l'action joueur ;
- rappeler les regles narratives ;
- demander un JSON `SceneResult`.

### app/core/openai_client.py

Appelle l'API OpenAI.

Responsabilites :

- charger la cle API ;
- creer le client ;
- envoyer le prompt ;
- retourner le texte genere.

### app/core/scene_result_parser.py

Transforme la reponse texte du LLM en dictionnaire Python.

Responsabilites :

- parser du JSON ;
- afficher l'erreur si la reponse n'est pas un JSON valide.

### app/core/scene_validator.py

Filtre le `SceneResult` avant application.

Responsabilites actuelles :

- proteger contre les champs qui ne sont pas des listes ou dictionnaires ;
- supprimer les dialogues invalides ;
- supprimer les dialogues du personnage joueur ;
- supprimer les actions invalides ;
- supprimer les evenements invalides ou vides ;
- supprimer les updates relationnels avec personnages invalides ;
- limiter les deltas relationnels entre `-5` et `5`.

### app/core/renderer.py

Transforme un `SceneResult` en texte lisible pour la CLI.

Responsabilites :

- afficher les blocs de narration ;
- afficher les dialogues des PNJ.

### app/core/relationship_engine.py

Applique les changements relationnels valides aux personnages.

Responsabilites actuelles :

- lire `relationship_updates` ;
- trouver la relation `source -> target` ;
- ajouter les deltas ;
- limiter les valeurs finales entre `0` et `100`.

## Flux Actuel

```md
1. Charger world.json.
2. Charger les personnages.
3. Construire le contexte de scene.
4. Generer la scene d'ouverture.
5. Afficher la scene.
6. Lire une action joueur.
7. Construire un prompt avec l'historique.
8. Appeler le LLM.
9. Parser le SceneResult.
10. Filtrer le SceneResult.
11. Appliquer les updates relationnels.
12. Sauvegarder les personnages.
13. Afficher la suite.
14. Ajouter la suite a l'historique.
15. Recommencer.
```

## Concepts Du Domaine

### WorldState

Etat global du monde :

- univers ;
- date ;
- heure ;
- lieux ;
- personnages ;
- evenements actifs ;
- scene active.

### Character

Personnage du monde :

- identite ;
- personnalite ;
- objectifs ;
- peurs ;
- desirs ;
- relations ;
- souvenirs futurs ;
- pensees privees.

### SceneResult

Sortie structuree proposee par le LLM.

Elle contient notamment :

- narration ;
- dialogues ;
- actions ;
- evenements ;
- relationship updates.

### Relationship

Etat emotionnel asymetrique d'un personnage envers un autre.

Le moteur applique uniquement les deltas valides et limite les valeurs finales.

## Modules A Ajouter Plus Tard

### world_update_engine.py

Appliquera les changements de monde :

- temps ;
- scene active ;
- lieux ;
- evenements actifs.

### memory_engine.py

Creera, sauvegardera et recuperera les souvenirs pertinents.

### player_input.py

Classera l'entree joueur :

- parole ;
- action ;
- texto ;
- intention narrative ;
- ellipse.

## Regles Techniques

- Le moteur ne doit jamais appliquer une sortie LLM brute.
- Les identifiants de personnages doivent exister.
- Les updates relationnels sont des deltas, pas des valeurs absolues.
- Les deltas sont limites avant application.
- Les valeurs finales de relation sont limitees entre `0` et `100`.
- Le joueur ne doit jamais etre controle par le LLM.
- Les donnees d'univers doivent rester separees du moteur.
