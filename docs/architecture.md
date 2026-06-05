# 🧱 Architecture

Cette documentation decrit l'architecture actuelle du prototype Ink & Fate.

## 🧠 Principe Central

Le moteur garde la verite.

Le LLM propose une scene sous forme de JSON. Le moteur parse, valide, filtre, applique uniquement les effets autorises, puis sauvegarde les donnees modifiees dans l'etat runtime de la partie.

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
-> MessageEngine
-> RuntimeSave
```

## 🗂️ Architecture Actuelle

```md
backend/
  api_main.py
  main.py
  app/
    api/
      game.py
      schemas.py
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
      planned_event_engine.py
      story_arc_engine.py
      story_arc_state_engine.py
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
        garrett.json
        hannah.json
        logan.json
        allie.json
        jules.json
        tucker.json
  saves/
    off-campus/
      default/
        world.json
        characters/

frontend/
  src/
    App.jsx
    styles/
      app.css
  vite.config.js
```

## 🧩 Modules

### backend/main.py

Point d'entree CLI du prototype.

Il orchestre la partie jouable :

- charger le monde canon ou runtime ;
- charger les personnages canon ou runtime ;
- construire le contexte de scene ;
- generer une scene ;
- lire l'action du joueur ;
- appliquer les effets persistants ;
- sauvegarder l'etat runtime de la partie ;
- afficher la scene.

### backend/api_main.py et app/api/

Interface HTTP FastAPI du moteur.

Responsabilites actuelles :

- charger ou creer la sauvegarde runtime `default` ;
- exposer la scene courante et les metadonnees ;
- traiter une action joueur ;
- streamer les entrees narratives en SSE ;
- exposer les SMS ;
- reinitialiser la sauvegarde par defaut.

### frontend/

Interface React/Vite.

Responsabilites actuelles :

- afficher le fil narratif ;
- envoyer les actions du joueur ;
- consommer le flux SSE ;
- afficher date, heure et personnage joueur ;
- afficher et envoyer les SMS ;
- reinitialiser la partie.

### app/core/scene_pipeline.py

Pipeline de generation d'une scene.

Responsabilites :

- construire le prompt ;
- construire les indices deterministes d'intention joueur et contact ;
- appeler OpenAI ;
- parser la reponse JSON ;
- valider le `SceneResult` ;
- appliquer les corrections deterministes issues des intentions detectees.

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
- deduire certains evenements planifies depuis une scene ;
- observer les signaux d'arcs narratifs apres une scene ;
- avancer le temps apres une scene ;
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

- calculer un score selon importance, age, tags, lieu, relations, evenements et contexte joueur ;
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

### app/core/planned_event_engine.py

Gestion MVP des evenements prevus.

Responsabilites actuelles :

- stocker des rendez-vous concrets dans `world.planned_events` ;
- eviter les doublons par `id` ;
- creer le rendez-vous patinoire Dean/Elina depuis une scene parlee claire ;
- fournir un contexte prompt lisible des evenements planifies ;
- servir de couche commune entre SMS, scene face-a-face et futurs moteurs hors champ.

### app/core/story_arc_engine.py

Construction du contexte d'arcs narratifs.

Responsabilites actuelles :

- lire `scenario.story_arcs` ;
- filtrer les arcs actifs ;
- formater les questions dramatiques, tensions, beats disponibles et beats bloques ;
- rappeler au prompt que les beats sont des opportunites, pas une checklist ;
- garder l'issue ouverte, y compris romance qui progresse, stagne, bifurque ou echoue.

### app/core/story_arc_state_engine.py

Observation runtime des arcs narratifs.

Responsabilites actuelles :

- stocker les signaux observes dans `world.arc_state` ;
- detecter des beats deja joues depuis les scenes et SMS ;
- eviter les doublons de signaux ;
- exposer un contexte prompt des beats deja vus ;
- aider le LLM a eviter les repetitions sans forcer la suite.

### app/core/npc_schedule_engine.py

Gestion simple des plannings PNJ.

Responsabilites actuelles :

- lire l'heure actuelle ;
- trouver l'entree de planning applicable ;
- deplacer les PNJ vers leur lieu prevu ;
- ignorer les PNJ deplaces narrativement pendant le tour ;
- ignorer les PNJ presents dans la scene active pendant le tour ;
- retourner les mouvements effectues pour les enregistrer dans `event_log`.

### app/core/message_engine.py

Moteur SMS MVP hors scene.

Responsabilites actuelles :

- detecter une opportunite narrative claire de message ;
- generer des SMS PNJ inities par `scenario.message_triggers` ;
- conserver le SMS Dean -> Elina pour le suivi patinoire comme trigger configure ;
- eviter les doublons par `trigger` ;
- stocker les messages dans `world.messages` ;
- lister les messages du joueur ;
- marquer les messages du joueur comme lus ;
- parser et appliquer les reponses SMS du joueur ;
- journaliser les reponses SMS dans `event_log` ;
- creer des consequences narratives simples depuis certains SMS, comme un `planned_meeting` et un `planned_event` durable ;
- noter certains signaux d'arcs depuis les SMS ajoutes au monde ;
- creer un souvenir simple chez un PNJ qui repond par SMS ;
- generer une confirmation Dean -> Elina apres une reponse au rendez-vous patinoire ;
- utiliser un texte deterministe par defaut ou un texte LLM optionnel si `INK_FATE_ENABLE_LLM_SMS=1` ;
- utiliser le meme principe LLM optionnel/fallback pour les SMS PNJ inities par trigger ;
- generer une reponse SMS PNJ generique via LLM quand le joueur envoie un SMS significatif a un PNJ contactable ;
- eviter les doublons de reponses generiques avec un trigger derive du SMS joueur.

### app/core/runtime_save.py

Gestion des sauvegardes runtime.

Responsabilites actuelles :

- charger le canon si aucune sauvegarde runtime n'existe ;
- charger `data/saves/<universe>/<save_id>` si elle existe ;
- sauvegarder `world.json` et les personnages runtime ensemble ;
- normaliser les `save_id` ;
- supprimer une sauvegarde runtime.

### app/core/runtime_directives.py

Directives HRP runtime.

Responsabilites actuelles :

- parser `/hrp`, `/rule` et `/context` ;
- stocker les directives dans `world.runtime_directives` ;
- eviter les doublons ;
- construire une section de prompt dediee.

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
- injecter les evenements planifies ;
- injecter les indices deterministes joueur/contact ;
- injecter les directives HRP runtime ;
- injecter le contexte de scenario ;
- injecter les arcs narratifs actifs ;
- injecter l'etat observe des arcs narratifs ;
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

Chargement et sauvegarde des personnages. En jeu, les sauvegardes passent par `runtime_save.py` pour ne pas modifier les personnages canon.

## 🔁 Flux Actuel

```md
1. main.py determine le `save_id`.
2. main.py charge le world runtime s'il existe, sinon le world canon.
3. main.py charge les personnages runtime s'ils existent, sinon les personnages canon.
4. scene_context construit le contexte de scene.
5. scene_pipeline genere et valide une scene d'ouverture.
6. renderer affiche la scene.
7. Le joueur ecrit une action ou une commande CLI.
8. Les commandes runtime (`messages`, `/hrp`, `reset`, etc.) sont traitees sans appel LLM.
9. scene_pipeline genere et valide la suite.
10. character_state_engine applique les effets personnages.
11. relationship_engine applique les relations.
12. contact_engine applique les moyens de contact.
13. memory_engine applique et vieillit les souvenirs.
14. world_engine applique les consequences du tour.
15. world_engine enregistre les evenements.
16. world_engine deduit les planned events depuis la scene.
17. world_engine observe les signaux d'arcs narratifs depuis la scene.
18. world_engine avance le temps.
19. world_engine applique les plannings PNJ hors scene.
20. message_engine genere les messages hors scene si les conditions sont reunies.
21. message_engine observe les signaux d'arcs narratifs depuis les SMS.
22. runtime_save sauvegarde le world et les personnages runtime.
23. world_engine reconstruit le contexte.
24. renderer affiche la scene suivante.
```

## 🛡️ Regles Techniques

- Le LLM ne modifie jamais directement les JSON.
- Toute sortie LLM passe par le parser puis le validator.
- Les relations sont des deltas, jamais des valeurs absolues.
- Les relations finales restent entre `0` et `100`.
- Le joueur ne doit jamais recevoir de dialogue genere par le LLM.
- Les souvenirs doivent avoir un proprietaire valide et un contenu non vide.
- Les lieux proposes par le LLM doivent exister dans le world charge.
- Le canon dans `data/universes` ne doit pas etre modifie pendant une partie.
- Le monde runtime et les personnages runtime sont sauvegardes ensemble dans `data/saves`.
