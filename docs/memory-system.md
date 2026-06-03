# Memory System

La memoire permet aux personnages de rester coherents sur le long terme.

Un personnage ne se souvient pas seulement d'un evenement objectif. Il se souvient de son interpretation personnelle de cet evenement.

## Principe

Evenement objectif :

```json
{
  "type": "first_meeting",
  "participants": ["dean", "elina"]
}
```

Souvenir de Dean :

```json
{
  "owner": "dean",
  "content": "Elina was more confident than I expected."
}
```

Souvenir d'Elina :

```json
{
  "owner": "elina",
  "content": "Dean was annoyingly charming."
}
```

Le meme evenement peut donc produire plusieurs souvenirs differents.

## Structure

Structure cible :

```json
{
  "id": "memory_001",
  "owner": "dean",
  "type": "episodic",
  "importance": 40,
  "content": "Elina seemed confident during their first meeting.",
  "tags": ["elina", "first_meeting"],
  "created_at": "2026-09-01 10:15"
}
```

Champs :

- `id` : identifiant stable.
- `owner` : personnage qui possede le souvenir.
- `type` : categorie du souvenir.
- `importance` : valeur de 1 a 100.
- `content` : interpretation subjective.
- `tags` : aide a la recuperation.
- `created_at` : date de creation.

## Types De Memoire

### Core Memory

Souvenir fondamental qui change rarement.

```json
{
  "type": "core",
  "content": "Beau is my brother."
}
```

### Episodic Memory

Souvenir d'un evenement vecu.

```json
{
  "type": "episodic",
  "content": "Dean carried my luggage on my first day at Briar."
}
```

### Emotional Memory

Souvenir centre sur une emotion.

```json
{
  "type": "emotional",
  "emotion": "attraction",
  "content": "I felt unexpectedly comfortable around Dean."
}
```

### Secret Memory

Souvenir ou pensee qui ne doit pas etre revele directement.

```json
{
  "type": "secret",
  "content": "I think I might be starting to like Elina."
}
```

## Importance

Chaque souvenir a une importance entre `1` et `100`.

Exemples :

```json
{
  "importance": 95,
  "content": "First kiss with Elina."
}
```

```json
{
  "importance": 10,
  "content": "Ate lunch with Garrett."
}
```

## Tags

Les tags permettent de retrouver les souvenirs pertinents.

```json
{
  "tags": ["dean", "romance", "first_meeting"]
}
```

## Recuperation Contextuelle

Le moteur ne doit jamais envoyer toute la memoire d'un personnage au LLM.

Il doit recuperer seulement les souvenirs pertinents selon :

- les personnages presents ;
- les tags ;
- l'importance ;
- la recence ;
- le type de scene ;
- les objectifs actuels.

Pour le MVP, une recuperation simple suffit :

```md
prendre les souvenirs du personnage qui mentionnent un participant de la scene.
```

Plus tard, la recuperation pourra devenir plus avancee.

## Decroissance

Un souvenir peut perdre de l'importance avec le temps.

Exemple :

```md
95 -> 90 -> 85 -> 80
```

Exceptions :

- le personnage y repense ;
- un evenement le renforce ;
- il est lie a une emotion forte ;
- il est lie a une relation importante.

Cette decroissance est une fonctionnalite future, pas obligatoire pour le MVP 1.

## MVP

Pour le MVP 1, le systeme de memoire doit seulement :

- accepter des `memory_updates` dans le `SceneResult` ;
- verifier que le proprietaire existe ;
- verifier que l'importance est entre 1 et 100 ;
- sauvegarder les souvenirs ;
- pouvoir reinjecter quelques souvenirs pertinents dans le prompt.

## Regles

- Un souvenir est subjectif.
- Un evenement est objectif.
- Un secret ne doit pas etre revele directement au joueur.
- Le LLM peut proposer un souvenir, mais le moteur le valide.
