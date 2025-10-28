# MySurf - Application de Prévisions Surf

Application web pour visualiser les conditions de surf en temps réel et les prévisions pour les 5 prochains jours.

## Technologies

- **Backend** : Python Flask
- **Frontend** : HTML, CSS, JavaScript
- **API** : RESTful API

## Structure du projet
```
mysurf/
├── backend/
│   ├── app.py                    # Serveur Flask principal
│   ├── routes/                   # Routes de l'API
│   ├── services/                 # Logique métier
│   └── donnees/                  # Données locales
├── frontend/
│   ├── index.html               # Page principale
│   ├── style5.css               # Styles CSS
│   └── app.js                   # JavaScript (à venir)
└── requirements.txt             # Dépendances Python
```

## Installation

### 1. Cloner le projet
```bash
git clone https://github.com/votre-username/mysurf.git
cd mysurf
```

### 2. Créer un environnement virtuel
```bash
python -m venv .venv
```

### 3. Activer l'environnement virtuel

**Windows :**
```bash
.venv\Scripts\activate
```

**Mac/Linux :**
```bash
source .venv/bin/activate
```

### 4. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 5. Lancer l'application
```bash
python backend/app.py
```

### 6. Ouvrir dans le navigateur
```
http://localhost:5000
```

## Routes API disponibles

- `GET /api/sante` - Vérifier que l'API fonctionne
- `GET /api/spots` - Liste des spots de surf
- `GET /api/spots/<id>` - Détails d'un spot
- `GET /api/conditions/<id_spot>` - Conditions actuelles
- `GET /api/previsions/<id_spot>` - Prévisions J à J+4
- `POST /api/connexion` - Connexion utilisateur
- `POST /api/inscription` - Inscription utilisateur

## Développement

Projet pédagogique pour apprendre :
- Le développement d'API REST avec Flask
- L'intégration frontend/backend
- La manipulation de données météo
- L'authentification utilisateur

## Auteur

Votre Nom

## Licence

MIT