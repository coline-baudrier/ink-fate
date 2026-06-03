# Ink & Fate

Ink & Fate est un moteur de roman interactif alimente par l'intelligence artificielle.

Le but n'est pas de creer un simple chatbot de roleplay, mais un moteur narratif capable de faire vivre une histoire dans un univers peuple de personnages autonomes. Le joueur incarne son propre personnage, agit librement, et le monde reagit en fonction des personnages, de leurs objectifs, de leurs souvenirs, de leurs relations et du temps qui passe.

## Statut Actuel

Le projet est actuellement un prototype CLI en Python.

Ce qui existe deja :

- chargement d'un univers depuis des fichiers JSON ;
- chargement des personnages ;
- construction d'un contexte de scene ;
- generation d'un prompt structure pour le LLM ;
- appel a l'API OpenAI ;
- parsing d'une reponse JSON `SceneResult`.

Ce qui n'existe pas encore :

- boucle interactive avec entree joueur ;
- validation complete du `SceneResult` ;
- application des mises a jour du monde ;
- sauvegarde de partie ;
- memoire persistante ;
- evolution effective des relations ;
- interface frontend ;
- API FastAPI.

## MVP 1

Le premier objectif jouable est volontairement limite :

- un seul univers : `off-campus` ;
- trois personnages : Elina, Beau et Dean ;
- une scene active ;
- stockage local en JSON ;
- interface CLI ;
- generation de scene par LLM ;
- validation minimale du JSON ;
- rendu lisible de la scene ;
- mise a jour simple des relations, souvenirs et etat du monde.

Voir [docs/mvp.md](docs/mvp.md) pour le perimetre exact.

## Vision

Ink & Fate doit permettre de generer des histoires longues, coherentes et evolutives.

L'histoire n'est pas ecrite a l'avance. Elle emerge des interactions entre :

- le joueur ;
- les personnages ;
- les relations ;
- les souvenirs ;
- les evenements ;
- le monde ;
- le temps.

Chaque partie doit pouvoir produire une histoire unique.

## Documentation

- [Vision](docs/vision.md) : experience cible et philosophie du moteur.
- [MVP](docs/mvp.md) : perimetre de la premiere version jouable.
- [Architecture](docs/architecture.md) : modules, flux actuel et flux cible.
- [Schema de donnees](docs/data-schema.md) : structure des fichiers JSON.
- [Game loop](docs/game-loop.md) : boucle de jeu attendue.
- [SceneResult](docs/scene-result.md) : contrat de sortie du LLM.
- [Prompt builder](docs/prompt-builder.md) : construction du prompt narratif.
- [Character system](docs/character-system.md) : structure des personnages.
- [Relationship system](docs/relationship-system.md) : relations dynamiques.
- [Memory system](docs/memory-system.md) : souvenirs et recuperation contextuelle.
- [World simulation](docs/world-simulation.md) : simulation hors champ.
- [Roadmap](docs/roadmap.md) : prochaines phases.

## Technologies

Actuel :

- Python ;
- JSON local ;
- OpenAI API.

Prevues plus tard :

- FastAPI ;
- SQLite ;
- React ou Vue ;
- eventuellement d'autres fournisseurs IA ou des modeles locaux.

## Lancement Du Prototype

Depuis la racine du projet :

```powershell
python backend/main.py
```

Le prototype charge l'univers `off-campus`, construit une scene d'arrivee, demande une generation au LLM, puis affiche le prompt, la reponse brute et le `SceneResult` parse.
