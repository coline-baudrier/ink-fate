# Relationship System

Le relationship system suit ce qu'un personnage ressent envers un autre.

Les relations sont asymetriques et multidimensionnelles.

## Dimensions

Structure cible :

```json
{
  "attraction": 0,
  "trust": 0,
  "respect": 0,
  "attachment": 0,
  "friendship": 0,
  "jealousy": 0
}
```

## Definitions

- `attraction` : est-ce que cette personne me plait ?
- `trust` : est-ce que je lui fais confiance ?
- `respect` : est-ce que je la considere ?
- `attachment` : est-ce qu'elle me manquerait ?
- `friendship` : est-ce que j'aime passer du temps avec elle ?
- `jealousy` : est-ce que ses interactions avec les autres m'affectent ?

## Asymetrie

Une relation est stockee du point de vue d'un personnage.

Exemple :

```json
{
  "dean": {
    "relationships": {
      "elina": {
        "attraction": 70,
        "trust": 20
      }
    }
  },
  "elina": {
    "relationships": {
      "dean": {
        "attraction": 25,
        "trust": 10
      }
    }
  }
}
```

Dean peut etre tres attire par Elina sans que l'inverse soit vrai.

## Valeurs

Pour le MVP, chaque dimension devrait rester entre `0` et `100`.

Interpretation indicative :

- `0` : absent ou nul ;
- `25` : faible ;
- `50` : notable ;
- `75` : fort ;
- `100` : maximum.

## Updates

Le LLM propose des deltas.

```json
{
  "source": "dean",
  "target": "elina",
  "changes": {
    "attraction": 10,
    "respect": 5
  }
}
```

Le moteur applique seulement apres validation.

Regles :

- les updates sont des deltas ;
- les valeurs finales sont limitees entre 0 et 100 ;
- les deltas trop grands sont refuses ou limites ;
- une update doit etre justifiee par la scene.

## Limites MVP

Pour eviter les changements trop brutaux :

```md
delta normal : -10 a +10
delta fort : -20 a +20, seulement pour evenement important
delta extreme : refuse par defaut
```

Exemple a refuser ou limiter :

```json
{
  "changes": {
    "attraction": 200
  }
}
```

## Exemples

Premiere rencontre :

```json
{
  "target_id": "elina",
  "attraction": 20,
  "trust": 0,
  "respect": 10,
  "attachment": 0,
  "friendship": 0,
  "jealousy": 0
}
```

Quelques semaines plus tard :

```json
{
  "target_id": "elina",
  "attraction": 70,
  "trust": 60,
  "respect": 75,
  "attachment": 55,
  "friendship": 80,
  "jealousy": 20
}
```

## Regles Narratives

- Une romance ne doit pas etre forcee.
- La confiance monte lentement.
- L'attraction peut monter plus vite que l'attachement.
- Le respect peut exister meme dans un conflit.
- La jalousie ne signifie pas automatiquement amour.
- Les relations doivent evoluer grace aux scenes et aux souvenirs.
