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
-> ContactEngine
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
      relationship_stages.py
      contact_engine.py
      memory_engine.py
      memory_retriever.py
      npc_schedule_engine.py
      event_log_engine.py
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

- appliquer les changements de lieu proposes par `world_updates` ;
- appliquer les consequences monde d'un tour avec `update_world_after_turn` ;
- maintenir `character_locations` ;
- recalculer les participants de la scene active ;
- appliquer les plannings PNJ ;
- proteger les participants actifs contre les mouvements automatiques de schedule ;
- enregistrer les mouvements PNJ hors champ ;
- avancer le temps apres une scene ;
- sauvegarder `world.json` ;
- reconstruire le contexte de scene.

### app/core/character_state_engine.py

Gestion des changements persistants des personnages apres une scene.

Responsabilites :

- appliquer les changements relationnels ;
- appliquer les changements de moyens de contact ;
- appliquer les nouveaux souvenirs ;
- vieillir les souvenirs.

### app/core/time_engine.py

Gestion du temps.

Responsabilite actuelle :

- avancer l'heure du monde ;
- passer au jour suivant quand minuit est depasse.

### app/core/memory_engine.py

Gestion des souvenirs.

Responsabilites actuelles :

- appliquer les nouveaux souvenirs aux personnages ;
- vieillir les souvenirs existants.

### app/core/memory_retriever.py

Selection des souvenirs pertinents pour le prompt.

Responsabilites actuelles :

- calculer un score selon importance, age, tags et contexte joueur ;
- choisir les souvenirs les plus utiles par participant actif ;
- eviter d'envoyer toute la memoire au LLM.

### app/core/relationship_engine.py

Gestion des relations.

Responsabilites actuelles :

- appliquer les deltas relationnels ;
- limiter les valeurs finales entre `0` et `100`.

### app/core/contact_engine.py

Gestion des moyens de contact.

Responsabilites actuelles :

- appliquer les `contact_updates` ;
- creer les contacts manquants si besoin ;
- dupliquer les echanges de numeros dans les deux sens ;
- dupliquer les connexions Instagram dans les deux sens ;
- construire un contexte de contact lisible pour le prompt.

### app/core/relationship_stages.py

Lecture narrative des relations.

Responsabilites actuelles :

- transformer des valeurs numeriques en paliers narratifs ;
- construire un contexte relationnel lisible pour les participants ;
- aider le LLM a respecter une progression romance graduelle.

### app/core/event_log_engine.py

Gestion du journal d'evenements.

Responsabilites actuelles :

- lire les `events` valides du `SceneResult` ;
- creer un resume court ;
- ajouter les evenements dans `world.event_log`.

### app/core/npc_schedule_engine.py

Gestion simple des plannings PNJ.

Responsabilites actuelles :

- lire l'heure actuelle ;
- trouver l'entree de planning applicable ;
- deplacer les PNJ vers leur lieu prevu ;
- ignorer les PNJ deplaces narrativement pendant le tour ;
- ignorer les PNJ presents dans la scene active pendant le tour ;
- retourner les mouvements effectues pour les enregistrer dans `event_log`.

### app/core/scene_validator.py

Validation minimale de la sortie LLM.

Responsabilites actuelles :

- proteger contre les listes/dictionnaires invalides ;
- valider les champs principaux de `scene` ;
- supprimer dialogues, actions, evenements invalides ;
- nettoyer les types invalides dans les champs secondaires ;
- supprimer les dialogues du joueur ;
- valider les updates relationnels ;
- valider les updates memoire ;
- valider les changements de lieu proposes ;
- limiter les deltas relationnels ;
- limiter l'importance des souvenirs.

### app/core/prompt_builder.py

Construction du prompt.

Responsabilites :

- injecter le monde ;
- injecter la scene active ;
- injecter les lieux disponibles ;
- injecter les participants ;
- injecter l'historique de scene ;
- injecter les souvenirs pertinents ;
- injecter les statuts relationnels ;
- injecter les moyens de contact disponibles ;
- injecter les evenements recents ;
- injecter le contexte de scenario ;
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
10. contact_engine applique les moyens de contact.
11. memory_engine applique et vieillit les souvenirs.
12. world_engine applique les consequences du tour.
13. world_engine enregistre les evenements.
14. world_engine avance le temps.
15. world_engine applique les plannings PNJ hors scene.
16. world_engine sauvegarde le monde.
17. character_loader sauvegarde les personnages.
18. world_engine reconstruit le contexte.
19. renderer affiche la scene suivante.
```

## 🛡️ Regles Techniques

- Le LLM ne modifie jamais directement les JSON.
- Toute sortie LLM passe par le parser puis le validator.
- Les relations sont des deltas, jamais des valeurs absolues.
- Les relations finales restent entre `0` et `100`.
- Le joueur ne doit jamais recevoir de dialogue genere par le LLM.
- Les souvenirs doivent avoir un proprietaire valide et un contenu non vide.
- Les lieux proposes par le LLM doivent exister dans `world.json`.
- Le monde et les personnages sont sauvegardes separement.
