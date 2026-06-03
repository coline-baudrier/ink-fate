# ✨ Vision

Ink & Fate est une application personnelle de roman interactif IA.

Le joueur ne discute pas avec un chatbot. Il vit une histoire dans un monde narratif ou les personnages existent avec leur propre personnalite, leurs objectifs, leurs peurs, leurs relations et leurs souvenirs.

## 🎮 Experience Cible

L'utilisateur ouvre l'application et choisit :

- un univers ;
- son personnage ;
- un scenario de depart.

Exemple :

```md
Univers : Off Campus
Personnage : Elina Maxwell
Contexte : petite soeur de Beau Maxwell, arrive a Briar University pour la rentree.
```

Le moteur genere ensuite une premiere scene, puis le joueur peut :

- parler ;
- agir ;
- ignorer quelqu'un ;
- quitter une scene ;
- envoyer un texto ;
- dormir ;
- laisser passer plusieurs heures ou plusieurs jours.

## 🧠 Philosophie

Le moteur ne suit pas un scenario impose.

Il simule :

- des personnages ;
- des relations ;
- des emotions ;
- des objectifs ;
- des souvenirs ;
- des evenements.

La romance, l'amitie, la rivalite ou le conflit ne sont pas garantis. Ils doivent emerger naturellement des interactions.

Par exemple :

- Dean peut tomber amoureux d'Elina ;
- Elina peut ne pas etre interessee ;
- Beau peut creer une tension involontaire ;
- une amitie peut devenir plus importante que la romance ;
- un evenement hors champ peut changer la dynamique.

## 🌍 Monde Vivant

Le monde ne doit pas attendre le joueur.

Quand le joueur dort, part en cours ou laisse passer du temps, les autres personnages peuvent continuer a agir :

- discuter entre eux ;
- prendre des decisions ;
- se disputer ;
- cacher une information ;
- developper un sentiment ;
- organiser un evenement.

Ces evenements peuvent etre visibles, decouvrables plus tard, ou rester caches.

## 👥 Personnages Autonomes

Chaque personnage doit posseder :

- une identite ;
- une personnalite ;
- des objectifs ;
- des peurs ;
- des desirs ;
- des relations ;
- des souvenirs ;
- un etat emotionnel.

Le moteur doit s'appuyer sur ces donnees pour garder des comportements coherents sur le long terme.

## 💞 Relations Dynamiques

Les relations ne sont pas binaires.

Le moteur ne stocke pas seulement :

```md
amoureux : oui / non
```

Il suit plusieurs dimensions :

- attraction ;
- confiance ;
- respect ;
- attachement ;
- amitie ;
- jalousie.

Ces dimensions evoluent progressivement selon les scenes, les evenements et les souvenirs.

## 🗂️ Univers Independants

Le moteur doit etre separe de l'univers.

Un univers est defini par des donnees :

- personnages ;
- lieux ;
- contexte ;
- regles narratives ;
- scenario de depart.

Ainsi, le meme moteur pourra fonctionner avec un univers original, une romance universitaire, de la fantasy ou de la science-fiction.

## 🚀 MVP Et Vision Future

Le MVP 1 reste volontairement simple :

- pas de frontend ;
- pas de FastAPI ;
- pas de base SQLite ;
- stockage JSON local ;
- interface CLI ;
- un seul univers ;
- une seule scene active ;
- trois personnages.

La vision finale est un systeme capable de generer des histoires longues, sur plusieurs semaines ou mois, ou les personnages restent coherents et ou les relations evoluent naturellement.
