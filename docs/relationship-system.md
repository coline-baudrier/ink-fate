# 💞 Relationship System

Le relationship system suit ce qu'un personnage ressent envers un autre.

Les relations sont asymetriques, multidimensionnelles et stockees dans les fichiers personnages. Pendant une partie, les changements sont ecrits dans les personnages runtime de `data/saves`, pas dans les personnages canon.

## 📐 Dimensions

Structure actuelle :

```json
{
  "friendship": 0,
  "trust": 0,
  "respect": 0,
  "attachment": 0,
  "jealousy": 0,
  "attraction": 0
}
```

## 📖 Definitions

- `attraction` : est-ce que cette personne me plait ?
- `trust` : est-ce que je lui fais confiance ?
- `respect` : est-ce que je la considere ?
- `attachment` : est-ce qu'elle me manquerait ?
- `friendship` : est-ce que j'aime passer du temps avec elle ?
- `jealousy` : est-ce que ses interactions avec les autres m'affectent ?

## ↔️ Asymetrie

Une relation est stockee du point de vue d'un personnage.

Exemple :

```json
{
  "dean": {
    "relationships": {
      "elina": {
        "attraction": 10,
        "trust": 0
      }
    }
  },
  "elina": {
    "relationships": {
      "dean": {
        "attraction": 2,
        "trust": 0
      }
    }
  }
}
```

Dean peut etre attire par Elina sans que l'inverse soit vrai.

## 🔢 Valeurs

Chaque dimension doit rester entre `0` et `100`.

Interpretation indicative :

- `0` : absent ou nul ;
- `25` : faible ;
- `50` : notable ;
- `75` : fort ;
- `100` : maximum.

Le module `relationship_stages.py` transforme ces valeurs en paliers narratifs comme `low attraction`, `emerging trust`, `strong respect` ou `trusted`.

Ces paliers sont reinjectes dans le prompt pour aider le LLM a garder une progression romance graduelle.

## 🔁 Updates Actuels

Le LLM propose des deltas dans `relationship_updates`.

```json
{
  "source": "dean",
  "target": "elina",
  "changes": {
    "attraction": 3,
    "respect": 1
  }
}
```

Le moteur applique ce flux :

```md
SceneResult
-> remove_invalid_relationship_updates
-> clamp_relationship_updates
-> apply_relationship_updates
-> save_runtime_state
```

Regles actuelles :

- les updates sont des deltas ;
- les deltas non entiers sont ignores ;
- les deltas sont limites selon la dimension ;
- `source` et `target` doivent etre des personnages existants ;
- la relation `source -> target` doit deja exister ;
- la valeur finale est limitee entre `0` et `100` ;
- les personnages modifies sont sauvegardes en JSON runtime.

Limites de deltas actuelles :

```md
attraction: -2 a +2
respect: -3 a +3
friendship: -2 a +2
trust: -1 a +2
attachment: -1 a +1
jealousy: -2 a +2
autre dimension: -2 a +2
```

## 🧪 Exemple

Etat initial :

```json
{
  "attraction": 0,
  "respect": 0
}
```

Update valide :

```json
{
  "changes": {
    "attraction": 3,
    "respect": 1
  }
}
```

Etat apres application :

```json
{
  "attraction": 3,
  "respect": 1
}
```

## 🚧 Limites Actuelles

- Le moteur ne cree pas encore une relation manquante.
- Le moteur n'affiche pas encore un resume joli des changements.
- Les changements sont sauvegardes dans la sauvegarde runtime.
- Les reponses SMS ne produisent pas encore de changements relationnels dedies.

## ✨ Regles Narratives

- Une romance ne doit pas etre forcee.
- La confiance monte lentement.
- L'attraction peut monter plus vite que l'attachement.
- Le respect peut exister meme dans un conflit.
- La jalousie ne signifie pas automatiquement amour.
- Les relations doivent evoluer grace aux scenes, aux choix du joueur et aux souvenirs futurs.
