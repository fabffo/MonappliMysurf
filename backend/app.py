"""
MySurf API - Application principale
Serveur Flask pour l'API de prévisions surf
Projet pédagogique Python pour apprendre le développement web
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
from datetime import datetime

# Import des routes (on les créera progressivement)
# from routes import auth, spots, conditions, forecast

# Initialisation de l'application Flask
app = Flask(__name__, static_folder='../frontend')

# Activation de CORS (Cross-Origin Resource Sharing)
# Permet au frontend de communiquer avec l'API même s'ils sont sur des ports différents
CORS(app)

# Configuration de l'application
app.config['SECRET_KEY'] = 'votre-cle-secrete-a-changer'  # A mettre dans .env plus tard pour la sécurité
app.config['JSON_AS_ASCII'] = False  # Permet l'affichage correct des accents français dans les réponses JSON

# ============================================================================
# ROUTES STATIQUES - Servir les fichiers HTML/CSS/JS du frontend
# ============================================================================

@app.route('/')
def index():
    """
    Route principale qui sert la page d'accueil
    Retourne le fichier index.html du dossier frontend
    """
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    """
    Route pour servir tous les fichiers statiques (CSS, JS, images)
    Le paramètre path capture n'importe quel chemin demandé
    Exemple: /style5.css, /app.js, etc.
    """
    return send_from_directory('../frontend', path)

# ============================================================================
# ROUTES API - Points d'entrée de l'API REST
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Route de diagnostic pour vérifier que l'API fonctionne
    Utile pour le monitoring et les tests
    Retourne un JSON avec le statut et l'heure
    """
    return jsonify({
        'status': 'ok',
        'message': 'MySurf API is running',
        'timestamp': datetime.now().isoformat()
    })

# ----------------------------------------------------------------------------
# SPOTS - Gestion des spots de surf
# ----------------------------------------------------------------------------

@app.route('/api/spots', methods=['GET'])
def get_spots():
    """
    Récupère la liste complète de tous les spots de surf

    Pour l'instant, les données sont codées en dur dans le code
    Plus tard, on les lira depuis un fichier data/spots.json

    Retourne:
        JSON avec la liste des spots et leur nombre total
    """
    # Liste temporaire des spots
    # Chaque spot contient: id, nom, localisation, coordonnées GPS, orientation et type
    spots = [
        {
            'id': 1,
            'name': 'Hossegor - Plage Nord',
            'location': 'Hossegor, France',
            'latitude': 43.6667,  # Coordonnées GPS
            'longitude': -1.4,
            'orientation': 270,  # Direction en degrés (270 = Ouest)
            'type': 'beach_break'  # Type de vague (beach break, reef break, point break)
        },
        {
            'id': 2,
            'name': 'Hossegor - La Gravière',
            'location': 'Hossegor, France',
            'latitude': 43.6617,
            'longitude': -1.4033,
            'orientation': 270,
            'type': 'beach_break'
        },
        {
            'id': 3,
            'name': 'Biarritz - Grande Plage',
            'location': 'Biarritz, France',
            'latitude': 43.4832,
            'longitude': -1.5586,
            'orientation': 290,
            'type': 'beach_break'
        }
    ]

    # Retourne un objet JSON standardisé
    # success: indique si la requête a réussi
    # data: contient les données demandées
    # count: nombre d'éléments (utile pour la pagination)
    return jsonify({
        'success': True,
        'data': spots,
        'count': len(spots)
    })

@app.route('/api/spots/<int:spot_id>', methods=['GET'])
def get_spot_by_id(spot_id):
    """
    Récupère les détails d'un spot spécifique par son ID

    Args:
        spot_id: L'identifiant unique du spot (entier)

    Exemple d'appel: GET /api/spots/1

    Retourne:
        JSON avec les informations détaillées du spot
    """
    # Pour l'instant, on simule avec des données fixes
    # Plus tard, on cherchera le spot réel dans la base de données
    spot = {
        'id': spot_id,
        'name': 'Hossegor - Plage Nord',
        'location': 'Hossegor, France',
        'latitude': 43.6667,
        'longitude': -1.4,
        'orientation': 270,
        'type': 'beach_break',
        'description': 'Un des meilleurs spots de France'
    }

    return jsonify({
        'success': True,
        'data': spot
    })

# ----------------------------------------------------------------------------
# CONDITIONS ACTUELLES - Récupération des conditions de surf en temps réel
# ----------------------------------------------------------------------------

@app.route('/api/conditions/<int:spot_id>', methods=['GET'])
def get_conditions(spot_id):
    """
    Récupère les conditions de surf actuelles pour un spot donné

    Inclut:
        - Hauteur, période et direction des vagues
        - Force et direction du vent
        - Horaires et hauteurs des marées
        - Score de qualité des conditions (1-5)

    Args:
        spot_id: L'identifiant du spot

    Plus tard, ces données viendront d'une API météo externe (Stormglass, etc.)
    Pour l'instant, on utilise des données simulées pour tester
    """
    # Objet contenant toutes les conditions actuelles
    conditions = {
        'spot_id': spot_id,
        'timestamp': datetime.now().isoformat(),  # Heure de la mesure

        # Informations sur les vagues
        'wave': {
            'height': 1.5,  # Hauteur en mètres
            'period': 12,  # Période en secondes (temps entre 2 vagues)
            'direction': 225,  # Direction en degrés
            'direction_label': 'SW'  # Label lisible (Sud-Ouest)
        },

        # Informations sur le vent
        'wind': {
            'speed': 15,  # Vitesse en noeuds (kt)
            'direction': 45,  # Direction en degrés
            'direction_label': 'NE'  # Label lisible (Nord-Est)
        },

        # Informations sur les marées
        'tide': {
            'current': 'rising',  # Marée montante ou descendante
            'low': {
                'time': '08:30',  # Heure de la marée basse
                'height': 0.5  # Hauteur en mètres
            },
            'high': {
                'time': '14:15',  # Heure de la marée haute
                'height': 3.2  # Hauteur en mètres
            }
        },

        # Score global des conditions (1 à 5 étoiles)
        'rating': 4
    }

    return jsonify({
        'success': True,
        'data': conditions
    })

# ----------------------------------------------------------------------------
# PRÉVISIONS - Prédictions des conditions pour les 5 prochains jours
# ----------------------------------------------------------------------------

@app.route('/api/forecast/<int:spot_id>', methods=['GET'])
def get_forecast(spot_id):
    """
    Récupère les prévisions de surf pour J à J+4 (5 jours)

    Pour chaque jour:
        - Score de qualité (nombre d'étoiles)
        - Hauteur et période des vagues
        - Force et direction du vent

    Args:
        spot_id: L'identifiant du spot

    Ces données viendront plus tard du service surf_calculator.py
    qui analysera les prévisions météo et calculera un score
    """
    # Liste des prévisions pour 5 jours
    # Chaque élément représente un jour
    forecast = [
        {
            'day': 0,  # Jour 0 = aujourd'hui
            'label': 'AUJOURD\'HUI',
            'date': datetime.now().date().isoformat(),  # Date au format ISO (YYYY-MM-DD)
            'rating': 4,  # Score sur 5
            'wave_height': 1.5,  # Hauteur vague en mètres
            'wave_period': 12,  # Période en secondes
            'wind_speed': 15,  # Vent en noeuds
            'wind_direction': 'NE'  # Direction du vent
        },
        {
            'day': 1,
            'label': 'JOUR +1',
            'date': None,  # A calculer (aujourd'hui + 1 jour)
            'rating': 3,
            'wave_height': 1.2,
            'wave_period': 10,
            'wind_speed': 20,
            'wind_direction': 'E'
        },
        {
            'day': 2,
            'label': 'JOUR +2',
            'date': None,  # A calculer
            'rating': 5,  # Excellentes conditions !
            'wave_height': 2.0,
            'wave_period': 14,
            'wind_speed': 10,
            'wind_direction': 'SW'
        },
        {
            'day': 3,
            'label': 'JOUR +3',
            'date': None,  # A calculer
            'rating': 2,  # Conditions médiocres
            'wave_height': 0.8,
            'wave_period': 8,
            'wind_speed': 25,
            'wind_direction': 'N'
        },
        {
            'day': 4,
            'label': 'JOUR +4',
            'date': None,  # A calculer
            'rating': 3,
            'wave_height': 1.3,
            'wave_period': 11,
            'wind_speed': 18,
            'wind_direction': 'NW'
        }
    ]

    return jsonify({
        'success': True,
        'data': forecast,
        'count': len(forecast)
    })

# ----------------------------------------------------------------------------
# AUTHENTIFICATION - Gestion des utilisateurs
# ----------------------------------------------------------------------------

@app.route('/api/login', methods=['POST'])
def login():
    """
    Connexion d'un utilisateur existant

    Reçoit en POST:
        - username: nom d'utilisateur
        - password: mot de passe

    Retourne:
        - Token d'authentification (JWT plus tard)
        - Informations utilisateur

    Note: Pour l'instant, version très simplifiée sans sécurité
    Plus tard, on vérifiera le mot de passe hashé en base de données
    et on générera un vrai token JWT
    """
    # Récupère les données JSON envoyées dans la requête
    data = request.get_json()

    # Validation: vérifie que les champs requis sont présents
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({
            'success': False,
            'message': 'Username et password requis'
        }), 400  # Code HTTP 400 = Bad Request

    # TODO: Vérifier le username et password en base de données
    # TODO: Comparer le password hashé (avec bcrypt par exemple)

    # Pour l'instant, on accepte n'importe quelle combinaison
    # C'est juste pour tester le fonctionnement de l'API
    return jsonify({
        'success': True,
        'message': 'Connexion réussie',
        'data': {
            'user_id': 1,
            'username': data['username'],
            'token': 'fake-jwt-token'  # A remplacer par un vrai JWT plus tard
        }
    })

@app.route('/api/register', methods=['POST'])
def register():
    """
    Inscription d'un nouvel utilisateur

    Reçoit en POST:
        - username: nom d'utilisateur souhaité
        - password: mot de passe
        - email: adresse email (optionnel pour l'instant)

    Retourne:
        - Confirmation de l'inscription
        - ID du nouvel utilisateur

    TODO:
        - Vérifier que le username n'existe pas déjà
        - Hasher le mot de passe avant de le sauvegarder
        - Sauvegarder dans un fichier JSON ou base de données
    """
    # Récupère les données envoyées
    data = request.get_json()

    # Validation des données
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({
            'success': False,
            'message': 'Données incomplètes'
        }), 400

    # TODO: Vérifier que le username est disponible
    # TODO: Hasher le password avec bcrypt
    # TODO: Sauvegarder le nouvel utilisateur

    # Pour l'instant, on confirme juste l'inscription
    return jsonify({
        'success': True,
        'message': 'Inscription réussie',
        'data': {
            'user_id': 1,
            'username': data['username']
        }
    })

# ============================================================================
# GESTION DES ERREURS - Handlers pour les erreurs HTTP courantes
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """
    Gère les erreurs 404 (Page non trouvée)
    Se déclenche quand on essaie d'accéder à une route qui n'existe pas
    """
    return jsonify({
        'success': False,
        'message': 'Route non trouvée'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """
    Gère les erreurs 500 (Erreur serveur interne)
    Se déclenche quand il y a une exception non gérée dans le code
    """
    return jsonify({
        'success': False,
        'message': 'Erreur serveur interne'
    }), 500

# ============================================================================
# LANCEMENT DU SERVEUR - Point d'entrée principal
# ============================================================================

if __name__ == '__main__':
    # Affichage des informations de démarrage
    print("=" * 60)
    print("MySurf API - Démarrage")
    print("=" * 60)
    print("API disponible sur : http://localhost:5000")
    print("Frontend disponible sur : http://localhost:5000")
    print("=" * 60)
    print("\nRoutes API disponibles :")
    print("  GET  /api/health")
    print("  GET  /api/spots")
    print("  GET  /api/spots/<id>")
    print("  GET  /api/conditions/<spot_id>")
    print("  GET  /api/forecast/<spot_id>")
    print("  POST /api/login")
    print("  POST /api/register")
    print("\nAppuyez sur Ctrl+C pour arrêter\n")

    # Lancement du serveur Flask
    # host='0.0.0.0' : accessible depuis n'importe quelle interface réseau
    # port=5000 : port d'écoute du serveur
    # debug=True : active le mode debug (rechargement auto + messages d'erreur détaillés)
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )