# MVP 1

Le MVP 1 doit produire une premiere boucle jouable simple.

L'objectif n'est pas encore de simuler un monde complet. L'objectif est de prouver que le moteur peut charger un etat narratif, recevoir une action joueur, generer une scene structuree, puis appliquer des changements simples.

## Perimetre

Inclus dans le MVP :

- interface CLI ;
- stockage local en JSON ;
- un seul univers : `off-campus` ;
- un seul scenario de depart ;
- trois personnages : Elina, Beau et Dean ;
- une scene active ;
- entree libre du joueur ;
- generation de scene par LLM ;
- sortie structuree `SceneResult` ;
- validation minimale du JSON ;
- rendu texte lisible ;
- mise a jour simple du temps ;
- mise a jour simple des relations ;
- creation de souvenirs simples ;
- sauvegarde du nouvel etat.

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

## Boucle Jouable Attendue

La premiere boucle doit ressembler a ceci :

```md
1. Charger le WorldState.
2. Charger les personnages de la scene.
3. Afficher la scene actuelle.
4. Lire l'action du joueur.
5. Construire le prompt.
6. Appeler le LLM.
7. Parser le SceneResult.
8. Valider le SceneResult.
9. Afficher la scene generee.
10. Appliquer les updates autorises.
11. Sauvegarder le nouvel etat.
12. Attendre la prochaine action du joueur.
```

## Exemple D'Interaction

```md
Moteur :
Dean s'approche avec un sourire insolent.

Dean :
Alors, c'est toi la fameuse petite soeur de Beau ?

Joueur :
Je leve les yeux au ciel et je garde ma valise contre moi.
```

Le moteur doit ensuite generer :

- une narration ;
- des dialogues de PNJ ;
- des actions objectives ;
- des updates relationnelles ;
- des souvenirs eventuels ;
- une avancee de temps eventuelle.

## Criteres De Fin

Le MVP 1 est termine quand :

- le joueur peut saisir une action dans la CLI ;
- le moteur genere une suite coherente ;
- le joueur n'est jamais force dans ses pensees, emotions ou dialogues ;
- la reponse LLM est un JSON valide ;
- le JSON est valide avant application ;
- les relations peuvent evoluer avec des limites ;
- des souvenirs simples peuvent etre crees ;
- l'etat du monde peut etre sauvegarde ;
- une nouvelle action peut continuer la scene.

## Priorite De Conception

Le LLM propose.

Le moteur decide.

Le LLM peut suggerer une relation, un evenement ou un souvenir. Le moteur doit verifier que la suggestion est valide, coherente et limitee avant de l'appliquer.
