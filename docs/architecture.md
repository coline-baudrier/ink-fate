# 🧱 Architecture

Cette documentation decrit l'architecture actuelle du prototype Ink & Fate.

## 🧠 Principe Central

Le moteur garde la verite.

Le LLM propose une scene sous forme de JSON. Le moteur parse, valide, filtre, applique uniquement les effets autorises, puis sauvegarde les donnees modifiees.

```md
World + Characters
-> SceneContext
-> ScenePipeline
-> PromptBuilder
-> OpenAI
-> SceneResultParser
-> SceneValidator
-> Renderer
-> CharacterStateEngine
-> RelationshipEngine
-> MemoryEngine
-> WorldEngine
-> JSON Save
```

## 🗂️ Architecture Actuelle

```md
backend/
  main.py
  app/
    core/
      json_loader.py
      character_loader.py
      scene_context.py
      scene_pipeline.py
      prompt_builder.py
      openai_client.py
      scene_result_parser.py
      scene_validator.py
      renderer.py
      character_state_engine.py
      relationship_engine.py
      memory_engine.py
      time_engine.py
      world_engine.py

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

## 🧩 Modules

### backend/main.py

Point d'entree CLI du prototype.

Il orchestre la partie jouable :

- charger le monde ;
- charger les personnages ;
- construire le contexte de scene ;
- generer une scene ;
- lire l'action du joueur ;
- appliquer les effets persistants ;
- sauvegarder le monde et les personnages ;
- afficher la scene.

### app/core/scene_pipeline.py

Pipeline de generation d'une scene.

Responsabilites :

- construire le prompt ;
- appeler OpenAI ;
- parser la reponse JSON ;
- valider le `SceneResult`.

### app/core/world_engine.py

Gestion simple du monde.

Responsabilites :

- appliquer les changements simples du monde apres une scene ;
- sauvegarder `world.json` ;
- reconstruire le contexte de scene.

### app/core/character_state_engine.py

Gestion des changements persistants des personnages apres une scene.

Responsabilites :

- appliquer les changements relationnels ;
- appliquer les nouveaux souvenirs ;
- vieillir les souvenirs.

### app/core/time_engine.py

Gestion du temps.

Responsabilite actuelle :

- avancer l'heure du monde de quelques minutes.

### app/core/memory_engine.py

Gestion des souvenirs.

Responsabilites actuelles :

- appliquer les nouveaux souvenirs aux personnages ;
- vieillir les souvenirs existants.

### app/core/relationship_engine.py

Gestion des relations.

Responsabilites actuelles :

- appliquer les deltas relationnels ;
- limiter les valeurs finales entre `0` et `100`.

### app/core/scene_validator.py

Validation minimale de la sortie LLM.

Responsabilites actuelles :

- proteger contre les listes/dictionnaires invalides ;
- supprimer dialogues, actions, evenements invalides ;
- supprimer les dialogues du joueur ;
- valider les updates relationnels ;
- valider les updates memoire ;
- limiter les deltas relationnels ;
- limiter l'importance des souvenirs.

### app/core/prompt_builder.py

Construction du prompt.

Responsabilites :

- injecter le monde ;
- injecter la scene active ;
- injecter les participants ;
- injecter l'historique de scene ;
- injecter les souvenirs pertinents ;
- injecter l'action joueur ;
- demander un JSON `SceneResult`.

### app/core/renderer.py

Rendu CLI.

Responsabilites :

- afficher la narration ;
- afficher les dialogues.

### app/core/json_loader.py

Lecture et ecriture JSON.

### app/core/character_loader.py

Chargement et sauvegarde des personnages.

## 🔁 Flux Actuel

```md
1. main.py charge world.json.
2. main.py charge les personnages.
3. scene_context construit le contexte de scene.
4. scene_pipeline genere et valide une scene d'ouverture.
5. renderer affiche la scene.
6. Le joueur ecrit une action.
7. scene_pipeline genere et valide la suite.
8. character_state_engine applique les effets personnages.
9. relationship_engine applique les relations.
10. memory_engine applique et vieillit les souvenirs.
11. world_engine avance le temps.
12. world_engine sauvegarde le monde.
13. character_loader sauvegarde les personnages.
14. world_engine reconstruit le contexte.
15. renderer affiche la scene suivante.
```

## 🛡️ Regles Techniques

- Le LLM ne modifie jamais directement les JSON.
- Toute sortie LLM passe par le parser puis le validator.
- Les relations sont des deltas, jamais des valeurs absolues.
- Les relations finales restent entre `0` et `100`.
- Le joueur ne doit jamais recevoir de dialogue genere par le LLM.
- Les souvenirs doivent avoir un proprietaire valide et un contenu non vide.
- Le monde et les personnages sont sauvegardes separement.
