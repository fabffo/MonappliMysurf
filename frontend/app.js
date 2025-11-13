/**
 * MySurf - Application JavaScript principale
 * Gère le chargement des spots et l'affichage des conditions
 */

// URL de base de l'API
const API_URL = 'http://localhost:5000/api';

// Variable pour stocker le spot actuellement sélectionné
let spotActuel = null;

/**
 * Initialisation au chargement de la page
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('MySurf - Initialisation');
    chargerSpots();
});

/**
 * Charge la liste des spots depuis l'API
 */
async function chargerSpots() {
    try {
        console.log('Chargement des spots...');

        // Appel à l'API
        const reponse = await fetch(`${API_URL}/spots`);
        const data = await reponse.json();

        if (data.succes && data.donnees) {
            console.log(`${data.nombre} spots chargés`);

            // Remplir le menu déroulant
            remplirSelecteurSpots(data.donnees);

            // Charger le premier spot par défaut
            if (data.donnees.length > 0) {
                chargerConditionsSpot(data.donnees[0].id);
            }
        }

    } catch (erreur) {
        console.error('Erreur chargement spots:', erreur);
        alert('Impossible de charger les spots. Vérifiez que l\'API est lancée.');
    }
}

/**
 * Remplit le menu déroulant avec la liste des spots
 * @param {Array} spots - Liste des spots
 */
function remplirSelecteurSpots(spots) {
    const selecteur = document.getElementById('selecteur-spot');

    // Vider le selecteur
    selecteur.innerHTML = '';

    // Ajouter chaque spot comme option
    spots.forEach(spot => {
        const option = document.createElement('option');
        option.value = spot.id;
        option.textContent = spot.nom;
        selecteur.appendChild(option);
    });

    // Écouter les changements de sélection
    selecteur.addEventListener('change', function() {
        const idSpot = parseInt(this.value);
        console.log(`Spot sélectionné: ${idSpot}`);
        chargerConditionsSpot(idSpot);
    });
}

/**
 * Charge les conditions d'un spot spécifique
 * @param {number} idSpot - ID du spot
 */
async function chargerConditionsSpot(idSpot) {
    try {
        console.log(`Chargement conditions spot ${idSpot}...`);

        // Appel à l'API conditions
        const reponseConditions = await fetch(`${API_URL}/conditions/${idSpot}`);
        const dataConditions = await reponseConditions.json();

        // Appel à l'API prévisions
        const reponsePrevisions = await fetch(`${API_URL}/previsions/${idSpot}`);
        const dataPrevisions = await reponsePrevisions.json();

        if (dataConditions.succes && dataPrevisions.succes) {
            afficherConditions(dataConditions.donnees);
            afficherPrevisions(dataPrevisions.donnees);
        }

    } catch (erreur) {
        console.error('Erreur chargement conditions:', erreur);
    }
}

/**
 * Affiche les conditions actuelles dans la page
 * @param {Object} conditions - Données des conditions
 */
function afficherConditions(conditions) {
    // Mise à jour des vagues
    document.getElementById('hauteur-vague').textContent = `${conditions.vague.hauteur} m`;
    document.getElementById('direction-vague').textContent =
        `${conditions.vague.direction_label} (${conditions.vague.direction}°)`;
    document.getElementById('periode-vague').textContent = `${conditions.vague.periode} s`;

    // Mise à jour du vent
    document.getElementById('force-vent').textContent = `${conditions.vent.vitesse} kt`;
    document.getElementById('direction-vent').textContent =
        `${conditions.vent.direction_label} (${conditions.vent.direction}°)`;

    // Mise à jour des marées
    document.getElementById('maree-basse').textContent = conditions.maree.basse.heure;
    document.getElementById('maree-haute').textContent = conditions.maree.haute.heure;
}

/**
 * Affiche les prévisions dans la page
 * @param {Array} previsions - Données des prévisions
 */
function afficherPrevisions(previsions) {
    const conteneur = document.getElementById('previsions');
    conteneur.innerHTML = '';

    previsions.forEach(prev => {
        const divJour = document.createElement('div');
        divJour.className = 'jour';

        // Créer les étoiles selon la note
        const etoiles = '⭐'.repeat(prev.note);

        divJour.innerHTML = `
            <div class="titre-jour">${prev.libelle}</div>
            <div class="contenu">
                ${etoiles}<br>
                ${prev.hauteur_vague}m - ${prev.periode_vague}s<br>
                ${prev.vitesse_vent}kt ${prev.direction_vent}
            </div>
        `;

        conteneur.appendChild(divJour);
    });
}

// Log pour vérifier que le script est chargé
console.log('app.js chargé');