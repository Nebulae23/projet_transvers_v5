#version 330 core

// Entrées depuis le Vertex Shader
in vec2 v_TexCoords;       // Coordonnées de texture interpolées
in vec3 v_WorldPos;        // Position du fragment dans l'espace monde
in vec3 v_Normal;          // Normale du fragment dans l'espace monde

// Sortie du shader
out vec4 FragColor;

// Textures
uniform sampler2D u_spriteTexture; // Texture principale du sprite (Albedo + Alpha)
// Optionnel: Autres textures PBR si utilisées (Normal, MetallicRoughness, AO)
// uniform sampler2D u_normalMap;
// uniform sampler2D u_metallicRoughnessMap;
// uniform sampler2D u_aoMap;

// Propriétés du matériau (si non texturées)
uniform vec4 u_baseColorFactor = vec4(1.0, 1.0, 1.0, 1.0); // Multiplicateur de couleur
uniform float u_metallicFactor = 0.1;   // Facteur métallique (0=diélectrique, 1=métal)
uniform float u_roughnessFactor = 0.8;  // Facteur de rugosité (0=lisse, 1=rugueux)
uniform float u_aoFactor = 1.0;         // Facteur d'occlusion ambiante (si pas de map)

// Informations globales
uniform vec3 u_cameraPosition;    // Position de la caméra dans l'espace monde
uniform vec3 u_ambientLight = vec3(0.1, 0.1, 0.1); // Couleur de la lumière ambiante globale

// Structure pour les lumières (simplifiée)
struct Light {
    vec3 position;    // Position (point/spot) ou Direction (directionnelle, w=0)
    vec3 color;       // Couleur de la lumière
    float intensity;
    int type;         // 0: Directional, 1: Point, 2: Spot
    // Pour Spot: vec3 direction; float cutOff; float outerCutOff;
};

// Tableau de lumières (taille fixe, ex: 4)
const int MAX_LIGHTS = 4;
uniform Light u_lights[MAX_LIGHTS];
uniform int u_numLights; // Nombre réel de lumières actives

// Constantes PBR
const float PI = 3.14159265359;

// --- Fonctions PBR (Cook-Torrance BRDF) ---

// Distribution des normales (GGX / Trowbridge-Reitz)
float DistributionGGX(vec3 N, vec3 H, float roughness) {
    float a = roughness * roughness;
    float a2 = a * a;
    float NdotH = max(dot(N, H), 0.0);
    float NdotH2 = NdotH * NdotH;

    float nom   = a2;
    float denom = (NdotH2 * (a2 - 1.0) + 1.0);
    denom = PI * denom * denom;

    return nom / max(denom, 0.001); // Éviter division par zéro
}

// Géométrie (Schlick-GGX)
float GeometrySchlickGGX(float NdotV, float roughness) {
    float r = (roughness + 1.0);
    float k = (r * r) / 8.0; // Direct light
    // float k = (roughness * roughness) / 2.0; // IBL
    float nom   = NdotV;
    float denom = NdotV * (1.0 - k) + k;
    return nom / max(denom, 0.001);
}

float GeometrySmith(vec3 N, vec3 V, vec3 L, float roughness) {
    float NdotV = max(dot(N, V), 0.0);
    float NdotL = max(dot(N, L), 0.0);
    float ggx2 = GeometrySchlickGGX(NdotV, roughness);
    float ggx1 = GeometrySchlickGGX(NdotL, roughness);
    return ggx1 * ggx2;
}

// Fresnel (Schlick approximation)
vec3 fresnelSchlick(float cosTheta, vec3 F0) {
    return F0 + (1.0 - F0) * pow(clamp(1.0 - cosTheta, 0.0, 1.0), 5.0);
}

// --- Shader Principal ---

void main()
{
    // 1. Lire les propriétés de base du matériau depuis la texture
    vec4 texColor = texture(u_spriteTexture, v_TexCoords);
    vec3 albedo = pow(texColor.rgb * u_baseColorFactor.rgb, vec3(2.2)); // Correction Gamma -> Linéaire
    float alpha = texColor.a * u_baseColorFactor.a;

    // Alpha testing (ignorer les pixels transparents)
    if (alpha < 0.1) {
        discard;
    }

    // 2. Définir les propriétés PBR
    // TODO: Lire depuis les textures si disponibles (u_metallicRoughnessMap, u_aoMap)
    float metallic = u_metallicFactor;
    float roughness = u_roughnessFactor;
    float ao = u_aoFactor; // TODO: Lire depuis u_aoMap si disponible

    // 3. Préparer les vecteurs pour l'éclairage
    vec3 N = normalize(v_Normal); // Normale (déjà interpolée et normalisée ?)
    vec3 V = normalize(u_cameraPosition - v_WorldPos); // Vecteur de vue

    // Calculer F0 (réflectance à incidence normale)
    vec3 F0 = vec3(0.04); // Base pour diélectriques
    F0 = mix(F0, albedo, metallic); // Mélanger avec albedo pour les métaux

    // 4. Calculer l'éclairage direct (boucle sur les lumières)
    vec3 Lo = vec3(0.0); // Lumière sortante
    for (int i = 0; i < u_numLights; ++i) {
        // Calculer le vecteur lumière (L) et l'atténuation/distance
        vec3 L;
        float distance;
        float attenuation = 1.0;
        vec3 lightColor = u_lights[i].color * u_lights[i].intensity;

        if (u_lights[i].type == 0) { // Directional Light
            L = normalize(-u_lights[i].position); // La position contient la direction opposée
            distance = 10000.0; // "Infini"
        } else { // Point Light (simplifié, pas de Spot ici)
            vec3 lightDir = u_lights[i].position - v_WorldPos;
            distance = length(lightDir);
            L = normalize(lightDir);
            // Atténuation quadratique inverse (simple)
            attenuation = 1.0 / (distance * distance + 1.0); // Ajouter +1 pour éviter div par zéro proche
        }

        // Vecteur demi-angle (Halfway vector)
        vec3 H = normalize(V + L);

        // Calculer la radiance (couleur * intensité * atténuation)
        vec3 radiance = lightColor * attenuation;

        // Terme BRDF (Cook-Torrance)
        float NDF = DistributionGGX(N, H, roughness);
        float G = GeometrySmith(N, V, L, roughness);
        vec3 F = fresnelSchlick(max(dot(H, V), 0.0), F0);

        vec3 kS = F; // Terme spéculaire Fresnel
        vec3 kD = vec3(1.0) - kS; // Terme diffus (conservation d'énergie)
        kD *= (1.0 - metallic); // Les métaux n'ont pas de diffusion de couleur

        // Calcul BRDF
        float NdotL = max(dot(N, L), 0.0);
        vec3 numerator = NDF * G * F;
        float denominator = 4.0 * max(dot(N, V), 0.0) * NdotL + 0.001; // Ajouter epsilon
        vec3 specular = numerator / denominator;

        // Ajouter la contribution de la lumière (diffus + spéculaire)
        // Note: Le terme PI dans BRDF est annulé par le cos(theta) de l'éclairage Lambertien
        Lo += (kD * albedo / PI + specular) * radiance * NdotL;
    }

    // 5. Ajouter l'éclairage ambiant (simplifié)
    // TODO: Utiliser IBL (Image-Based Lighting) si disponible
    vec3 ambient = u_ambientLight * albedo * ao; // Appliquer AO à l'ambiante

    // 6. Combiner éclairage direct et ambiant
    vec3 color = ambient + Lo;

    // 7. Correction Gamma (Linéaire -> sRGB) et sortie
    color = pow(color, vec3(1.0/2.2));
    FragColor = vec4(color, alpha);
}