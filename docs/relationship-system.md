# 💞 Relationship System

Le relationship system suit ce qu'un personnage ressent envers un autre.

Les relations sont asymetriques, multidimensionnelles et stockees directement dans les fichiers personnages.

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
-> save_characters
```

Regles actuelles :

- les updates sont des deltas ;
- les deltas non entiers sont ignores ;
- les deltas sont limites entre `-5` et `5` ;
- `source` et `target` doivent etre des personnages existants ;
- la relation `source -> target` doit deja exister ;
- la valeur finale est limitee entre `0` et `100` ;
- les personnages modifies sont sauvegardes en JSON.

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
- Les changements sont sauvegardes directement dans les fichiers personnages.
- Il n'y a pas encore de sauvegarde de partie separee.

## ✨ Regles Narratives

- Une romance ne doit pas etre forcee.
- La confiance monte lentement.
- L'attraction peut monter plus vite que l'attachement.
- Le respect peut exister meme dans un conflit.
- La jalousie ne signifie pas automatiquement amour.
- Les relations doivent evoluer grace aux scenes, aux choix du joueur et aux souvenirs futurs.
