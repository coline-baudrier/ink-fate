# Game Loop

La game loop definit ce qui se passe a chaque interaction entre le joueur et Ink & Fate.

Elle transforme une action joueur en :

- scene narrative ;
- dialogues ;
- actions objectives ;
- evenements ;
- souvenirs ;
- changements relationnels ;
- mise a jour du monde.

## Boucle MVP

```md
1. Charger le WorldState.
2. Lire la scene active.
3. Charger les personnages participants.
4. Afficher la scene actuelle.
5. Lire l'action du joueur.
6. Recuperer les souvenirs pertinents.
7. Construire le prompt.
8. Envoyer au LLM.
9. Recevoir un SceneResult.
10. Parser le JSON.
11. Valider le SceneResult.
12. Afficher la scene au joueur.
13. Appliquer les updates autorises.
14. Sauvegarder le nouvel etat du monde.
15. Attendre la prochaine action.
```

## Entree Joueur

Le joueur peut ecrire librement.

Exemples :

```md
Je souris a Dean.
```

```md
Je recupere ma valise et je leve les yeux au ciel.
```

```md
Dean, tu es ou ?
```

Pour le MVP, l'entree peut etre traitee comme une intention narrative simple.

Plus tard, le moteur pourra classer :

- parole ;
- action ;
- texto ;
- intention narrative ;
- ellipse.

## Prompt

Le prompt builder recoit :

- l'etat du monde ;
- la scene active ;
- les personnages presents ;
- les relations utiles ;
- les souvenirs pertinents ;
- l'action joueur ;
- les regles narratives ;
- le format `SceneResult`.

Il doit rappeler que le LLM ne controle jamais le personnage joueur.

## SceneResult

Le LLM doit retourner un JSON.

Le moteur doit ensuite verifier :

- JSON valide ;
- champs obligatoires presents ;
- personnages existants ;
- lieux existants ;
- pas de dialogue joueur ;
- pas de pensees joueur ;
- changements relationnels acceptables ;
- evenements coherents.

Voir [scene-result.md](scene-result.md).

## Application Des Updates

Le LLM propose.

Le moteur dispose.

Exemple de sortie LLM :

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

Le moteur doit refuser ou limiter cette valeur.

Pour le MVP :

```md
attraction +200 -> refuse ou limite
attraction +10 -> acceptable si justifie par la scene
```

## Renderer

Le renderer transforme le `SceneResult` en affichage.

### Mode Roman

```md
Dean s'approche avec un sourire insolent.

Dean :
Alors, c'est toi la fameuse petite soeur de Beau ?
```

### Mode Dialogue

```md
Dean :
Alors, c'est toi la fameuse petite soeur de Beau ?
```

### Mode Texto

```md
[Dean]
Tu es rentree ?
```

Pour le MVP, seul un rendu roman simple est necessaire.

## Ellipses

Certaines entrees peuvent faire avancer le temps.

Exemples :

```md
Je vais dormir.
Je passe l'apres-midi en cours.
Je laisse passer deux jours.
```

Dans ce cas, le flux cible devient :

```md
PlayerInput
-> TimeSkipDetector
-> WorldSimulationEngine
-> OffscreenEvents
-> MemoryUpdates
-> RelationshipUpdates
-> NewScene
```

Pour le MVP, les ellipses peuvent rester tres simples.

## Objectif De La Premiere Boucle Jouable

La premiere boucle doit permettre ceci :

```md
Ink & Fate demarre.
Le moteur charge Off Campus.
Le moteur charge Elina, Beau et Dean.
Le moteur genere la scene d'arrivee.
Le joueur repond.
Le moteur genere la suite.
Les relations et souvenirs sont mis a jour.
Le nouvel etat est sauvegarde.
```
