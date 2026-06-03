# Ink & Fate

Ink & Fate est un prototype Python de moteur narratif IA pour roman interactif.

Le but n'est pas de creer un simple chatbot de roleplay, mais un moteur capable de faire vivre une histoire dans un univers peuple de personnages autonomes. Le joueur incarne son propre personnage, agit librement, et le moteur genere la suite en tenant compte du contexte, de l'historique de scene et des relations entre personnages.

## 📍 Statut Actuel

Le projet est actuellement un prototype CLI jouable.

✅ Ce qui existe deja :

- chargement d'un univers depuis des fichiers JSON ;
- chargement et sauvegarde des personnages ;
- construction du contexte de scene active ;
- pipeline de generation et validation de scene ;
- generation d'un prompt structure pour le LLM ;
- appel a l'API OpenAI ;
- parsing d'une reponse JSON `SceneResult` ;
- boucle CLI avec entree joueur ;
- historique de scene envoye au prompt ;
- souvenirs pertinents selectionnes puis reinjectes au prompt ;
- statut relationnel des participants reinjecte au prompt ;
- evenements recents reinjectes au prompt ;
- regles de scenario, de romance progressive et de pacing dans `scenario.json` ;
- module central pour appliquer les effets personnages ;
- rendu texte simple ;
- validation du `SceneResult` ;
- validation des champs principaux de `scene` ;
- validation des champs secondaires de `actions`, `events`, `memory_updates`, `relationship_updates` et `world_updates` ;
- filtrage des dialogues/actions/evenements invalides ;
- suppression des dialogues du personnage joueur ;
- limitation des deltas relationnels par dimension ;
- application et sauvegarde des mises a jour relationnelles ;
- creation et sauvegarde de souvenirs ;
- avancee et sauvegarde du temps dans `world.json` ;
- passage au jour suivant apres minuit ;
- changements simples de lieu via `world_updates` ;
- positions des personnages sauvegardees dans `world.json` ;
- plannings simples pour les PNJ ;
- mouvements PNJ hors champ sauvegardes dans `event_log` ;
- protection des PNJ presents en scene contre les mouvements automatiques de schedule ;
- validation des mouvements de personnages proposes par le LLM ;
- journal d'evenements persistant.

🚧 Ce qui n'existe pas encore :

- rapport de validation lisible pour comprendre ce que le moteur a nettoye ;
- selection encore plus fine des souvenirs/evenements ;
- simulation hors champ avancee ;
- sauvegarde de partie separee ;
- interface frontend ;
- API FastAPI.

## 🎮 MVP 1

Le MVP 1 vise une boucle jouable simple :

- un seul univers : `off-campus` ;
- trois personnages : Elina, Beau et Dean ;
- une scene active ;
- stockage local en JSON ;
- interface CLI ;
- generation de scene par LLM ;
- validation structuree du `SceneResult` ;
- rendu texte ;
- evolution simple des relations ;
- souvenirs simples ;
- avancee du temps ;
- sauvegarde des personnages et du monde.

Voir [docs/mvp.md](docs/mvp.md) pour le perimetre exact.

## ✨ Vision

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

## 📚 Documentation

- 🧭 [Comment ca fonctionne](docs/how-it-works.md) : guide simple du projet et des interactions entre fichiers.
- ✨ [Vision](docs/vision.md) : experience cible et philosophie du moteur.
- 🎮 [MVP](docs/mvp.md) : perimetre de la premiere version jouable.
- 🧱 [Architecture](docs/architecture.md) : modules, flux actuel et flux cible.
- 🗂️ [Schema de donnees](docs/data-schema.md) : structure des fichiers JSON.
- 🔁 [Game loop](docs/game-loop.md) : boucle de jeu actuelle et cible.
- 📦 [SceneResult](docs/scene-result.md) : contrat de sortie du LLM.
- 🧵 [Prompt builder](docs/prompt-builder.md) : construction du prompt narratif.
- 👤 [Character system](docs/character-system.md) : structure des personnages.
- 💞 [Relationship system](docs/relationship-system.md) : relations dynamiques.
- 🧠 [Memory system](docs/memory-system.md) : souvenirs et recuperation contextuelle.
- 🌍 [World simulation](docs/world-simulation.md) : simulation hors champ.
- 🛣️ [Roadmap](docs/roadmap.md) : prochaines phases.

## 🛠️ Technologies

Actuel :

- Python ;
- JSON local ;
- OpenAI API ;
- CLI.

Prevues plus tard :

- FastAPI ;
- SQLite ;
- React ou Vue ;
- eventuellement d'autres fournisseurs IA ou des modeles locaux.

## 🚀 Lancement Du Prototype

Depuis la racine du projet :

```powershell
py .\backend\main.py
```

Le prototype charge l'univers `off-campus`, genere une scene d'ouverture, attend une action du joueur, genere la suite, valide la reponse, applique les relations, les souvenirs, certains changements de monde et le journal d'evenements, avance le temps, puis sauvegarde les personnages et le monde.
