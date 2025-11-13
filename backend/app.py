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
# from routes import authentification, spots, conditions, previsions

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
def page_accueil():
    """
    Route principale qui sert la page d'accueil
    Retourne le fichier index.html du dossier frontend
    """
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:chemin>')
def fichiers_statiques(chemin):
    """
    Route pour servir tous les fichiers statiques (CSS, JS, images)
    Le paramètre chemin capture n'importe quel chemin demandé
    Exemple: /style5.css, /app.js, etc.
    """
    return send_from_directory('../frontend', chemin)

# ============================================================================
# ROUTES API - Points d'entrée de l'API REST
# ============================================================================

@app.route('/api/sante', methods=['GET'])
def verification_sante():
    """
    Route de diagnostic pour vérifier que l'API fonctionne
    Utile pour le monitoring et les tests
    Retourne un JSON avec le statut et l'heure
    """
    return jsonify({
        'statut': 'ok',
        'message': 'MySurf API fonctionne correctement',
        'horodatage': datetime.now().isoformat()
    })

# ----------------------------------------------------------------------------
# SPOTS - Gestion des spots de surf
# ----------------------------------------------------------------------------

@app.route('/api/spots', methods=['GET'])
def obtenir_spots():
    """
    Récupère la liste complète de tous les spots de surf
    Version avec 5 spots autour de Biarritz et Hossegor

    Pour l'instant, les données sont codées en dur dans le code
    Plus tard, on les lira depuis un fichier donnees/spots.json

    Retourne:
        JSON avec la liste des spots et leur nombre total
    """
    # Liste de 5 spots de la côte basque
    # Chaque spot contient: id, nom, localisation, coordonnées GPS, orientation et type
    spots = [
        {
            'id': 1,
            'nom': 'Hossegor - Plage Nord',
            'localisation': 'Hossegor, Landes',
            'latitude': 43.6667,  # Coordonnées GPS
            'longitude': -1.4,
            'orientation': 270,  # Direction en degrés (270 = Ouest)
            'type': 'beach_break'  # Type de vague (beach break, reef break, point break)
        },
        {
            'id': 2,
            'nom': 'Hossegor - La Gravière',
            'localisation': 'Hossegor, Landes',
            'latitude': 43.6617,
            'longitude': -1.4033,
            'orientation': 270,
            'type': 'beach_break'
        },
        {
            'id': 3,
            'nom': 'Biarritz - Grande Plage',
            'localisation': 'Biarritz, Pyrénées-Atlantiques',
            'latitude': 43.4832,
            'longitude': -1.5586,
            'orientation': 290,  # Ouest-Nord-Ouest
            'type': 'beach_break'
        },
        {
            'id': 4,
            'nom': 'Biarritz - Côte des Basques',
            'localisation': 'Biarritz, Pyrénées-Atlantiques',
            'latitude': 43.4762,
            'longitude': -1.5594,
            'orientation': 280,  # Ouest
            'type': 'beach_break'
        },
        {
            'id': 5,
            'nom': 'Guéthary - Parlementia',
            'localisation': 'Guéthary, Pyrénées-Atlantiques',
            'latitude': 43.4247,
            'longitude': -1.6061,
            'orientation': 315,  # Nord-Ouest
            'type': 'reef_break'
        }
    ]

    # Retourne un objet JSON standardisé
    # succes: indique si la requête a réussi
    # donnees: contient les données demandées
    # nombre: nombre d'éléments (utile pour la pagination)
    return jsonify({
        'succes': True,
        'donnees': spots,
        'nombre': len(spots)
    })

@app.route('/api/spots/<int:id_spot>', methods=['GET'])
def obtenir_spot_par_id(id_spot):
    """
    Récupère les détails d'un spot spécifique par son ID

    Args:
        id_spot: L'identifiant unique du spot (entier)

    Exemple d'appel: GET /api/spots/1

    Retourne:
        JSON avec les informations détaillées du spot
    """
    # Liste des spots (même liste que dans obtenir_spots)
    # Plus tard, on la mettra dans un fichier séparé ou une base de données
    spots = [
        {'id': 1, 'nom': 'Hossegor - Plage Nord', 'localisation': 'Hossegor, Landes', 'latitude': 43.6667, 'longitude': -1.4, 'orientation': 270, 'type': 'beach_break'},
        {'id': 2, 'nom': 'Hossegor - La Gravière', 'localisation': 'Hossegor, Landes', 'latitude': 43.6617, 'longitude': -1.4033, 'orientation': 270, 'type': 'beach_break'},
        {'id': 3, 'nom': 'Biarritz - Grande Plage', 'localisation': 'Biarritz, Pyrénées-Atlantiques', 'latitude': 43.4832, 'longitude': -1.5586, 'orientation': 290, 'type': 'beach_break'},
        {'id': 4, 'nom': 'Biarritz - Côte des Basques', 'localisation': 'Biarritz, Pyrénées-Atlantiques', 'latitude': 43.4762, 'longitude': -1.5594, 'orientation': 280, 'type': 'beach_break'},
        {'id': 5, 'nom': 'Guéthary - Parlementia', 'localisation': 'Guéthary, Pyrénées-Atlantiques', 'latitude': 43.4247, 'longitude': -1.6061, 'orientation': 315, 'type': 'reef_break'}
    ]

    # Chercher le spot avec l'ID demandé
    spot = next((s for s in spots if s['id'] == id_spot), None)

    if spot:
        return jsonify({
            'succes': True,
            'donnees': spot
        })
    else:
        return jsonify({
            'succes': False,
            'message': 'Spot non trouvé'
        }), 404

# ----------------------------------------------------------------------------
# CONDITIONS ACTUELLES - Récupération des conditions de surf en temps réel
# ----------------------------------------------------------------------------

@app.route('/api/conditions/<int:id_spot>', methods=['GET'])
def obtenir_conditions(id_spot):
    """
    Récupère les conditions de surf actuelles pour un spot donné

    Inclut:
        - Hauteur, période et direction des vagues
        - Force et direction du vent
        - Horaires et hauteurs des marées
        - Score de qualité des conditions (1-5)

    Args:
        id_spot: L'identifiant du spot

    Plus tard, ces données viendront d'une API météo externe (Stormglass, etc.)
    Pour l'instant, on utilise des données simulées pour tester
    """
    # Objet contenant toutes les conditions actuelles
    conditions = {
        'id_spot': id_spot,
        'horodatage': datetime.now().isoformat(),  # Heure de la mesure

        # Informations sur les vagues
        'vague': {
            'hauteur': 1.5,  # Hauteur en mètres
            'periode': 12,  # Période en secondes (temps entre 2 vagues)
            'direction': 225,  # Direction en degrés
            'direction_label': 'SO'  # Label lisible (Sud-Ouest)
        },

        # Informations sur le vent
        'vent': {
            'vitesse': 15,  # Vitesse en noeuds (kt)
            'direction': 45,  # Direction en degrés
            'direction_label': 'NE'  # Label lisible (Nord-Est)
        },

        # Informations sur les marées
        'maree': {
            'actuelle': 'montante',  # Marée montante ou descendante
            'basse': {
                'heure': '08:30',  # Heure de la marée basse
                'hauteur': 0.5  # Hauteur en mètres
            },
            'haute': {
                'heure': '14:15',  # Heure de la marée haute
                'hauteur': 3.2  # Hauteur en mètres
            }
        },

        # Score global des conditions (1 à 5 étoiles)
        'note': 4
    }

    return jsonify({
        'succes': True,
        'donnees': conditions
    })

# ----------------------------------------------------------------------------
# PRÉVISIONS - Prédictions des conditions pour les 5 prochains jours
# ----------------------------------------------------------------------------

@app.route('/api/previsions/<int:id_spot>', methods=['GET'])
def obtenir_previsions(id_spot):
    """
    Récupère les prévisions de surf pour J à J+4 (5 jours)

    Pour chaque jour:
        - Score de qualité (nombre d'étoiles)
        - Hauteur et période des vagues
        - Force et direction du vent

    Args:
        id_spot: L'identifiant du spot

    Ces données viendront plus tard du service calculateur_surf.py
    qui analysera les prévisions météo et calculera un score
    """
    # Liste des prévisions pour 5 jours
    # Chaque élément représente un jour
    previsions = [
        {
            'jour': 0,  # Jour 0 = aujourd'hui
            'libelle': 'AUJOURD\'HUI',
            'date': datetime.now().date().isoformat(),  # Date au format ISO (YYYY-MM-DD)
            'note': 4,  # Score sur 5
            'hauteur_vague': 1.5,  # Hauteur vague en mètres
            'periode_vague': 12,  # Période en secondes
            'vitesse_vent': 15,  # Vent en noeuds
            'direction_vent': 'NE'  # Direction du vent
        },
        {
            'jour': 1,
            'libelle': 'JOUR +1',
            'date': None,  # A calculer (aujourd'hui + 1 jour)
            'note': 3,
            'hauteur_vague': 1.2,
            'periode_vague': 10,
            'vitesse_vent': 20,
            'direction_vent': 'E'
        },
        {
            'jour': 2,
            'libelle': 'JOUR +2',
            'date': None,  # A calculer
            'note': 5,  # Excellentes conditions !
            'hauteur_vague': 2.0,
            'periode_vague': 14,
            'vitesse_vent': 10,
            'direction_vent': 'SO'
        },
        {
            'jour': 3,
            'libelle': 'JOUR +3',
            'date': None,  # A calculer
            'note': 2,  # Conditions médiocres
            'hauteur_vague': 0.8,
            'periode_vague': 8,
            'vitesse_vent': 25,
            'direction_vent': 'N'
        },
        {
            'jour': 4,
            'libelle': 'JOUR +4',
            'date': None,  # A calculer
            'note': 3,
            'hauteur_vague': 1.3,
            'periode_vague': 11,
            'vitesse_vent': 18,
            'direction_vent': 'NO'
        }
    ]

    return jsonify({
        'succes': True,
        'donnees': previsions,
        'nombre': len(previsions)
    })

# ----------------------------------------------------------------------------
# AUTHENTIFICATION - Gestion des utilisateurs
# ----------------------------------------------------------------------------

@app.route('/api/connexion', methods=['POST'])
def connexion():
    """
    Connexion d'un utilisateur existant

    Reçoit en POST:
        - nom_utilisateur: nom d'utilisateur
        - mot_de_passe: mot de passe

    Retourne:
        - Token d'authentification (JWT plus tard)
        - Informations utilisateur

    Note: Pour l'instant, version très simplifiée sans sécurité
    Plus tard, on vérifiera le mot de passe hashé en base de données
    et on générera un vrai token JWT
    """
    # Récupère les données JSON envoyées dans la requête
    donnees = request.get_json()

    # Validation: vérifie que les champs requis sont présents
    if not donnees or 'nom_utilisateur' not in donnees or 'mot_de_passe' not in donnees:
        return jsonify({
            'succes': False,
            'message': 'Nom d\'utilisateur et mot de passe requis'
        }), 400  # Code HTTP 400 = Bad Request

    # TODO: Vérifier le nom_utilisateur et mot_de_passe en base de données
    # TODO: Comparer le mot_de_passe hashé (avec bcrypt par exemple)

    # Pour l'instant, on accepte n'importe quelle combinaison
    # C'est juste pour tester le fonctionnement de l'API
    return jsonify({
        'succes': True,
        'message': 'Connexion réussie',
        'donnees': {
            'id_utilisateur': 1,
            'nom_utilisateur': donnees['nom_utilisateur'],
            'jeton': 'faux-jeton-jwt'  # A remplacer par un vrai JWT plus tard
        }
    })

@app.route('/api/inscription', methods=['POST'])
def inscription():
    """
    Inscription d'un nouvel utilisateur

    Reçoit en POST:
        - nom_utilisateur: nom d'utilisateur souhaité
        - mot_de_passe: mot de passe
        - email: adresse email (optionnel pour l'instant)

    Retourne:
        - Confirmation de l'inscription
        - ID du nouvel utilisateur

    TODO:
        - Vérifier que le nom_utilisateur n'existe pas déjà
        - Hasher le mot de passe avant de le sauvegarder
        - Sauvegarder dans un fichier JSON ou base de données
    """
    # Récupère les données envoyées
    donnees = request.get_json()

    # Validation des données
    if not donnees or 'nom_utilisateur' not in donnees or 'mot_de_passe' not in donnees:
        return jsonify({
            'succes': False,
            'message': 'Données incomplètes'
        }), 400

    # TODO: Vérifier que le nom_utilisateur est disponible
    # TODO: Hasher le mot_de_passe avec bcrypt
    # TODO: Sauvegarder le nouvel utilisateur

    # Pour l'instant, on confirme juste l'inscription
    return jsonify({
        'succes': True,
        'message': 'Inscription réussie',
        'donnees': {
            'id_utilisateur': 1,
            'nom_utilisateur': donnees['nom_utilisateur']
        }
    })

# ============================================================================
# GESTION DES ERREURS - Handlers pour les erreurs HTTP courantes
# ============================================================================

@app.errorhandler(404)
def non_trouve(erreur):
    """
    Gère les erreurs 404 (Page non trouvée)
    Se déclenche quand on essaie d'accéder à une route qui n'existe pas
    """
    return jsonify({
        'succes': False,
        'message': 'Route non trouvée'
    }), 404

@app.errorhandler(500)
def erreur_interne(erreur):
    """
    Gère les erreurs 500 (Erreur serveur interne)
    Se déclenche quand il y a une exception non gérée dans le code
    """
    return jsonify({
        'succes': False,
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
    print("  GET  /api/sante")
    print("  GET  /api/spots")
    print("  GET  /api/spots/<id>")
    print("  GET  /api/conditions/<id_spot>")
    print("  GET  /api/previsions/<id_spot>")
    print("  POST /api/connexion")
    print("  POST /api/inscription")
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