# 🔁 Game Loop

La game loop definit ce qui se passe a chaque interaction entre le joueur et Ink & Fate.

## 🎮 Boucle Actuelle

```md
1. Determiner le `save_id`.
2. Charger le world runtime s'il existe, sinon le world canon.
3. Charger les personnages runtime s'ils existent, sinon les personnages canon.
4. Construire le contexte de scene active.
5. Generer une scene d'ouverture.
6. Afficher la scene d'ouverture.
7. Stocker cette scene dans l'historique.
8. Lire l'action du joueur.
9. Si l'entree est une commande runtime, l'appliquer sans appel LLM.
10. Sinon, generer une nouvelle scene via scene_pipeline.
11. Valider le SceneResult.
12. Appliquer les effets personnages via `character_state_engine`.
13. Appliquer les updates relationnels.
14. Appliquer les contact_updates.
15. Appliquer les memory_updates.
16. Vieillir les souvenirs.
17. Appliquer les consequences monde via `update_world_after_turn`.
18. Ajouter les evenements valides dans `event_log`.
19. Avancer l'heure du monde.
20. Appliquer les plannings PNJ hors scene.
21. Recalculer les participants.
22. Generer les SMS hors scene eventuels.
23. Sauvegarder le world et les personnages runtime dans `data/saves`.
24. Reconstruire le contexte de scene.
25. Afficher la nouvelle scene.
26. Ajouter l'action et la scene a l'historique.
27. Recommencer.
```

## ✍️ Entree Joueur

Le joueur ecrit librement dans la CLI ou dans le frontend.

Exemples :

```md
Je souris a Dean.
```

```md
Je recupere ma valise et je leve les yeux au ciel.
```

```md
Dean, tu es ou ?
```

Les entrees RP sont envoyees au prompt comme des actions libres. Les commandes runtime sont interceptees avant le LLM.

Dans le frontend, `POST /game/action/stream` renvoie les entrees de scene sous forme d'evenements SSE. La sauvegarde est effectuee avant l'envoi du flux au navigateur.

Commandes runtime actuelles :

- `messages`, `sms`, `inbox` : consulter les SMS du joueur et les marquer comme lus ;
- `reply dean: texte`, `sms dean: texte`, `text dean: texte` : envoyer une reponse SMS hors scene ;
- `/hrp texte` : ajouter une note HRP runtime ;
- `/rule texte` : ajouter une regle runtime ;
- `/context texte` : ajouter un contexte runtime ;
- `directives`, `rules`, `hrp` : afficher les directives runtime ;
- `clear_directives`, `clear rules` : supprimer les directives runtime ;
- `reset` : supprimer la sauvegarde runtime active ;
- `quit`, `exit` : quitter.

## 🧪 ScenePipeline

Le pipeline de scene fait :

```md
PromptBuilder
-> OpenAI
-> SceneResultParser
-> SceneValidator
-> SceneResult valide
```

Cela permet a `main.py` de rester plus simple.

## 💾 Effets Persistants

Apres validation, le moteur applique :

- les effets personnages avec `character_state_engine.py` ;
- `relationship_updates` avec `relationship_engine.py` ;
- `memory_updates` et vieillissement des souvenirs avec `memory_engine.py` ;
- changements de lieu et positions avec `world_engine.py` ;
- journal d'evenements avec `event_log_engine.py` ;
- plannings PNJ avec `npc_schedule_engine.py` ;
- avancee de temps avec `world_engine.py` et `time_engine.py` ;
- messages hors scene avec `message_engine.py` ;
- sauvegarde de partie avec `runtime_save.py`.

Les personnages et le monde sont ensuite sauvegardes en JSON dans `data/saves`, pas dans le canon `data/universes`.

Pendant un tour, les PNJ presents dans la scene active ne sont pas deplaces par leur schedule. Un schedule peut seulement bouger un PNJ hors scene, sauf si la narration a explicitement deplace ce personnage.

## 🚧 Non Encore Gere

La boucle ne gere pas encore :

- ellipses longues ;
- simulation hors champ avancee ;
- choix du `save_id` et de l'univers depuis le frontend.

## 🎯 Objectif Du Prochain Palier

Le prochain palier logique :

```md
SMS stocke
-> reponse joueur
-> action narrative hors scene face-a-face
-> reponse PNJ optionnelle deterministe ou LLM
-> consequences relationnelles/memoire
-> saved game state
```
