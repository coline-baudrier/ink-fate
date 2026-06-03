# Relationship System

Chaque relation entre deux personnages possède plusieurs dimensions :

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

- **Attraction** : `Est-ce que cette personne me plaît ?` -> Peut exister sans confiance ;
- **Trust** : `Est-ce que je crois ce qu'il me dit ?` -> Peut être faible même dans une romance ;
- **Respect** : `Est-ce que je la considère ?` -> Très important dans les conflits ;
- **Attachment** : `Est-ce qu'elle me manquerait ?` -> C'est souvent ce qui précède l'amour ;
- **Friendship** : `Est-ce que j'apprecie passer du temps avec elle ?` ;
- **Jealousy** : `Suis-je affecté par ses interactions avec les autres ?` ;

## Exemple concret

- Quand Dean rencontre Elina :

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

- Quelques semaines plus tard :

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

---

# Relations asymétriques

Les relations doivent être asymétriques :

- Dean -> Elina

```json
{
  "attraction": 70
}
```

- Elina -> Dean

```json
{
  "attraction": 25
}
```

Les deux ne ressentent pas forcément la même chose.

Et c'est précisément ce qui crée des histoires intéressantes.

---

# Structure des fichiers

On ne met pas les relations dans un fichier séparé, mais plutôt directement _dans les personnages_ :

```json
{
  "id": "dean",

  "relationships": {
    "beau": {
      "friendship": 95,
      "trust": 90,
      "respect": 85
    },

    "elina": {
      "attraction": 20,
      "trust": 0,
      "respect": 10
    }
  }
}
```
