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

**Statut : fait pour le MVP.**

✅ Deja fait :

- verification des listes/dictionnaires de base ;
- suppression des dialogues invalides ;
- suppression des dialogues du joueur ;
- suppression des actions invalides ;
- suppression des evenements invalides ou vides ;
- suppression des updates relationnels invalides ;
- suppression des updates memoire invalides ;
- limitation des deltas relationnels ;
- limitation des deltas relationnels par dimension ;
- limitation de l'importance des souvenirs ;
- validation des champs principaux de `scene` ;
- validation de `scene.location` ;
- validation de `scene.time` ;
- validation de `scene.participants` ;
- validation des champs secondaires de `actions` ;
- validation des champs secondaires de `events` ;
- validation des champs secondaires de `memory_updates` ;
- validation des champs secondaires de `relationship_updates` ;
- validation du lieu demande dans `world_updates.new_location` ;
- limitation de `world_updates.time_advance_minutes` ;
- validation des lieux dans `world_updates.character_movements` ;
- protection contre les types invalides dans `world_updates` ;
- produire un rapport de validation lisible.

## 💞 Phase 3 - Relations Persistantes

**Statut : fait pour le MVP.**

✅ Deja fait :

- appliquer les `relationship_updates` ;
- limiter les valeurs finales entre `0` et `100` ;
- produire des paliers narratifs de relation ;
- reinjecter le statut relationnel dans le prompt ;
- sauvegarder les personnages modifies en JSON.

🔮 Ameliorations futures :

- creer une relation manquante si elle n'existe pas ;
- afficher les changements relationnels de facon plus lisible.

## 🧠 Phase 4 - Memoire Simple

**Statut : fait pour le MVP.**

✅ Deja fait :

- demander des `memory_updates` au LLM ;
- valider proprietaire et contenu ;
- limiter l'importance ;
- sauvegarder les souvenirs dans les personnages ;
- selectionner les souvenirs pertinents par score ;
- reinjecter les souvenirs pertinents dans le prompt ;
- vieillir les souvenirs ;
- eviter de vieillir les souvenirs crees pendant le tour courant ;
- eviter les doublons exacts ;
- valider des types de souvenirs autorises ;
- enrichir le scoring avec les relations, lieux et evenements.

🔮 Ameliorations futures :

- enrichir encore le scoring avec plus de signaux narratifs ;
- ajouter des types de souvenirs plus specialises si le gameplay en a besoin.

## 🌍 Phase 5 - Updates Du Monde

**Statut : partiellement fait.**

✅ Deja fait :

- avancer l'heure ;
- sauvegarder l'etat runtime dans `data/saves` sans modifier le canon ;
- choisir une sauvegarde runtime avec un `save_id` ;
- charger la sauvegarde runtime si elle existe ;
- sauvegarder le world runtime et les personnages runtime ensemble ;
- supprimer la sauvegarde runtime avec la commande `reset` ;
- consulter les SMS stockes depuis la boucle CLI ;
- envoyer une reponse SMS joueur hors scene ;
- journaliser les reponses SMS joueur dans `event_log` ;
- creer des consequences narratives SMS simples, comme `planned_meeting` ;
- stocker les rendez-vous concrets dans `planned_events` ;
- creer un `planned_event` depuis une conversation a voix haute claire ;
- reinjecter les `planned_events` dans le prompt ;
- creer des souvenirs PNJ simples a partir des reponses SMS ;
- generer une confirmation SMS Dean -> Elina pour le rendez-vous patinoire ;
- permettre au LLM d'ecrire le contenu d'une reponse SMS PNJ autorisee, avec fallback deterministe ;
- generer une reponse SMS PNJ LLM generique quand le joueur envoie un SMS significatif a un PNJ contactable ;
- generer des SMS PNJ hors scene depuis des `message_triggers` configurables ;
- permettre au LLM d'ecrire le contenu des SMS PNJ inities par trigger, avec fallback deterministe ;
- ajouter des directives HRP runtime sans modifier le scenario canon ;
- reinjecter les directives HRP runtime dans le prompt ;
- reconstruire le contexte de scene ;
- appliquer `world_updates.new_location` ;
- changer le lieu actif ;
- suivre la position des personnages avec `character_locations` ;
- recalculer les participants selon le lieu actif ;
- appliquer `world_updates.time_advance_minutes` ;
- gerer le passage au jour suivant quand minuit est depasse ;
- enregistrer les evenements dans `event_log` ;
- appliquer des plannings PNJ simples ;
- proteger les participants actifs contre les mouvements automatiques de schedule ;
- limiter les dialogues PNJ quand le joueur les laisse explicitement derriere ;
- enregistrer les mouvements PNJ hors champ dans `event_log`.

🚧 Reste a faire :

- mieux choisir les evenements de `event_log` a reinjecter dans le prompt ;
- mieux simuler les consequences hors champ.

## 🌙 Phase 6 - Ellipses Et Simulation Hors Champ

**Statut : partiellement fait.**

- detection d'ellipses simples ;
- evenements hors champ avances ;
- souvenirs hors champ ;
- visibilite `visible`, `discoverable`, `hidden`.

## 🧭 Phase 6bis - Arcs Narratifs Souples

**Statut : fait pour la guidance MVP.**

✅ Deja fait :

- definir des `story_arcs` dans `scenario.json` ;
- reinjecter les arcs actifs dans le prompt ;
- stocker un `arc_state` runtime dans le world ;
- observer des signaux simples depuis les scenes et les SMS ;
- reinjecter les beats deja joues dans le prompt ;
- eviter les doublons de signaux observes ;
- formater les questions dramatiques, tensions, beats disponibles et beats bloques ;
- rappeler au LLM que les beats sont des opportunites, pas des obligations ;
- bloquer narrativement les raccourcis comme `love_confession` ou `official_couple` trop tot ;
- laisser la possibilite que la romance progresse, stagne, bifurque ou echoue.

🔮 Ameliorations futures :

- faire progresser `phase` et `status` en runtime selon les signaux relationnels et les souvenirs ;
- proposer des arcs non romantiques ;
- produire un rapport leger quand le LLM tente un beat bloque.

## 🧼 Phase 7 - Nettoyage Et Tests

**Statut : partiellement fait.**

- tests unitaires du validator ;
- tests du world engine ;
- tests du memory engine ;
- tests du relationship engine ;
- tests du time engine ;
- tests de l'event log ;
- nettoyage des accents dans les JSON ;
- documentation a jour.

## 🖥️ Phase 8 - API Et Interface

**Statut : futur.**

- API FastAPI ;
- base SQLite ;
- frontend React ou Vue ;
- sauvegardes multiples ;
- selection d'univers.
