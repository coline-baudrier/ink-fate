# 🎮 MVP 1

Le MVP 1 vise une boucle jouable simple, disponible en CLI et dans une interface web.

## ✅ Inclus Aujourd'hui

- un seul univers : `off-campus` ;
- neuf fiches personnages dans l'univers, avec Elina, Beau et Dean comme trio central initial ;
- une scene active ;
- stockage local en JSON ;
- generation de scene par LLM ;
- boucle CLI avec entree joueur ;
- API FastAPI ;
- frontend React/Vite ;
- streaming SSE des scenes dans l'interface web ;
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
- positions des personnages dans le world runtime ;
- validation des mouvements de PNJ ;
- sauvegarde runtime separee du canon ;
- `save_id` CLI pour choisir une partie ;
- SMS hors scene MVP ;
- consultation des SMS stockes ;
- reponses SMS joueur stockees et loggees ;
- directives HRP runtime.

## 🚧 Encore Partiel

- selection encore plus fine des souvenirs/evenements ;
- progression romance plus structuree sur le long terme ;
- detection d'ellipses ;
- reponses SMS PNJ encore plus contextuelles, avec decisions narratives plus fines avant appel LLM.

## ⛔ Exclu Du MVP

- base SQLite ;
- plusieurs univers jouables ;
- selection de sauvegarde dans le frontend ;
- authentification et multi-utilisateur ;
- simulation permanente ;
- systeme d'arcs narratifs complet.

## 🔁 Boucle MVP Actuelle

```md
Joueur
-> CLI `main.py` ou API `api_main.py`
-> scene_pipeline.py
-> prompt_builder.py
-> OpenAI
-> scene_result_parser.py
-> scene_validator.py
-> relationship_engine.py
-> contact_engine.py
-> memory_engine.py
-> world_engine.py
-> message_engine.py
-> runtime_save.py
-> renderer.py / reponse API
-> Joueur
```

## 🧠 Priorite De Conception

Le LLM propose.

Le moteur decide.

Le moteur ne doit jamais appliquer une sortie LLM sans validation.
