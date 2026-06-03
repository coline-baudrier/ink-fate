# 🎮 MVP 1

Le MVP 1 vise une boucle jouable simple dans la CLI.

## ✅ Inclus Aujourd'hui

- un seul univers : `off-campus` ;
- trois personnages : Elina, Beau et Dean ;
- une scene active ;
- stockage local en JSON ;
- generation de scene par LLM ;
- boucle CLI avec entree joueur ;
- historique de scene ;
- validation du `SceneResult` ;
- rendu texte ;
- relations persistantes ;
- paliers narratifs de relations ;
- souvenirs persistants ;
- selection pertinente des souvenirs ;
- journal d'evenements ;
- evenements recents reinjectes au prompt ;
- statut relationnel reinjecte au prompt ;
- regles de pacing dans le scenario ;
- validation des champs secondaires du `SceneResult` ;
- temps qui avance ;
- passage au jour suivant apres minuit ;
- changements simples de lieu ;
- positions des personnages dans `world.json` ;
- validation des mouvements de PNJ ;
- sauvegarde de `world.json` et des personnages.

## 🚧 Encore Partiel

- selection encore plus fine des souvenirs/evenements ;
- progression romance plus structuree sur le long terme ;
- detection d'ellipses ;
- sauvegarde de partie separee.

## ⛔ Exclu Du MVP

- frontend ;
- API FastAPI ;
- base SQLite ;
- plusieurs univers jouables ;
- simulation permanente ;
- systeme d'arcs narratifs complet.

## 🔁 Boucle MVP Actuelle

```md
Joueur
-> main.py
-> scene_pipeline.py
-> prompt_builder.py
-> OpenAI
-> scene_result_parser.py
-> scene_validator.py
-> relationship_engine.py
-> memory_engine.py
-> world_engine.py
-> sauvegarde JSON
-> renderer.py
-> Joueur
```

## 🧠 Priorite De Conception

Le LLM propose.

Le moteur decide.

Le moteur ne doit jamais appliquer une sortie LLM sans validation.
