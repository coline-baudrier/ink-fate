# World Simulation

Le but n'est pas de décrire tout l'univers, mais suffisamment d'informations pour que le moteur sache :

- où on en est ;
- quand on est ;
- qui existe ;
- quelle est la situation actuelle.

```json
{
  "universe": {
    "id": "",
    "name": ""
  },
  "timeline": {
    "current_date": "",
    "current_time": "",
    "current_day": null
  },
  "player_character": "",
  "locations": [
    {
      "id": "",
      "name": ""
    }
  ],
  "characters": [],
  "active_events": [
    {
      "id": "",
      "title": "",
      "status": ""
    }
  ],
  "active_scene": {
    "location": "",
    "participants": []
  }
}
```

Cette structure pourra facilement évoluer, par exemple :

```json
"current_time": "18:30"
```

ou

```json
"current_day": 14
```

Volontairement, on indique seulement ce qui sert au roman, on ne va donc pas intégrer :

- weather
- economy
- inventory
- quests

---

# Scenario

Le scénario **ne contient pas l'histoire**, il contient seulement :

- la situation de départ ;
- ce que chaque personnage sait ;
- les tensions existantes ;

```json
{
  "title": "",
  "premise": "",
  "initial_state": {
    "beau_knows": [],
    "dean_knows": [],
    "elina_knows": []
  },
  "initial_tensions": [
    {
      "description": ""
    }
  ]
}
```

Cela permet aussi d'avoir plusieurs scénarios possibles :

```
Off Campus/
├── characters/
├── world.json
│
├── scenarios/
│   ├── arrival.json
│   ├── summer_break.json
│   ├── graduation.json
│   └── rival_team.json
```
