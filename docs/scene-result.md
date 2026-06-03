# SceneResult

Le `SceneResult` est le contrat de sortie du LLM.

Le LLM ne doit pas repondre avec du texte libre. Il doit produire un JSON exploitable par le moteur.

## Philosophie

Le LLM met en scene.

Le moteur decide ce qui devient vrai.

Le `SceneResult` est donc une proposition structuree. Avant application, il doit etre parse, valide, puis transforme en updates autorises.

## Structure Cible MVP

```json
{
  "scene": {
    "location": "",
    "time": "",
    "participants": []
  },
  "narration": [],
  "dialogues": [],
  "actions": [],
  "events": [],
  "world_updates": {},
  "memory_updates": [],
  "relationship_updates": [],
  "next_hooks": []
}
```

## scene

Contexte de la scene generee.

```json
{
  "location": "campus",
  "time": "10:15",
  "participants": ["dean", "beau", "elina"]
}
```

Regles :

- `location` doit exister dans `world.json`.
- `participants` doit contenir uniquement des personnages existants.
- `time` doit rester coherent avec la timeline.

## narration

Fragments narratifs lus par le joueur.

```json
[
  "Dean remarque Elina presque aussitot.",
  "Un sourire amusé traverse son visage."
]
```

Regles :

- la narration peut decrire le monde, les PNJ et les actions visibles du joueur ;
- elle ne doit jamais decrire les pensees, emotions ou decisions internes du joueur ;
- elle doit rester coherente avec le ton de l'univers.

## dialogues

Dialogues separes de la narration.

```json
[
  {
    "speaker": "dean",
    "text": "Alors, c'est toi la fameuse petite soeur de Beau ?"
  }
]
```

Regles :

- `speaker` doit etre un personnage existant ;
- le LLM ne doit pas ecrire de dialogue pour le personnage joueur ;
- le texte doit rester naturel et compatible avec le personnage.

## actions

Actions objectives qui peuvent etre comprises par le moteur.

```json
[
  {
    "character": "dean",
    "type": "notice",
    "target": "elina"
  }
]
```

Regles :

- `character` doit exister ;
- `target` doit etre vide ou correspondre a une entite existante ;
- `type` doit decrire une action objective, pas une emotion.

## events

Evenements importants a enregistrer.

```json
[
  {
    "type": "first_meeting",
    "participants": ["dean", "elina"]
  }
]
```

Regles :

- tous les dialogues ne sont pas des evenements ;
- un evenement doit etre narrativement utile ;
- les participants doivent exister.

## world_updates

Changements proposes sur l'etat du monde.

```json
{
  "time_advanced_minutes": 10,
  "new_scene_state": {
    "location": "campus"
  }
}
```

Regles :

- le moteur peut refuser une avancee de temps trop grande ;
- un changement de lieu doit pointer vers un lieu existant ;
- le LLM ne modifie pas directement `world.json`.

## memory_updates

Souvenirs proposes pour les personnages.

```json
[
  {
    "owner": "dean",
    "type": "episodic",
    "importance": 40,
    "content": "Elina seemed confident during their first meeting.",
    "tags": ["elina", "first_meeting"]
  }
]
```

Regles :

- `owner` doit exister ;
- `importance` doit etre entre 1 et 100 ;
- le contenu doit etre subjectif ;
- les tags doivent aider la recuperation future.

## relationship_updates

Changements relationnels proposes.

```json
[
  {
    "source": "dean",
    "target": "elina",
    "changes": {
      "attraction": 10,
      "respect": 5
    }
  }
]
```

Regles :

- les valeurs sont des deltas, pas des valeurs absolues ;
- `source` et `target` doivent exister ;
- le moteur limite les deltas ;
- une relation reste asymetrique.

Exemple :

```md
attraction: 200
```

doit etre refuse ou limite par le moteur.

## next_hooks

Pistes narratives ouvertes.

```json
[
  "Dean may try to see Elina again later.",
  "Beau noticed Dean's interest."
]
```

Regles :

- un hook n'est pas une verite obligatoire ;
- il sert a guider les generations futures ;
- il ne doit pas forcer une romance ou une decision joueur.

## Validation Minimale

Avant application, le moteur doit verifier :

- JSON valide ;
- champs obligatoires presents ;
- types corrects ;
- personnages existants ;
- lieux existants ;
- pas de dialogue joueur ;
- pas de pensees joueur ;
- deltas relationnels acceptables ;
- souvenirs avec importance valide.
