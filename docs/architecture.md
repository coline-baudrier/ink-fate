# Architecture

Cette documentation decrit l'architecture actuelle du prototype et l'architecture cible du MVP 1.

## Principe Central

Le moteur garde la verite.

Le LLM genere des propositions narratives structurees, mais le moteur decide ce qui est valide, ce qui est applique et ce qui est sauvegarde.

```md
WorldState
-> SceneContext
-> PromptBuilder
-> LLM
-> SceneResult
-> Validator
-> WorldUpdateEngine
-> Renderer
-> New WorldState
```

## Architecture Actuelle

Le projet actuel est un prototype CLI.

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
      renderer.py

data/
  universes/
    off-campus/
      world.json
      scenario.json
      characters/
```

## Modules Actuels

### backend/main.py

Point d'entree CLI du prototype.

Responsabilites actuelles :

- charger `world.json` ;
- charger les personnages ;
- construire le contexte de scene ;
- construire le prompt ;
- appeler OpenAI ;
- parser la reponse ;
- afficher les resultats de debug.

### app/core/json_loader.py

Charge et sauvegarde des fichiers JSON.

Responsabilites :

- verifier qu'un fichier existe ;
- charger du JSON ;
- sauvegarder du JSON lisible.

### app/core/character_loader.py

Charge un ou plusieurs personnages depuis le dossier `characters`.

Responsabilites :

- convertir un identifiant personnage en chemin de fichier ;
- retourner un dictionnaire de personnages charges.

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

Responsabilites actuelles :

- parser du JSON.

Responsabilites futures :

- deleguer la validation a un validateur dedie.

### app/core/renderer.py

Module prevu pour transformer un `SceneResult` en texte lisible.

Statut actuel :

- fichier vide.

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
- souvenirs ;
- pensees privees.

### Scene

Moment actuellement joue.

Une scene est temporaire. Elle contient :

- un lieu ;
- une date ;
- une heure ;
- des participants ;
- un contexte narratif.

### Event

Fait objectif qui s'est produit dans le monde.

Un evenement n'est pas une emotion. Exemple :

```json
{
  "type": "first_meeting",
  "participants": ["dean", "elina"]
}
```

### Memory

Interpretation subjective d'un evenement par un personnage.

Deux personnages peuvent vivre le meme evenement et creer deux souvenirs differents.

### Relationship

Etat emotionnel asymetrique d'un personnage envers un autre.

Exemple :

```json
{
  "source": "dean",
  "target": "elina",
  "attraction": 30,
  "trust": 5
}
```

## Flux Actuel

```md
1. main.py charge world.json.
2. main.py charge les personnages.
3. scene_context construit la scene active.
4. prompt_builder construit un prompt.
5. openai_client appelle le LLM.
6. scene_result_parser parse la reponse.
7. main.py affiche le resultat.
```

## Flux Cible MVP

```md
1. Charger le WorldState.
2. Charger les personnages pertinents.
3. Afficher la scene actuelle.
4. Lire l'action du joueur.
5. Construire le prompt avec l'action joueur.
6. Appeler le LLM.
7. Parser le SceneResult.
8. Valider le SceneResult.
9. Rendre la scene au joueur.
10. Appliquer les updates autorises.
11. Sauvegarder le nouvel etat.
12. Recommencer.
```

## Modules A Ajouter

### scene_result_validator.py

Valide la structure et les valeurs du `SceneResult`.

### world_update_engine.py

Applique les changements autorises :

- temps ;
- scene active ;
- evenements ;
- souvenirs ;
- relations.

### player_input.py

Lit et classe l'entree joueur :

- parole ;
- action ;
- texto ;
- intention narrative ;
- ellipse.

### memory_retriever.py

Selectionne uniquement les souvenirs pertinents a envoyer au prompt.

## Regles Techniques

- Le moteur ne doit jamais appliquer une sortie LLM non valide.
- Les identifiants de personnages et de lieux doivent exister.
- Les updates relationnelles doivent etre limitees.
- Le joueur ne doit jamais etre controle par le LLM.
- Les donnees d'univers doivent rester separees du moteur.
- Le prompt builder doit rester deterministe a structure equivalente.
