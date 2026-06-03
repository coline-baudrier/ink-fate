# World Simulation Engine

## Rôle

Le moteur de simulation sociale décide ce qui se passe lorsque le joueur n'est pas directement impliqué dans une scène.

Par exemple :

```
Elina va dormir.
Elina part en cours.
Elina passe l’après-midi à la bibliothèque.
Elina laisse passer trois jours.
```

Pendant ce temps les autres personnages continuent d'exister.

---

## Principe central

Le monde ne doit pas attendre le joueur.

Les personnages peuvent :

- parler entre eux ;
- envoyer des messages ;
- organiser des évènements ;
- se disputer ;
- cacher des informations ;
- développer des sentiments ;
- éviter quelqu'un ;
- prendre une décision importante.

---

## Boucle de simulation

Quand le temps avance, le moteur fait :

1. Lire l’état actuel du monde
2. Identifier les personnages disponibles
3. Lire leurs objectifs, émotions et relations
4. Générer des événements plausibles
5. Enregistrer les événements
6. Créer les souvenirs associés
7. Mettre à jour les relations
8. Avancer l’horloge du monde

---

# Exemple

Elina va dormir à 23h. Le moteur simule la nuit :

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

---

## Types d'évènements hors champ

### Conversation

Deux ou plusieurs personnages discutent :

```json
  "type": "conversation",
  "participants": ["dean", "beau"],
  "summary": "Beau warned Dean about Elina."
```

### Text Message

Un personnage envoie un message :

```json
  "type": "text_message",
  "sender": "dean",
  "receiver": "garrett",
  "content": "Did Beau ever mention he had a sister?"
```

### Private reflection

Un personnage pense à quelque chose :

```json
  "type": "social_plan",
  "organizer": "beau",
  "summary": "Beau plans to introduce Elina to a few friends."
```

### Conflict

Une tension apparaît ou augmente :

```json
  "type": "conflict",
  "participants": ["beau", "dean"],
  "summary": "Beau dislikes how Dean joked about Elina."
```

---

# Règle importante

Tous les évènements hors champ ne doivent pas être immédiatement révélés au joueur, certains évènements restent secrets :

```json
{
  "visibility": "hidden"
}
```

ou visibles plus tard :

```json
{
  "visibility": "discoverable"
}
```

---

## Visibilité des évènements

- visible → le joueur l’apprend immédiatement
- discoverable → le joueur peut l’apprendre plus tard
- hidden → uniquement connu des personnages concernés

--

# Exemple concret

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
