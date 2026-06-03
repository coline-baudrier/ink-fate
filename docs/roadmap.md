# Roadmap

La roadmap separe ce qui existe deja, ce qui est partiel et les extensions futures.

## Phase 0 - Prototype De Base

Statut : fait.

Livrables :

- charger un univers ;
- charger des personnages ;
- construire un contexte de scene ;
- construire un prompt ;
- appeler le LLM ;
- parser un `SceneResult`.

## Phase 1 - Boucle Joueur CLI

Statut : fait.

Livrables :

- afficher une scene d'ouverture ;
- lire une action joueur ;
- regenerer la suite ;
- garder un historique de scene ;
- continuer tant que le joueur joue ;
- quitter avec `quit` ou `exit`.

## Phase 2 - Validation SceneResult

Statut : partiellement fait.

Deja fait :

- verification des listes/dictionnaires de base ;
- suppression des dialogues invalides ;
- suppression des dialogues du joueur ;
- suppression des actions invalides ;
- suppression des evenements invalides ou vides ;
- suppression des updates relationnels invalides ;
- limitation des deltas relationnels.

Reste a faire :

- verifier les champs obligatoires de `scene` ;
- verifier les lieux ;
- verifier les types de chaque champ ;
- gerer proprement un JSON incomplet ;
- produire un rapport de validation lisible.

## Phase 3 - Relations Persistantes

Statut : partiellement fait.

Deja fait :

- appliquer les `relationship_updates` ;
- limiter les valeurs finales entre `0` et `100` ;
- sauvegarder les personnages modifies en JSON.

Reste a faire :

- creer une relation manquante si elle n'existe pas ;
- afficher les changements relationnels de facon plus lisible ;
- eviter de sauvegarder si aucune relation n'a change ;
- tester les cas limites.

## Phase 4 - Updates Du Monde

Statut : a faire.

Objectif :

- transformer un `SceneResult` valide en nouvel etat du monde.

Livrables :

- avancee du temps ;
- mise a jour de la scene active ;
- changement de lieu ;
- creation d'evenements ;
- sauvegarde d'un etat de partie.

## Phase 5 - Memoire Simple

Statut : a faire.

Objectif :

- permettre aux personnages de se souvenir des evenements importants.

Livrables :

- souvenirs par personnage ;
- importance de 1 a 100 ;
- tags ;
- sauvegarde JSON ;
- recuperation simple par personnage present ;
- injection selective dans le prompt.

## Phase 6 - Ellipses Et Simulation Hors Champ

Statut : a faire.

Objectif :

- simuler ce qui se passe quand le joueur laisse passer du temps.

Livrables :

- detection d'ellipses simples ;
- evenements hors champ ;
- souvenirs hors champ ;
- visibilite `visible`, `discoverable`, `hidden`.

## Phase 7 - API Et Interface

Statut : futur.

Livrables possibles :

- API FastAPI ;
- base SQLite ;
- frontend React ou Vue ;
- sauvegardes multiples ;
- selection d'univers ;
- historique de scenes.

## Phase 8 - Systeme Narratif Avance

Statut : futur.

Livrables possibles :

- arcs narratifs ;
- systeme de secrets ;
- messagerie ;
- recherche avancee de souvenirs ;
- simulation sociale plus riche ;
- plusieurs univers ;
- plusieurs personnages simultanes.
