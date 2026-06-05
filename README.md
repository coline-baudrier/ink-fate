# Ink & Fate

Ink & Fate est un prototype Python de moteur narratif IA pour roman interactif.

Le but n'est pas de creer un simple chatbot de roleplay, mais un moteur capable de faire vivre une histoire dans un univers peuple de personnages autonomes. Le joueur incarne son propre personnage, agit librement, et le moteur genere la suite en tenant compte du contexte, de l'historique de scene et des relations entre personnages.

## 📍 Statut Actuel

Le projet est actuellement un prototype jouable avec deux interfaces :

- une CLI Python ;
- une interface web React connectee a une API FastAPI.

✅ Ce qui existe deja :

- chargement d'un univers depuis des fichiers JSON ;
- chargement des personnages ;
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
- arcs narratifs souples reinjectes au prompt ;
- etat observe des arcs narratifs reinjecte au prompt ;
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
- avancee et sauvegarde du temps dans la sauvegarde runtime ;
- passage au jour suivant apres minuit ;
- changements simples de lieu via `world_updates` ;
- positions des personnages sauvegardees dans la sauvegarde runtime ;
- plannings simples pour les PNJ ;
- mouvements PNJ hors champ sauvegardes dans `event_log` ;
- protection des PNJ presents en scene contre les mouvements automatiques de schedule ;
- validation des mouvements de personnages proposes par le LLM ;
- journal d'evenements persistant ;
- evenements planifies runtime pour les rendez-vous concrets ;
- sauvegardes runtime separees dans `data/saves` avec `save_id` ;
- SMS hors scene stockes, consultables et repondables depuis le CLI.
- directives HRP runtime avec `/hrp`, `/rule` et `/context`.
- API FastAPI pour demarrer ou reprendre une partie, jouer une action, streamer une scene en SSE, lire ou envoyer des SMS et reinitialiser la sauvegarde par defaut ;
- frontend React/Vite avec fil narratif, saisie structuree, panneau SMS, date, heure et remise a zero.

🚧 Ce qui reste partiel :

- selection encore plus fine des souvenirs/evenements ;
- simulation hors champ avancee ;
- choix de l'univers et de la sauvegarde depuis l'interface web ;
- persistance SQLite et gestion multi-utilisateur ;
- couverture de tests dediee aux routes FastAPI et au frontend.

## 🎮 MVP 1

Le MVP 1 vise une boucle jouable simple :

- un seul univers : `off-campus` ;
- neuf fiches personnages, avec Elina, Beau et Dean au coeur du scenario initial ;
- une scene active ;
- stockage local en JSON ;
- interfaces CLI et web ;
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
- 🧪 [Audit du 5 juin 2026](docs/audit-2026-06-05.md) : verification locale, ecarts et risques observes.

## 🛠️ Technologies

Actuel :

- Python ;
- FastAPI ;
- JSON local ;
- OpenAI API ;
- CLI ;
- React et Vite.

Prevues plus tard :

- SQLite ;
- selection d'univers et de sauvegarde dans l'interface ;
- eventuellement d'autres fournisseurs IA ou des modeles locaux.

## 🚀 Installation

Prerequis :

- Python 3.10 ou plus recent ;
- Node.js et npm ;
- une cle API OpenAI.

Depuis la racine :

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r .\backend\requirements.txt
npm --prefix .\frontend install
```

Creer un fichier `.env` a la racine :

```dotenv
OPENAI_API_KEY=...
```

Variables optionnelles :

```dotenv
INK_FATE_SAVE_ID=partie-1
INK_FATE_ENABLE_LLM_SMS=1
```

## 🚀 Lancement Du Prototype

### Interface web

```powershell
.\start.ps1
```

Le script lance :

- API : `http://localhost:8000` ;
- documentation OpenAPI : `http://localhost:8000/docs` ;
- frontend : `http://localhost:5173`.

L'API et le frontend utilisent actuellement l'univers `off-campus` et la sauvegarde runtime `default`.

### CLI

Depuis la racine du projet :

```powershell
py .\backend\main.py
```

Pour choisir une sauvegarde runtime :

```powershell
py .\backend\main.py --save-id partie-1
```

Dans la boucle CLI, les commandes `messages`, `sms` ou `inbox` affichent les SMS stockes pour le joueur. La commande `reply dean: texte` envoie une reponse SMS hors scene et l'ajoute a `event_log`. Certains SMS peuvent aussi creer des consequences narratives simples, comme un rendez-vous planifie ou un souvenir PNJ. Les rendez-vous concrets sont stockes dans `planned_events` et peuvent aussi venir d'une conversation a voix haute claire. Les PNJ peuvent envoyer des SMS hors scene depuis des `message_triggers` configurables dans `scenario.json`, avec anti-spam par trigger. Dean peut envoyer une confirmation automatique pour le rendez-vous patinoire. Par defaut, les SMS configures utilisent un fallback deterministe ; avec `INK_FATE_ENABLE_LLM_SMS=1`, leur texte peut etre ecrit par le LLM, puis nettoye et valide avant stockage. Quand cette option est active, un PNJ contactable peut aussi repondre via LLM a un SMS joueur significatif. Les commandes `/hrp`, `/rule` et `/context` ajoutent des directives d'auteur dans la sauvegarde runtime, sans modifier `scenario.json`. La commande `directives` les affiche, `clear_directives` les supprime, et `reset` supprime seulement la sauvegarde runtime active en laissant le canon dans `data/universes` intact.

Le prototype charge l'univers `off-campus`, genere une scene d'ouverture, attend une action du joueur, genere la suite, valide la reponse, applique les relations, les souvenirs, certains changements de monde et le journal d'evenements, avance le temps, puis sauvegarde l'etat de partie dans `data/saves`.

## Verification locale

```powershell
py -m pytest -q
npm --prefix .\frontend run lint
npm --prefix .\frontend run build
```

## Tests LLM optionnels

Les tests qui appellent l'API OpenAI sont marques `llm` et sont ignores par defaut.

Pour les lancer explicitement depuis PowerShell :

```powershell
$env:INK_FATE_RUN_LLM_TESTS="1"
py -m pytest tests/llm
```

Ils necessitent aussi `OPENAI_API_KEY`.
