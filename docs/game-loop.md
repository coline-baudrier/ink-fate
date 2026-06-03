# Game Loop

La game loop definit ce qui se passe a chaque interaction entre le joueur et Ink & Fate.

Elle transforme une action joueur en :

- scene narrative ;
- dialogues ;
- actions objectives ;
- evenements ;
- changements relationnels ;
- sauvegarde des personnages.

## Boucle Actuelle

```md
1. Charger world.json.
2. Charger les personnages.
3. Construire le contexte de scene active.
4. Generer une scene d'ouverture.
5. Afficher la scene d'ouverture.
6. Stocker cette scene dans l'historique.
7. Lire l'action du joueur.
8. Construire un prompt avec l'historique et l'action.
9. Envoyer au LLM.
10. Parser le JSON.
11. Filtrer le SceneResult.
12. Appliquer les updates relationnels.
13. Sauvegarder les personnages.
14. Afficher la nouvelle scene.
15. Ajouter l'action et la scene a l'historique.
16. Recommencer.
```

## Entree Joueur

Le joueur peut ecrire librement.

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

Plus tard, le moteur pourra classer :

- parole ;
- action ;
- texto ;
- intention narrative ;
- ellipse.

## Prompt

Le prompt builder recoit :

- l'univers ;
- la scene active ;
- le lieu ;
- les personnages presents ;
- l'historique de scene ;
- l'action joueur ;
- les regles narratives ;
- le format `SceneResult`.

Il doit rappeler que le LLM ne controle jamais le personnage joueur.

## SceneResult

Le LLM doit retourner un JSON.

Le moteur filtre actuellement :

- les dialogues dont le speaker est invalide ;
- les dialogues du personnage joueur ;
- les actions dont le personnage est invalide ;
- les evenements mal formes ou sans participant valide ;
- les updates relationnels avec source ou target invalide ;
- les deltas relationnels non numeriques ;
- les deltas relationnels hors limites.

Voir [scene-result.md](scene-result.md).

## Application Des Relations

Le LLM propose des deltas.

```json
{
  "source": "dean",
  "target": "elina",
  "changes": {
    "attraction": 3,
    "respect": 1
  }
}
```

Le validator limite d'abord les deltas entre `-5` et `5`.

Puis le relationship engine applique les changements a la relation `source -> target` et limite la valeur finale entre `0` et `100`.

## Renderer

Le renderer transforme le `SceneResult` en texte CLI.

Exemple :

```md
Dean s'approche avec un sourire insolent.

dean:
"Alors, c'est toi la fameuse petite soeur de Beau ?"
```

Pour le MVP, ce rendu simple suffit.

## Non Encore Gere

La boucle ne gere pas encore :

- la mise a jour de l'heure ;
- le changement de scene active ;
- la creation de souvenirs ;
- la simulation hors champ ;
- la sauvegarde d'un historique de partie separe.

## Objectif Du Prochain Palier

Le prochain palier logique :

```md
SceneResult
-> relationship updates
-> memory updates
-> world updates
-> saved game state
```
