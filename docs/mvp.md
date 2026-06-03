# MVP 1

Le MVP 1 doit produire une boucle jouable simple.

L'objectif n'est pas encore de simuler un monde complet. L'objectif est de prouver que le moteur peut charger un etat narratif, recevoir une action joueur, generer une scene structuree, valider la sortie du LLM, appliquer des changements relationnels simples et sauvegarder les personnages.

## Perimetre Actuel

Inclus aujourd'hui :

- interface CLI ;
- stockage local en JSON ;
- un seul univers : `off-campus` ;
- un seul scenario de depart ;
- trois personnages : Elina, Beau et Dean ;
- une scene active ;
- entree libre du joueur ;
- generation de scene par LLM ;
- historique de scene renvoye au prompt ;
- sortie structuree `SceneResult` ;
- parsing JSON ;
- validation minimale du `SceneResult` ;
- rendu texte lisible ;
- application simple des relations ;
- limitation des deltas relationnels ;
- limitation des valeurs finales de relation entre `0` et `100` ;
- sauvegarde des personnages modifies.

Encore partiel ou absent :

- mise a jour du temps ;
- changement de scene active ;
- creation de souvenirs ;
- sauvegarde de partie separee ;
- simulation hors champ ;
- validation complete de tous les champs ;
- gestion avancee des lieux.

Exclus du MVP :

- frontend ;
- API FastAPI ;
- base SQLite ;
- plusieurs univers jouables ;
- simulation permanente du monde ;
- gestion avancee des textos ;
- dix personnages simultanes ;
- moteur d'arcs narratifs complet ;
- recherche vectorielle de souvenirs ;
- systeme complexe de quetes.

## Boucle Jouable Actuelle

```md
1. Charger le WorldState.
2. Charger les personnages.
3. Construire la scene active.
4. Generer la scene d'ouverture.
5. Afficher la scene.
6. Lire l'action du joueur.
7. Construire le prompt avec l'historique.
8. Appeler le LLM.
9. Parser le SceneResult.
10. Filtrer les dialogues, actions, evenements et updates invalides.
11. Supprimer les dialogues du joueur.
12. Limiter les deltas relationnels.
13. Appliquer les updates relationnels.
14. Sauvegarder les personnages.
15. Afficher la suite.
16. Ajouter la suite a l'historique.
17. Attendre la prochaine action.
```

## Exemple D'Interaction

```md
Moteur :
Dean s'approche avec un sourire insolent.

Dean:
"Alors, c'est toi la fameuse petite soeur de Beau ?"

Joueur :
Je leve les yeux au ciel et je garde ma valise contre moi.
```

Le moteur doit ensuite generer :

- une narration ;
- des dialogues de PNJ ;
- des actions objectives ;
- des evenements eventuels ;
- des updates relationnels.

## Criteres De Fin MVP

Le MVP 1 sera termine quand :

- le joueur peut jouer plusieurs tours dans la CLI ;
- le moteur garde un historique coherent ;
- le joueur n'est jamais force dans ses pensees, emotions ou dialogues ;
- la reponse LLM est parse et filtree avant application ;
- les relations evoluent et sont sauvegardees ;
- les valeurs relationnelles restent entre `0` et `100` ;
- le temps ou la scene active peuvent etre mis a jour simplement ;
- quelques souvenirs simples peuvent etre crees et sauvegardes.

## Priorite De Conception

Le LLM propose.

Le moteur decide.

Le LLM peut suggerer une relation, un evenement ou un souvenir. Le moteur doit verifier que la suggestion est valide, coherente et limitee avant de l'appliquer.
