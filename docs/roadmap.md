# Roadmap

La roadmap separe le prototype actuel, le MVP jouable et les extensions futures.

## Phase 0 - Prototype Actuel

Statut : en cours.

Objectif :

- charger un univers ;
- charger des personnages ;
- construire un contexte de scene ;
- construire un prompt ;
- appeler le LLM ;
- parser un `SceneResult`.

Travail restant dans cette phase :

- stabiliser le parsing JSON ;
- harmoniser le format attendu du `SceneResult` ;
- ajouter un rendu texte simple.

## Phase 1 - Boucle Joueur CLI

Objectif :

- afficher la scene ;
- lire une action joueur ;
- regenerer la suite ;
- continuer tant que le joueur joue.

Livrables :

- boucle CLI ;
- renderer texte ;
- prompt incluant l'action joueur ;
- interdiction explicite de controler le joueur.

## Phase 2 - Validation SceneResult

Objectif :

- ne jamais appliquer aveuglement la sortie LLM.

Livrables :

- schema de validation ;
- verification des champs obligatoires ;
- verification des personnages ;
- verification des lieux ;
- limites sur les updates relationnelles ;
- rejet ou correction des valeurs invalides.

## Phase 3 - Updates Du Monde

Objectif :

- transformer un `SceneResult` valide en nouvel etat du monde.

Livrables :

- avancee du temps ;
- mise a jour de la scene active ;
- creation d'evenements ;
- creation de souvenirs ;
- application limitee des relations ;
- sauvegarde JSON.

## Phase 4 - Memoire Simple

Objectif :

- permettre aux personnages de se souvenir des evenements importants.

Livrables :

- souvenirs par personnage ;
- importance de 1 a 100 ;
- tags ;
- recuperation simple par personnage present ;
- injection selective dans le prompt.

## Phase 5 - Ellipses Et Simulation Hors Champ

Objectif :

- simuler ce qui se passe quand le joueur laisse passer du temps.

Livrables :

- detection d'ellipses simples ;
- evenements hors champ ;
- souvenirs hors champ ;
- visibilite `visible`, `discoverable`, `hidden`.

## Phase 6 - API Et Interface

Objectif :

- sortir du prototype CLI.

Livrables possibles :

- API FastAPI ;
- base SQLite ;
- frontend React ou Vue ;
- sauvegardes multiples ;
- selection d'univers ;
- historique de scenes.

## Phase 7 - Systeme Narratif Avance

Objectif :

- soutenir des histoires longues et complexes.

Livrables possibles :

- arcs narratifs ;
- systeme de secrets ;
- messagerie ;
- recherche avancee de souvenirs ;
- simulation sociale plus riche ;
- plusieurs univers ;
- plusieurs personnages simultanes.
