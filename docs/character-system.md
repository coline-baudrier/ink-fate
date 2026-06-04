# 👤 Character System

Le character system decrit comment un personnage est represente dans Ink & Fate.

Un personnage n'est pas seulement un nom. C'est une entite narrative avec une personnalite, des objectifs, des relations et une memoire.

## 🗂️ Structure

Structure cible :

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
  "speech_style": [],
  "behavior_rules": [],
  "private_thoughts": [],
  "schedule": [],
  "memories": []
}
```

## 🪪 identity

Informations publiques du personnage.

```json
{
  "first_name": "Dean",
  "last_name": "Di Laurentis",
  "age": 22
}
```

Regles :

- `id` doit rester stable ;
- le nom peut etre affiche au joueur ;
- l'identite ne doit pas contenir les secrets internes du personnage.

## ✨ personality

Traits qui guident le comportement.

```json
{
  "humor": 95,
  "charisma": 95,
  "loyalty": 90,
  "impulsiveness": 70
}
```

Les valeurs numeriques donnent une direction au LLM et au moteur, mais elles ne doivent pas produire des comportements mecaniques.

## 🎭 archetype

Role narratif general.

Exemples :

- `newcomer` ;
- `charmer` ;
- `protective_brother`.

L'archetype aide a comprendre rapidement la fonction dramatique du personnage, mais il ne doit pas remplacer la personnalite.

## 🎯 goals

Objectifs longs du personnage.

```json
["enjoy_college_life", "maintain_friendships"]
```

Ces objectifs influencent les decisions sur plusieurs scenes.

## 📍 current_goals

Objectifs actifs maintenant.

```json
["tease_beau"]
```

Ils sont plus utiles au prompt que les objectifs longs pour generer une scene precise.

## 😟 fears

Peurs profondes.

```json
["emotional_commitment"]
```

Elles doivent influencer les reactions, surtout dans les scenes emotionnelles.

## 💭 desires

Envies ou besoins profonds.

```json
["freedom", "belonging", "love"]
```

Les desirs peuvent entrer en conflit avec les peurs.

## 💞 relationships

Relations asymetriques vers d'autres personnages.

Voir [relationship-system.md](relationship-system.md).

## contacts

Moyens de contact asymetriques vers d'autres personnages.

Ils indiquent si un personnage peut appeler, envoyer un SMS ou DM un autre personnage hors scene.

## speech_style

Style de parole stable du personnage.

Exemples :

- `confident, teasing and direct` ;
- `protective but not humorless`.

## behavior_rules

Regles comportementales stables et reutilisables.

Elles ne doivent pas dependre d'un scenario precis. Les dynamiques specifiques, comme "Elina est la petite soeur de Beau", restent dans `scenario.json`.

## schedule

Planning simple utilise par le moteur pour deplacer les PNJ hors scene.

## 🔒 private_thoughts

Informations internes au personnage.

Regles :

- elles peuvent aider le LLM a comprendre une intention ;
- elles ne doivent pas etre revelees directement au joueur sans scene appropriee ;
- elles ne sont pas forcement des faits objectifs.

## 🧠 memories

Souvenirs persistants du personnage.

Voir [memory-system.md](memory-system.md).

## 🎮 MVP

Pour le MVP, un personnage doit au minimum avoir :

- `id` ;
- `identity` ;
- `personality` ;
- `goals` ;
- `current_goals` ;
- `relationships` ;
- `contacts`.

La memoire peut etre ajoutee progressivement.

## 🛡️ Regles

- Un personnage doit agir selon ses donnees.
- Un personnage peut mentir, eviter, hesiter ou mal comprendre.
- Un personnage ne doit pas changer brutalement sans evenement credible.
- Les donnees internes ne doivent pas etre exposees directement au joueur.
