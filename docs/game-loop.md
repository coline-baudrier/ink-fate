# Game Loop

La game loop definit ce qui se passe a chaque interaction entre le joueur et Ink & Fate.

## Boucle Actuelle

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
10. Appliquer les updates relationnels.
11. Appliquer les memory_updates.
12. Vieillir les souvenirs.
13. Avancer l'heure du monde.
14. Sauvegarder world.json.
15. Sauvegarder les personnages.
16. Reconstruire le contexte de scene.
17. Afficher la nouvelle scene.
18. Ajouter l'action et la scene a l'historique.
19. Recommencer.
```

## Entree Joueur

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

## ScenePipeline

Le pipeline de scene fait :

```md
PromptBuilder
-> OpenAI
-> SceneResultParser
-> SceneValidator
-> SceneResult valide
```

Cela permet a `main.py` de rester plus simple.

## Effets Persistants

Apres validation, le moteur applique :

- `relationship_updates` avec `relationship_engine.py` ;
- `memory_updates` avec `memory_engine.py` ;
- avancee de temps avec `world_engine.py` et `time_engine.py`.

Les personnages et le monde sont ensuite sauvegardes en JSON.

## Non Encore Gere

La boucle ne gere pas encore :

- changement de lieu via `SceneResult` ;
- mise a jour de `active_scene` ;
- sauvegarde de partie separee ;
- ellipses longues ;
- simulation hors champ.

## Objectif Du Prochain Palier

Le prochain palier logique :

```md
SceneResult
-> world_updates
-> active_scene update
-> event log
-> saved game state
```
