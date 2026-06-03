# 🛣️ Roadmap

La roadmap separe ce qui existe deja, ce qui est partiel et les extensions futures.

## ✅ Phase 0 - Prototype De Base

**Statut : fait.**

- charger un univers ;
- charger des personnages ;
- construire un contexte de scene ;
- construire un prompt ;
- appeler le LLM ;
- parser un `SceneResult`.

## ✅ Phase 1 - Boucle Joueur CLI

**Statut : fait.**

- scene d'ouverture ;
- entree joueur ;
- generation de suite ;
- historique de scene ;
- commande `quit` ou `exit`.

## 🧪 Phase 2 - Validation SceneResult

**Statut : partiellement fait.**

✅ Deja fait :

- verification des listes/dictionnaires de base ;
- suppression des dialogues invalides ;
- suppression des dialogues du joueur ;
- suppression des actions invalides ;
- suppression des evenements invalides ou vides ;
- suppression des updates relationnels invalides ;
- suppression des updates memoire invalides ;
- limitation des deltas relationnels ;
- limitation de l'importance des souvenirs.

🚧 Reste a faire :

- verifier les champs obligatoires de `scene` ;
- verifier les lieux ;
- verifier les types de chaque champ ;
- produire un rapport de validation lisible.

## 💞 Phase 3 - Relations Persistantes

**Statut : fait pour le MVP.**

✅ Deja fait :

- appliquer les `relationship_updates` ;
- limiter les valeurs finales entre `0` et `100` ;
- sauvegarder les personnages modifies en JSON.

🔮 Ameliorations futures :

- creer une relation manquante si elle n'existe pas ;
- afficher les changements relationnels de facon plus lisible ;
- tester les cas limites.

## 🧠 Phase 4 - Memoire Simple

**Statut : partiellement fait.**

✅ Deja fait :

- demander des `memory_updates` au LLM ;
- valider proprietaire et contenu ;
- limiter l'importance ;
- sauvegarder les souvenirs dans les personnages ;
- reinjecter quelques souvenirs dans le prompt ;
- vieillir les souvenirs.

🚧 Reste a faire :

- eviter de vieillir les souvenirs tout juste crees ;
- mieux choisir les souvenirs pertinents ;
- eviter les doublons ;
- ajouter des types de souvenirs plus stricts.

## 🌍 Phase 5 - Updates Du Monde

**Statut : partiellement fait.**

✅ Deja fait :

- avancer l'heure ;
- sauvegarder `world.json` ;
- reconstruire le contexte de scene.

🚧 Reste a faire :

- changer `active_scene` ;
- changer de lieu ;
- appliquer des `world_updates` depuis le `SceneResult` ;
- gerer les jours quand minuit est depasse ;
- enregistrer les evenements.

## 🌙 Phase 6 - Ellipses Et Simulation Hors Champ

**Statut : a faire.**

- detection d'ellipses simples ;
- evenements hors champ ;
- souvenirs hors champ ;
- visibilite `visible`, `discoverable`, `hidden`.

## 🧼 Phase 7 - Nettoyage Et Tests

**Statut : a faire.**

- tests unitaires du validator ;
- tests du relationship engine ;
- tests du memory engine ;
- tests du time engine ;
- nettoyage des accents dans les JSON ;
- documentation a jour.

## 🖥️ Phase 8 - API Et Interface

**Statut : futur.**

- API FastAPI ;
- base SQLite ;
- frontend React ou Vue ;
- sauvegardes multiples ;
- selection d'univers.
