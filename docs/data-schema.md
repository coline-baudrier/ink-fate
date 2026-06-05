# 🗂️ Schema De Donnees

Les donnees d'Ink & Fate sont stockees en JSON pendant le MVP.

Le moteur doit rester independant des univers. Les fichiers JSON decrivent l'univers, les personnages, les lieux et l'etat courant.

## 🌳 Arborescence Actuelle

```md
data/
  universes/
    off-campus/
      world.json
      scenario.json
      characters/
        elina.json
        beau.json
        dean.json
  saves/
    off-campus/
      default/
        world.json
        characters/
          elina.json
          beau.json
          dean.json
```

## 🌍 world.json

Dans `data/universes`, `world.json` represente l'etat canon de depart de l'univers.

Pendant une partie, l'etat courant est sauvegarde dans `data/saves/<universe>/<save_id>/world.json`. Le format reste le meme, avec quelques champs runtime supplementaires.

Structure actuelle :

```json
{
  "universe": {
    "id": "off-campus",
    "name": "Off Campus"
  },
  "timeline": {
    "current_date": "2026-09-01",
    "current_time": "10:00",
    "current_day": 1
  },
  "player_character": "elina",
  "locations": [],
  "characters": [],
  "active_events": [],
  "active_scene": {},
  "character_locations": {},
  "character_positions": {},
  "character_activities": {},
  "active_tasks": [],
  "scene_props": {},
  "event_log": [],
  "planned_events": [],
  "arc_state": {},
  "messages": [],
  "runtime_directives": [],
  "scene_history": []
}
```

Champs :

- `universe` : identite de l'univers charge.
- `timeline` : date, heure et jour courant.
- `player_character` : identifiant du personnage controle par le joueur.
- `locations` : lieux disponibles.
- `characters` : identifiants des personnages a charger.
- `active_events` : evenements importants en cours.
- `active_scene` : scene actuellement jouee.
- `character_locations` : position actuelle de chaque personnage.
- `character_positions` : position fine d'un personnage a l'interieur du lieu courant.
- `character_activities` : activite persistante en cours pour chaque personnage.
- `active_tasks` : taches partagees avec progression et participants.
- `scene_props` : details physiques persistants par lieu.
- `event_log` : journal des evenements importants deja arrives.
- `planned_events` : evenements concrets prevus pour plus tard dans la sauvegarde runtime.
- `arc_state` : signaux narratifs observes pour les arcs actifs pendant cette partie.
- `messages` : messages hors scene stockes dans la sauvegarde runtime.
- `runtime_directives` : directives HRP ajoutees pendant la partie.
- `scene_history` : derniers tours narratifs, limites a 20 dans les interfaces actuelles.

Important : les champs runtime evoluent dans `data/saves`. Le canon peut fournir des valeurs initiales, mais une partie ne doit jamais reecrire directement `data/universes`.

## 📍 Location

Un lieu doit avoir :

```json
{
  "id": "campus",
  "name": "Briar University Campus",
  "description": "Le campus de Briar University."
}
```

Champs :

- `id` : identifiant stable utilise par le moteur.
- `name` : nom affiche ou envoye au prompt.
- `description` : contexte narratif du lieu.

Important : le prompt builder lit actuellement `location["description"]`. Tout lieu pouvant devenir actif doit donc avoir une description.

## 🎬 active_scene

La scene active indique ou se passe la scene et quels personnages sont presents.

```json
{
  "location": "campus",
  "participants": ["beau", "elina", "dean"]
}
```

Champs :

- `location` : identifiant d'un lieu existant.
- `participants` : identifiants de personnages charges.

## Positions Des Personnages

`character_locations` stocke le lieu actuel de chaque personnage.

```json
{
  "elina": "dormitory",
  "beau": "campus",
  "dean": "campus"
}
```

Le moteur utilise ces positions pour recalculer `active_scene.participants` apres un changement de lieu.

Regles actuelles :

- les cles sont des IDs de personnages ;
- les valeurs sont des IDs de lieux ;
- le joueur est deplace automatiquement quand `world_updates.new_location` est applique ;
- les PNJ peuvent etre deplaces via `world_updates.character_movements` ;
- les PNJ hors scene peuvent etre deplaces par leur `schedule` ;
- les PNJ presents dans la scene active sont proteges du schedule pendant le tour.

## event_log

`event_log` conserve les evenements importants valides.

```json
{
  "day": 1,
  "date": "2026-09-01",
  "time": "10:15",
  "type": "arrival",
  "participants": ["elina"],
  "summary": "Elina arrive sur le campus."
}
```

Le journal est sauvegarde dans le world runtime et les derniers evenements sont reinjectes dans le prompt.

## planned_events

`planned_events` conserve les rendez-vous ou intentions concretes a venir.
Ils peuvent venir d'un SMS, d'une conversation a voix haute ou d'un autre moteur futur.

```json
{
  "id": "planned_skating_lesson_dean_elina_day2_0700",
  "type": "planned_event",
  "trigger": "skating_lesson_planned_meeting",
  "status": "scheduled",
  "participants": ["dean", "elina"],
  "location": "ice_rink",
  "day": 2,
  "time": "07:00",
  "summary": "Dean and Elina agreed to meet at the rink for a skating lesson.",
  "source": "sms"
}
```

Regles actuelles :

- les planned events sont stockes dans le world runtime ;
- `id` sert a eviter les doublons ;
- `status` vaut actuellement `scheduled` pour les evenements a venir ;
- `source` indique le canal qui a cree l'evenement, par exemple `sms` ou `scene` ;
- le prompt reinjecte les planned events pour que le LLM tienne compte des promesses deja posees ;
- le MVP detecte le rendez-vous patinoire Dean/Elina depuis un SMS confirme ou une scene parlee claire.

## arc_state

`arc_state` conserve ce que la partie a deja observe pour les arcs narratifs.
Il ne remplace pas `scenario.story_arcs` : le scenario definit la boussole, le runtime note les signaux deja joues.

```json
{
  "dean_elina_slow_burn": {
    "phase": "initial_tension",
    "played_beats": ["playful_challenge", "text_followup"],
    "signals": ["playful_challenge_seen", "text_followup_seen"],
    "last_updated_day": 1
  }
}
```

Regles actuelles :

- `arc_state` vit dans le world runtime ;
- les signaux sont deduits de scenes, evenements, souvenirs et SMS ;
- les signaux ne sont pas dupliques ;
- les beats joues aident le LLM a eviter les repetitions ;
- l'etat observe ne force pas le prochain beat ;
- `phase` reste pour l'instant initialisee depuis le scenario, sans progression automatique.

## messages

`messages` conserve les SMS hors scene generes par le moteur.

```json
{
  "id": "dean-elina-skating_lesson_followup-d1-1035",
  "from": "dean",
  "to": "elina",
  "channel": "sms",
  "content": "Demain matin. Patinoire. 7h.",
  "sent_at_day": 1,
  "sent_at_time": "10:35",
  "status": "unread",
  "trigger": "skating_lesson_followup"
}
```

Regles actuelles :

- les messages sont stockes dans le world runtime ;
- `trigger` sert a eviter les doublons narratifs ;
- `status` vaut actuellement `unread` ou `read` ;
- le CLI peut afficher les messages du joueur et les marquer comme lus ;
- le CLI peut envoyer une reponse avec `reply dean: texte` ;
- une reponse SMS joueur est stockee avec `status: sent` et ajoute un evenement `text_message` dans `event_log` ;
- certains SMS peuvent ajouter un evenement narratif supplementaire dans `event_log` et un `planned_event` durable quand un rendez-vous est confirme ;
- une reponse PNJ peut creer un souvenir simple chez le PNJ qui repond ;
- certains PNJ peuvent generer une reponse anti-spam, par exemple Dean qui confirme le rendez-vous patinoire ;
- le contenu de cette reponse utilise un fallback deterministe par defaut, ou un texte LLM optionnel si `INK_FATE_ENABLE_LLM_SMS=1` ;
- avec `INK_FATE_ENABLE_LLM_SMS=1`, un PNJ contactable peut aussi generer une reponse SMS LLM generique a un SMS joueur significatif ;
- avec `INK_FATE_ENABLE_LLM_SMS=1`, les SMS PNJ inities par `message_triggers` peuvent aussi etre reformules par le LLM avec fallback deterministe ;
- les reponses generiques utilisent des triggers commencant par `generic_sms_reply_` pour eviter les doublons.

## runtime_directives

`runtime_directives` stocke les consignes HRP ajoutees pendant une partie.

```json
{
  "type": "rule",
  "content": "Dean doit rester plus subtil.",
  "scope": "session"
}
```

Regles actuelles :

- les commandes `/hrp`, `/rule` et `/context` ajoutent des directives ;
- elles sont sauvegardees dans le world runtime ;
- elles sont reinjectees dans le prompt ;
- elles ne modifient pas `scenario.json` ;
- elles ne peuvent pas annuler les contraintes du moteur, par exemple ne jamais faire parler le personnage joueur.

## 📖 scenario.json

`scenario.json` decrit le point de depart narratif.

```json
{
  "title": "Arrival at Briar",
  "premise": "Elina Maxwell arrives at Briar University.",
  "initial_state": {},
  "initial_tensions": []
}
```

Champs :

- `title` : nom du scenario.
- `premise` : situation initiale.
- `initial_state` : ce que les personnages savent deja.
- `initial_tensions` : tensions narratives de depart.

Le prompt builder lit `scenario.json` pour injecter les regles de ton, de canon, de dynamique personnages, de pacing et les triggers de messages.

Champ courant supplementaire :

- `story_arcs` : arcs narratifs actifs servant de boussole dramatique souple.
- `message_triggers` : configuration de messages hors scene, par exemple le SMS de suivi patinoire Dean -> Elina ou le check-in de Beau apres un depart au dortoir.

### story_arcs

Les arcs narratifs indiquent les tensions persistantes d'un scenario.
Ils ne sont pas une checklist obligatoire et ne forcent pas l'issue.

```json
{
  "id": "dean_elina_slow_burn",
  "title": "Dean and Elina slow-burn tension",
  "status": "active",
  "phase": "initial_tension",
  "participants": ["dean", "elina", "beau"],
  "dramatic_questions": [],
  "current_tensions": [],
  "available_beats": [],
  "blocked_beats": [],
  "progress_signals": [],
  "branching_notes": []
}
```

Regles actuelles :

- seuls les arcs `active` sont reinjectes dans le prompt ;
- `available_beats` propose des opportunites, pas des obligations ;
- `blocked_beats` aide a eviter les raccourcis comme une confession ou un couple officiel trop tot ;
- `progress_signals` indique ce qui peut justifier une progression future ;
- `branching_notes` explique comment gerer les refus, retards ou bifurcations du joueur ;
- le MVP ne modifie pas encore automatiquement `phase` ou `status` pendant la partie.

Exemple :

```json
{
  "trigger": "beau_dormitory_checkin",
  "from": "beau",
  "to": "elina",
  "channel": "sms",
  "content": "T'es bien arrivee au dortoir ?",
  "keywords": ["dortoir", "dormitory", "installee"]
}
```

Regles actuelles :

- le destinataire doit etre le personnage joueur ;
- `from` et `to` doivent exister dans les personnages charges ;
- le PNJ expediteur doit connaitre un contact SMS vers le joueur ;
- le PNJ et le joueur doivent etre a des lieux differents ;
- le contexte recent doit contenir au moins un des `keywords` ;
- `trigger` sert a eviter les doublons ;
- `content` sert de fallback deterministe si le LLM SMS optionnel est desactive ou indisponible.

## 👤 character.json

Un personnage represente une entite narrative autonome.

Structure actuelle :

```json
{
  "id": "dean",
  "identity": {},
  "personality": {},
  "archetype": "charmer",
  "goals": [],
  "fears": [],
  "desires": [],
  "relationships": {},
  "contacts": {},
  "current_goals": [],
  "private_thoughts": [],
  "schedule": []
}
```

Champs :

- `id` : identifiant stable du personnage.
- `identity` : nom, age et informations publiques.
- `personality` : traits numeriques ou qualitatifs.
- `archetype` : role narratif general.
- `goals` : objectifs longs.
- `fears` : peurs importantes.
- `desires` : envies profondes.
- `relationships` : relations asymetriques vers les autres personnages.
- `contacts` : acces de communication asymetriques vers les autres personnages.
- `current_goals` : objectifs actifs dans la scene ou la journee.
- `private_thoughts` : informations internes a utiliser avec prudence.
- `schedule` : planning simple du personnage.
- `speech_style` : maniere stable de parler.
- `behavior_rules` : regles comportementales stables et reutilisables.

Champ courant :

- `memories` : souvenirs persistants.

## schedule

Un planning indique ou un personnage devrait etre a partir d'une heure donnee.

```json
{
  "time": "11:00",
  "location": "hockey_house",
  "activity": "hanging out at the hockey house"
}
```

Regles actuelles :

- `time` est au format `HH:MM` ;
- `location` doit etre un lieu connu ;
- `activity` sert a resumer le mouvement dans `event_log` ;
- le schedule ne deplace pas automatiquement le personnage joueur ;
- un PNJ deplace narrativement pendant le tour n'est pas aussitot ecrase par son schedule ;
- un PNJ present dans la scene active n'est pas deplace automatiquement par son schedule pendant ce tour ;
- un PNJ hors scene peut continuer a bouger selon son schedule.

## 💞 relationship

Une relation est stockee du point de vue d'un personnage vers un autre.

```json
{
  "friendship": 20,
  "trust": 10,
  "respect": 15,
  "attachment": 0,
  "jealousy": 0,
  "attraction": 30
}
```

Regles actuelles :

- les relations sont asymetriques ;
- les valeurs sont entre `0` et `100` ;
- les updates du LLM sont des deltas ;
- les personnages runtime sont sauvegardes apres application des updates ;
- les personnages canon dans `data/universes` restent propres pendant une partie.

## contacts

Les contacts indiquent si un personnage peut joindre un autre personnage hors scene.
Ils sont stockes separement des relations emotionnelles.

```json
{
  "phone_number_known": false,
  "phone_numbers_exchanged": false,
  "instagram_connected": false
}
```

Champs :

- `phone_number_known` : le personnage source connait le numero du personnage cible. Ce champ est asymetrique et permet de representer un numero obtenu par un tiers.
- `phone_numbers_exchanged` : les deux personnages ont explicitement echange leurs numeros. Le moteur le duplique dans les deux sens.
- `instagram_connected` : les deux personnages sont connectes sur Instagram dans le MVP. Le moteur le duplique dans les deux sens.

Regles actuelles :

- `source.contacts[target].phone_number_known = true` permet a `source` d'envoyer un texto ou d'appeler `target` ;
- `phone_numbers_exchanged = true` implique aussi `phone_number_known = true` dans les deux sens ;
- `instagram_connected = true` permet les DM Instagram dans les deux sens ;
- ces champs ne representent pas l'affection, seulement les moyens de contact disponibles.

## 🧠 memory

Les souvenirs sont sauvegardes dans les fichiers personnages runtime.

Structure actuelle simplifiee :

```json
{
  "owner": "dean",
  "content": "Elina seemed confident.",
  "type": "memory",
  "importance": 5,
  "age": 0,
  "tags": ["elina", "first_meeting"]
}
```

## 🧠 Regle Generale

Les JSON runtime representent la verite de la partie en cours.

Le LLM peut proposer des changements, mais seul le moteur applique les donnees apres validation.
