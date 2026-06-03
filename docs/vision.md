# Projet : Moteur de Roman Interactif IA

## Vision générale

Créer une application personnelle permettant de vivre des histoires interactives au sein d'univers existants (Off-Campus, Harry Potter, ACOTAR, Fourth Wing, etc) ou d'univers originaux.

Le joueur incarne son propre personnage et interagit librement avec un monde peublé de personnages autonomes.

L'objectif n'est pas de discuter avec un chatbot mais de vivre une histoire dont le jouer est le héros.

---

# Expérience recherchée

L'utilisateur ouvre l'application et choisit :

- un univers
- son personnage
- un scénario de départ

Exemple

```md
Univers : Off Campus

Personnage :
Elina Maxwell

Contexte :
Petite soeur de Beau Maxwell
Arrive sur le campus de Briar pour la rentrée
```

Le moteur génère ensuite le premier chapitre :

```md
Campus de Briar

Beau referme le coffre de sa voiture tandis que tu récpuères ta valise.

Quelques mètres plus loin, Dean Di Laurentis s'approche avec son sourire habituel...
```

L'utilisateur peur ensuite :

- parler
- agir
- ignorer quelqu'un
- quitter une scène
- changer de sujet
- dormir
- envoyer un texto
- partir plusieurs jours

---

## Philosophie du moteur

Le moteur ne suit pas un scénario imposé.

Il simule :

- des personnages
- des relations
- des émotions
- des objectifs
- des souvenirs

et laisse l'histoire émerger naturellement.

Ainsi :

- Dean peut tomber amoureux
- Logan peut tomber amoureux à sa place
- personne ne peut tomber amoureux
- une rivalité peut apparaître
- une amitié peut naître

Aucun résultat n'est garanti.

---

# Fonctionnalités principales

## Narration hybride

L'IA doit pouvoir alterner entre :

- **Narration roman**

```
Dean s'appuie contre le mur et croise les bras.
"Tu es toujours aussi têtue ?"
```

- **Dialogue**

```
Dean :
Tu es toujours aussi têtue ?
```

- **Textos**

```
[Dean]
Tu es rentrée ?
```

---

## Monde vivant

Les personnages continuent à vivre même lorsque le joueur n'est pas présent.

Exemple :

Pendant que Elina dort :

- Dean parle à Garrett
- Beau organise une sortie
- Logan apprend une information
- une fête se prépare

Ces évènements sont enregistrés.

Le monde évolue sans le joueur.

---

## Evènement hors caméra

Le moteur doit être capable de générer :

```
Dean et Garrett ont discuté d'Elina.

Beau demande à Dean de garder ses distances.
```

sans que le joueur soit présent.

---

## Gestion du temps

Système hybride :

- **Temps réel narratif** : les scènes avancent naturellement.
- **Ellipses** : Le joueur peut décider :

```
Je vais dormir.

Je passe l'après-midi à travailler.

Je laisse passer trois jours.
```

Le moteur simule alors les évènements intermédiaires.

---

## Personnages

Chaque personnage possède :

- identité
- personnalité
- histoire
- relations
- souvenirs
- objectifs
- peurs
- désirs
- état émotionnel

Exemple pour Dean :

- humour
- charme
- impulsivité
- loyauté
- peur de l'engagement

---

## Systèmes de relations

Les relations ne sont pas binaires.

On ne stocke pas :

```
Amoureux : oui / non
```

mais plusieurs dimensions.

Exemple :

```
Attraction
Confiance
Respect
Attachement
Jalousie
Affection
Admiration
```

Ces valeurs évoluent selon les évènements.

---

## Mémoire

Chaque personnage dispose :

- **Lore permanent** : informations immuables

```
Dean joue au hockey
Dean est riche
Dean est le meilleur ami de Beau
```

- **Souvenirs** : évènements vécus

```
Elina lui a tenu tête.
```

- **Etat actuel** : évènements temporaires

```
Dean est jaloux
Dean est contrarié
Dans est blessé
```

---

## Univers

Le moteur doit être indépendant de l'univers.
L'univers est défini par :

- personnages
- lieux
- règles
- contexte

Ainsi le même moteur pourra fonctionner avec des univers différents et des univers originaux.

---

# Architecture technique envisagée

- **Backend**
  - Python
  - FastAPI
- **Base de données**
  - SQLIte
- **IA** : IA OpenAI dans un premier temps, mais évolution possible vers des modèles locaux ou autres fournisseurs
- **Frontend** : React ou Vue

---

# MVP 1

Objectif :

- Créer une histoire avec seulement :
  - Elina
  - Beau
  - Dean
- Fonctionnalités :
  - chargement des personnages
  - génération des scènes
  - mémoire persistante
  - évolution des relations
  - sauvegarde
- Pas encore :
  - SMS
  - évènements complexes
  - 10 personnages simultanés
  - simulation avancée

---

# Objectif final

Obtenir un système capable de générer des histoires longues, plusieurs semaines ou mois, cohérentes, émotionnelles et dynamiques, dans lesquelles :

- les personnages restent fidèles à leur personnalités ;
- les relations évoluent naturellement ;
- les évènements continuent à se produits même en l'absence du joueur ;
- l'utilisateur a réellement l'impression de vivre dans un roman dont il est le héros ;
