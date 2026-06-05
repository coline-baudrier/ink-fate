# Frontend Ink & Fate

Interface React/Vite du prototype.

## Fonctionnalites

- reprise ou creation de la sauvegarde runtime `default` ;
- affichage du fil narratif ;
- envoi d'actions avec streaming SSE ;
- syntaxe visuelle pour actions, dialogues, intentions et textos ;
- affichage de la date et de l'heure du monde ;
- panneau de conversations SMS ;
- remise a zero de la partie.

## Developpement

L'API FastAPI doit tourner sur `http://localhost:8000`.
Vite proxifie les requetes `/game` vers cette adresse.

Depuis ce dossier :

```powershell
npm install
npm run dev
```

Ou depuis la racine du depot :

```powershell
.\start.ps1
```

## Verification

```powershell
npm run lint
npm run build
```

## API utilisee

- `POST /game/start`
- `POST /game/action`
- `POST /game/action/stream`
- `GET /game/messages`
- `POST /game/sms`
- `POST /game/reset`

Limites actuelles : univers `off-campus` fixe, sauvegarde `default`, pas d'authentification.
