# 🌙 World Simulation Engine

Le world simulation engine gere ce qui se passe lorsque le joueur n'est pas directement implique dans une scene.

Cette fonctionnalite est importante pour la vision finale, mais elle doit rester limitee dans le MVP. Aujourd'hui, Ink & Fate a deja un Message Engine MVP deterministe ; la simulation hors champ avancee reste future.

## 🎭 Role

Le monde ne doit pas attendre le joueur.

Quand le joueur laisse passer du temps, les personnages peuvent :

- parler entre eux ;
- envoyer des messages ;
- organiser un evenement ;
- se disputer ;
- cacher une information ;
- developper un sentiment ;
- eviter quelqu'un ;
- prendre une decision importante.

## ⚡ Declencheurs

La simulation hors champ se declenche quand le joueur indique une ellipse.

Exemples :

```md
Je vais dormir.
Je passe l'apres-midi en cours.
Je rentre au dortoir.
Je laisse passer deux jours.
```

Pour le MVP, il ne doit pas y avoir de simulation permanente. La simulation se produit seulement sur ellipse explicite.

Note actuelle : le Message Engine peut aussi generer un SMS hors scene sans ellipse longue, quand une opportunite narrative claire existe deja.

## 🔁 Boucle Cible

```md
1. Lire l'etat actuel du monde.
2. Detecter une ellipse.
3. Identifier la duree.
4. Identifier les personnages disponibles.
5. Lire leurs objectifs, relations et souvenirs.
6. Generer des evenements plausibles.
7. Creer les souvenirs associes.
8. Mettre a jour les relations.
9. Avancer l'horloge du monde.
10. Sauvegarder le nouvel etat.
```

## 🧪 Exemple

Elina va dormir a 23h.

Le moteur simule la nuit :

```json
{
  "time_skip": {
    "from": "2026-09-01 23:00",
    "to": "2026-09-02 08:00"
  },
  "offscreen_events": [
    {
      "type": "conversation",
      "participants": ["dean", "beau"],
      "summary": "Beau warned Dean not to mess with Elina."
    },
    {
      "type": "private_reflection",
      "participants": ["dean"],
      "summary": "Dean found Beau's warning amusing and thought about Elina."
    }
  ]
}
```

## 📌 Types D'Evenements Hors Champ

### conversation

Deux ou plusieurs personnages discutent.

```json
{
  "type": "conversation",
  "participants": ["dean", "beau"],
  "summary": "Beau warned Dean about Elina."
}
```

### text_message

Un personnage envoie un message.

```json
{
  "type": "text_message",
  "sender": "dean",
  "receiver": "garrett",
  "content": "Did Beau ever mention he had a sister?"
}
```

Dans le backend actuel, les messages sont stockes dans `world.messages` avec un format plus proche de :

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

### private_reflection

Un personnage reflechit seul.

```json
{
  "type": "private_reflection",
  "participants": ["dean"],
  "summary": "Dean thinks about Elina's arrival."
}
```

### social_plan

Un personnage prepare une action sociale.

```json
{
  "type": "social_plan",
  "organizer": "beau",
  "summary": "Beau plans to introduce Elina to a few friends."
}
```

### conflict

Une tension apparait ou augmente.

```json
{
  "type": "conflict",
  "participants": ["beau", "dean"],
  "summary": "Beau dislikes how Dean joked about Elina."
}
```

## 👁️ Visibilite

Tous les evenements hors champ ne doivent pas etre reveles immediatement au joueur.

```json
{
  "visibility": "discoverable"
}
```

Valeurs :

- `visible` : le joueur l'apprend immediatement ;
- `discoverable` : le joueur peut l'apprendre plus tard ;
- `hidden` : seulement connu des personnages concernes.

## 🧩 Exemple Complet

```json
{
  "id": "event_001",
  "type": "conversation",
  "participants": ["beau", "dean"],
  "date": "2026-09-01",
  "time": "23:45",
  "location": "hockey_house",
  "summary": "Beau told Dean not to flirt with Elina.",
  "visibility": "discoverable",
  "consequences": {
    "relationship_changes": [
      {
        "source": "beau",
        "target": "dean",
        "trust": -2
      },
      {
        "source": "dean",
        "target": "elina",
        "curiosity": 5
      }
    ],
    "new_memories": [
      {
        "owner": "dean",
        "type": "episodic",
        "importance": 45,
        "content": "Beau warned me not to flirt with Elina.",
        "tags": ["beau", "elina", "warning"]
      }
    ]
  }
}
```

## 🎮 MVP

Pour le MVP 1, cette fonctionnalite peut rester minimale :

- generer certains messages hors scene deterministes ;
- generer certaines reponses SMS PNJ avec un fallback deterministe et un texte LLM optionnel ;
- detecter quelques ellipses explicites ;
- avancer l'heure ;
- generer au maximum quelques evenements hors champ ;
- sauvegarder ces evenements ;
- creer des souvenirs simples.

La simulation sociale avancee viendra plus tard. Le joueur peut deja envoyer une reponse SMS hors scene, et Dean peut confirmer le rendez-vous patinoire. Cette confirmation peut garder son texte deterministe ou etre ecrite par le LLM quand l'option SMS LLM est active. Le prochain palier logique est de generaliser les reponses PNJ avec une vraie logique narrative au-dela du cas Dean/patinoire.
