# Memory System

Les personnages ne se souviennent pas des évènements, mais ils se souviennent de leur interprétation des évènements.

- Evènement objectif :

```json
{
  "type": "first_meeting",
  "participants": ["dean", "elina"]
}
```

- Mémoire de Dean :

```json
{
  "content": "Elina was surprisingly confident."
}
```

- Mémoire d'Elina

```json
{
  "content": "Dean was annoyingly charming."
}
```

On est sur le même évènement mais deux souvenirs différents, ce qui crée des personnages crédibles.

---

# 4 types de mémoire

On va séparer les souvenirs dès le début.

## Core Memory

Ne change presque jamais :

```json
{
  "type": "core",
  "content": "Beau is my brother."
}
```

ou

```json
{
  "type": "core",
  "content": "Dean is Beau's best friend."
}
```

Ce sont ces souvenirs qui vont **définir le personnage**.

## Episodic Memory

Ce sont les évènements vécus :

```json
{
  "type": "episodic",
  "content": "Dean carried my luggage on my first day at Briar."
}
```

C'est-à-dire la majorité des souvenirs.

## Emotionnal Memory

Ce sera très important pour les romances :

```json
{
  "type": "emotional",
  "emotion": "attraction",
  "content": "I felt unusually comfortable around Dean."
}
```

ou

```json
{
  "type": "emotional",
  "emotion": "anger",
  "content": "Dean embarrassed me in front of everyone."
}
```

## Secret Memory

Concerne le personnage uniquement, ce n'est jamais révélé directement.

```json
{
  "type": "secret",
  "content": "I think I'm starting to fall for Elina."
}
```

---

# Importance

Chaque souvenir doit avoir :

```json
{
  "importance": 0
}
```

entre 1 (oubliable) et 100 (marquant).

```json
{
  "importance": 95,
  "content": "First kiss with Elina."
}
```

ou

```json
{
  "importance": 10,
  "content": "Ate lunch with Garrett."
}
```

---

# Tags

```json
{
  "tags": []
}
```

Par exemple :

```json
{
  "tags": ["dean", "romance", "first_meeting"]
}
```

Cela permettra pluys tard de faire des recherches en fonction du personnage et du tag défini dessus.

---

# Décroissance

Un souvenir perd naturellement de son importance :

```
95
↓
90
↓
85
↓
80
```

au fil du temps.

Sauf si :

- on y repense ;
- il est renforcé ;
- il est lié à une émotion forte ;

---

# Récupération contextuelle

Le personnage ne consulte pas toutes ses mémoires, il va seulement consulter :

- sa mémoire active ;

```json
["first_meeting", "last_argument", "last_text_message"]
```

- sa mémoire pertinente : si Dean voit Elina, le moteur cherche les mémoires tagguées elina, romance et attraction ;

Et c'est seulement ça qui sera envoyé au LLM.

Ce qui fait qu'après un temps de jeu énorme où la mémoire peut être constituée de 5000 souvenirs, le prompt en contiendra seulement 10 à 20 de pertinents.
