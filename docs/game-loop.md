# 🔁 Game Loop

La game loop definit ce qui se passe a chaque interaction entre le joueur et Ink & Fate.

## 🎮 Boucle Actuelle

```md
1. Charger world.json.
2. Charger les personnages.
3. Construire le contexte de scene active.
4. Generer une scene d'ouverture.
5. Afficher la scene d'ouverture.
6. Stocker cette scene dans l'historique.
7. Lire l'action du joueur.
8. Generer une nouvelle scene via scene_pipeline.
9. Valider le SceneResult.
10. Appliquer les effets personnages via `character_state_engine`.
11. Appliquer les updates relationnels.
12. Appliquer les memory_updates.
13. Vieillir les souvenirs.
14. Avancer l'heure du monde.
15. Sauvegarder world.json.
16. Sauvegarder les personnages.
17. Reconstruire le contexte de scene.
18. Afficher la nouvelle scene.
19. Ajouter l'action et la scene a l'historique.
20. Recommencer.
```

## ✍️ Entree Joueur

Le joueur ecrit librement dans la CLI.

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

Pour l'instant, l'entree est envoyee au prompt comme une action libre.

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
- avancee de temps avec `world_engine.py` et `time_engine.py`.

Les personnages et le monde sont ensuite sauvegardes en JSON.

## 🚧 Non Encore Gere

La boucle ne gere pas encore :

- changement de lieu via `SceneResult` ;
- mise a jour de `active_scene` ;
- sauvegarde de partie separee ;
- ellipses longues ;
- simulation hors champ.

## 🎯 Objectif Du Prochain Palier

Le prochain palier logique :

```md
SceneResult
-> world_updates
-> active_scene update
-> event log
-> saved game state
```
