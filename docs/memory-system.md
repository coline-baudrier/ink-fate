# 🧠 Memory System

La memoire permet aux personnages de garder une trace subjective de ce qui arrive.

Un souvenir n'est pas seulement un evenement objectif. C'est ce qu'un personnage retient ou ressent a propos d'un moment.

## 📍 Etat Actuel

La memoire existe en version MVP.

Le moteur peut :

- demander des `memory_updates` au LLM ;
- verifier que le proprietaire du souvenir existe ;
- verifier que le contenu est une chaine non vide ;
- limiter l'importance entre `1` et `10` ;
- ajouter les souvenirs au personnage concerne ;
- sauvegarder les souvenirs dans les fichiers personnages ;
- selectionner les souvenirs pertinents selon importance, age, tags et contexte ;
- reinjecter les souvenirs selectionnes dans le prompt ;
- augmenter l'age des souvenirs.

## 🗂️ Structure Actuelle

```json
{
  "owner": "dean",
  "type": "memory",
  "content": "Elina challenged Dean with confidence.",
  "importance": 5,
  "age": 0,
  "tags": ["elina", "challenge"]
}
```

Champs :

- `owner` : id du personnage qui possede le souvenir.
- `type` : type libre pour l'instant.
- `content` : souvenir subjectif.
- `importance` : entier entre `1` et `10`.
- `age` : age du souvenir.
- `tags` : mots cles optionnels.

## 🔁 Flux Actuel

```md
SceneResult
-> remove_invalid_memory_updates
-> clamp_memory_importance
-> apply_memory_updates
-> increase_memory_age
-> save_characters
```

## 🧵 Recuperation Dans Le Prompt

`prompt_builder.py` passe par `memory_retriever.py` pour choisir les souvenirs utiles.

Le score d'un souvenir prend en compte :

- son importance ;
- son age ;
- ses tags ;
- les mots presents dans l'action du joueur ;
- les mots presents dans l'historique de scene.

Les souvenirs retenus sont ajoutes dans :

```md
RELEVANT MEMORIES
```

Cela aide le LLM a rester coherent sur plusieurs tours.

## 🚧 Limites Actuelles

- Les doublons ne sont pas encore detectes.
- La recuperation reste simple et locale aux participants actifs.
- Les types de souvenirs ne sont pas encore stricts.
- Il n'y a pas encore d'id unique de souvenir.

## 🔮 Direction Future

Plus tard, le moteur pourra :

- creer des souvenirs avec un id stable ;
- distinguer `core`, `episodic`, `emotional`, `secret` ;
- eviter les doublons ;
- ameliorer le scoring selon les relations, les lieux et les evenements ;
- reduire l'importance des vieux souvenirs ;
- proteger les secrets.
