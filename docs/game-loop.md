# Game Loop

La game loop définit ce qui se passe à chaque interaction entre le joueur et Ink & Fate. Elle transforme une action du joueur en :

- scène narrative ;
- évènements ;
- souvenirs ;
- changements relationnels ;
- mise à jour du monde.

La boucle principale :

1. Charger le WorldState
2. Lire la scène active
3. Lire l’action du joueur
4. Récupérer les personnages concernés
5. Récupérer les souvenirs pertinents
6. Construire le prompt
7. Envoyer au LLM
8. Recevoir un SceneResult
9. Valider le JSON
10. Appliquer les mises à jour
11. Sauvegarder le nouvel état du monde
12. Afficher la scène au joueur

---

## Entrée du joueur

Il peut écrire librement :

```
"Je souris à Dean."
```

```
*Je récupère ma valise et je lève les yeux au ciel.*
```

```
-- Dean, tu es où ?
```

Le moteur pourra interpréter la syntaxe :

- "..." → parole
- _..._ → action
- -- ... → texto
- texte libre → intention narrative

## Traitement normal

```
PlayerInput
↓
PromptBuilder
↓
LLM
↓
SceneResult
↓
WorldUpdateEngine
↓
Renderer
```

## Traitement des ellipses

Certaines entrées déclenchent une simulation hors champ. Par exemple :

```
Je vais dormir.
Je passe l’après-midi en cours.
Je laisse passer deux jours.
```

Dans ce cas :

```
PlayerInput
↓
TimeSkipDetector
↓
WorldSimulationEngine
↓
OffscreenEvents
↓
MemoryUpdates
↓
RelationshipUpdates
↓
NewScene
```

---

# Validation du SceneResult

Le moteur ne doit jamais appliqué aveuglément la sortie du LLM. Il doit vérfier :

- JSON valide ;
- champs obligatoires présents ;
- personnages existants ;
- lieux existants ;
- changements relationnels acceptables ;
- évènements cohérents.

---

# Règle importante

Le LLM propose et le moteur dispose.

Le LLM peut proposer :

```json
{
  "relationship_updates": [
    {
      "source": "dean",
      "target": "elina",
      "changes": {
        "attraction": 200
      }
    }
  ]
}
```

Le moteur doit refuser ou limiter : `+ 200 attraction -> refusé ou clampé à +10`.

---

# Sortie vers le joueur

Le Renderer transforme le SceneResult en affichage.

- **Mode roman** :

```
Dean s’approche avec un sourire insolent.

« Alors, c’est toi la fameuse petite sœur de Beau ? »
```

- **Mode dialogue** :

```
Dean :
Alors, c’est toi la fameuse petite sœur de Beau ?
```

- **Mode texto** :

```
[Dean]
Tu es rentrée ?
```

---

# Objectifs de la première boucle jouable

Obtenir ceci :

```
Ink & Fate démarre.
Le moteur charge Off Campus.
Le moteur charge Elina, Beau et Dean.
Le moteur génère la scène d’arrivée.
Le joueur répond.
Le moteur génère la suite.
Les relations et souvenirs sont mis à jour.
```
