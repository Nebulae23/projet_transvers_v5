#version 450 core

// Ce fichier contient les fonctions pour le calcul des ombres PCSS.
// Il est destiné à être inclus ou adapté dans un shader d'éclairage principal.

uniform sampler2DShadow shadowMap; // La shadow map (utilisant sampler2DShadow pour la comparaison matérielle)
uniform vec2 shadowMapSize;       // Taille de la texture de la shadow map (largeur, hauteur)
uniform float lightSizeUV;        // Taille de la source lumineuse en UV sur la shadow map (approximatif)
uniform float nearPlane;          // Near plane de la caméra de la lumière

const int BLOCKER_SEARCH_NUM_SAMPLES = 16; // Nombre d'échantillons pour la recherche de bloqueurs
const int PCF_NUM_SAMPLES = 32;            // Nombre d'échantillons pour le filtrage PCF

// Fonction pour trouver la profondeur moyenne des bloqueurs
float findBlockerDepth(vec3 fragPosLightSpace, vec2 searchRegionRadiusUV)
{
    float avgBlockerDepth = 0.0;
    int numBlockers = 0;

    vec2 texelSize = 1.0 / shadowMapSize;

    for (int i = 0; i < BLOCKER_SEARCH_NUM_SAMPLES; ++i)
    {
        // Échantillonner dans une région autour du fragment
        // Utiliser une distribution de Poisson ou une grille régulière simple
        float angle = float(i) / float(BLOCKER_SEARCH_NUM_SAMPLES) * 2.0 * 3.14159265;
        float radius = sqrt(float(i) / float(BLOCKER_SEARCH_NUM_SAMPLES)); // Distribution en disque simple
        vec2 offset = vec2(cos(angle), sin(angle)) * radius * searchRegionRadiusUV;

        vec3 sampleCoords = vec3(fragPosLightSpace.xy + offset, fragPosLightSpace.z);

        // Comparer la profondeur (textureProj effectue la comparaison z <= depth_in_map)
        // Nous voulons la profondeur des bloqueurs (ceux qui sont PLUS PROCHES que le fragment)
        float shadowMapDepth = texture(shadowMap, sampleCoords).r; // Obtenir la profondeur stockée

        // Si l'échantillon est un bloqueur (plus proche que le fragment actuel)
        if (shadowMapDepth < fragPosLightSpace.z - 0.005) // Ajouter un biais
        {
            avgBlockerDepth += shadowMapDepth;
            numBlockers++;
        }
    }

    if (numBlockers == 0)
        return 0.0; // Pas de bloqueurs trouvés

    return avgBlockerDepth / float(numBlockers);
}


// Fonction principale pour calculer l'ombre PCSS
// fragPosLightSpace: Coordonnées du fragment dans l'espace lumière [0, 1] pour xy, profondeur linéaire pour z
// lightDir: Direction normalisée vers la lumière (utilisée pour le biais)
// N: Normale du fragment (utilisée pour le biais)
float calculatePCSS(vec3 fragPosLightSpace, vec3 lightDir, vec3 N)
{
    // -------- Étape 1: Recherche des bloqueurs --------
    // Calculer la taille de la région de recherche basée sur la taille de la lumière et la distance
    // w = (d_receiver - d_blocker) / d_blocker * lightSize
    // Ici, on approxime la taille de la région de recherche en UV
    float searchRegionRadiusUV = lightSizeUV * (fragPosLightSpace.z - nearPlane) / fragPosLightSpace.z; // Approximation

    float avgBlockerDepth = findBlockerDepth(fragPosLightSpace, vec2(searchRegionRadiusUV));

    if (avgBlockerDepth == 0.0) // Pas de bloqueurs, le fragment est entièrement éclairé
        return 1.0;

    // -------- Étape 2: Estimation du Penumbra --------
    // Calculer la taille du penumbra basée sur la distance moyenne des bloqueurs
    // w_penumbra = (d_receiver - d_avg_blocker) / d_avg_blocker * lightSizeUV
    // Note: fragPosLightSpace.z est la profondeur du récepteur (d_receiver)
    // avgBlockerDepth est la profondeur moyenne des bloqueurs (d_avg_blocker)
    // Assurez-vous que les profondeurs sont comparables (linéaires ou non)
    float penumbraRadiusUV = (fragPosLightSpace.z - avgBlockerDepth) / avgBlockerDepth * lightSizeUV;

    // -------- Étape 3: Filtrage PCF --------
    float shadow = 0.0;
    vec2 texelSize = 1.0 / shadowMapSize;

    // Biais basé sur la pente pour éviter l'acné d'ombre
    float bias = max(0.05 * (1.0 - dot(N, lightDir)), 0.005);

    for (int i = 0; i < PCF_NUM_SAMPLES; ++i)
    {
        // Utiliser une distribution de Poisson ou une grille régulière pour les échantillons PCF
        float angle = float(i) / float(PCF_NUM_SAMPLES) * 2.0 * 3.14159265;
        float radius = sqrt(float(i) / float(PCF_NUM_SAMPLES)); // Distribution en disque simple
        vec2 offset = vec2(cos(angle), sin(angle)) * radius * penumbraRadiusUV;

        // Coordonnées pour l'échantillonnage PCF avec le biais
        vec4 pcfCoords = vec4(fragPosLightSpace.xy + offset, fragPosLightSpace.z - bias, 1.0);

        // Utiliser textureProj pour la comparaison de profondeur matérielle
        // textureProj compare pcfCoords.z <= texture(shadowMap, pcfCoords.xy)
        shadow += textureProj(shadowMap, pcfCoords);
    }

    return shadow / float(PCF_NUM_SAMPLES);
}

// Fonction principale (placeholder si ce fichier est compilé seul)
// void main() { FragColor = vec4(1.0); }