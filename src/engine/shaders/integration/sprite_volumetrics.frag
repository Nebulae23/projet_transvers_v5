#version 330 core

// Entrées depuis le Vertex Shader
in vec2 v_TexCoords;   // Coordonnées de texture
in vec3 v_WorldPos;    // Position dans l'espace monde
in vec4 v_ViewPos;     // Position dans l'espace vue
in vec4 v_ClipPos;     // Position en espace clip

// Sortie
out vec4 FragColor;

// Texture du sprite
uniform sampler2D u_spriteTexture;
uniform vec4 u_baseColorFactor = vec4(1.0);

// Ressources volumétriques
// Option 1: Texture 3D de brouillard/lumière volumétrique pré-calculée
uniform sampler3D u_volumetricTexture;
uniform mat4 u_worldToVolumeTransform; // Matrice pour passer de l'espace monde à l'espace de la texture volumétrique

// Option 2: Texture 2D de brouillard volumétrique en espace écran (résultat d'un compute shader)
uniform sampler2D u_screenSpaceVolumetricTexture;
uniform vec2 u_screenResolution; // Pour calculer les UVs écran

// Paramètres de mélange
uniform float u_volumetricIntensity = 1.0; // Intensité de l'effet volumétrique appliqué
uniform float u_volumetricScattering = 0.5; // Facteur de diffusion (comment la lumière volumétrique s'ajoute)

// Fonction pour échantillonner le volume 3D
vec4 sampleVolumeTexture(vec3 worldPos) {
    // Transformer la position monde en coordonnées de texture volumétrique
    vec4 volumeCoords4 = u_worldToVolumeTransform * vec4(worldPos, 1.0);
    // Normaliser si nécessaire (dépend de la matrice et de la configuration de la texture)
    vec3 volumeCoords = volumeCoords4.xyz / volumeCoords4.w;
    // Échantillonner la texture 3D (s'assurer que les coords sont dans [0, 1])
    if (all(greaterThanEqual(volumeCoords, vec3(0.0))) && all(lessThanEqual(volumeCoords, vec3(1.0)))) {
        return texture(u_volumetricTexture, volumeCoords);
    } else {
        return vec4(0.0); // En dehors du volume
    }
}

// Fonction pour échantillonner le volume en espace écran
vec4 sampleScreenSpaceVolume() {
    // Calculer les coordonnées UV écran à partir de la position clip
    vec2 screenUV = (v_ClipPos.xy / v_ClipPos.w) * 0.5 + 0.5;
    return texture(u_screenSpaceVolumetricTexture, screenUV);
}

void main()
{
    // Lire la couleur et l'alpha du sprite
    vec4 spriteColor = texture(u_spriteTexture, v_TexCoords) * u_baseColorFactor;

    // Alpha testing
    if (spriteColor.a < 0.1) {
        discard;
    }

    // Échantillonner les données volumétriques
    // Choisir l'une des méthodes (ou combiner)
    // vec4 volumetricData = sampleVolumeTexture(v_WorldPos);
    vec4 volumetricData = sampleScreenSpaceVolume(); // Utiliser l'espace écran ici

    // Interpréter les données volumétriques (ex: RGB = in-scattering, A = extinction/density)
    vec3 inScattering = volumetricData.rgb;
    float extinction = volumetricData.a; // Ou une autre interprétation

    // Calculer l'effet volumétrique sur la couleur du sprite
    // Modèle simple :
    // 1. Atténuer la couleur du sprite par l'extinction
    // 2. Ajouter la lumière diffusée (in-scattering)
    // Le facteur de distance est implicitement dans volumetricData si calculé correctement

    // Appliquer l'extinction (transmission)
    // Note: L'extinction devrait idéalement être intégrée le long du rayon vue,
    // mais pour un sprite plat, on peut approximer avec la valeur au point du sprite.
    vec3 attenuatedColor = spriteColor.rgb * (1.0 - extinction * u_volumetricIntensity); // Approximation simple

    // Ajouter l'in-scattering (lumière ajoutée par le volume)
    vec3 finalColor = attenuatedColor + inScattering * u_volumetricScattering * u_volumetricIntensity;

    // Sortir la couleur finale avec l'alpha original
    FragColor = vec4(finalColor, spriteColor.a);

    // Alternative: Mélange additif simple (moins réaliste)
    // FragColor = vec4(spriteColor.rgb + inScattering * u_volumetricIntensity, spriteColor.a);

    // Alternative: Utiliser l'extinction comme un brouillard basé sur la densité
    // float fogFactor = exp(-extinction * v_ViewPos.z * u_volumetricIntensity); // v_ViewPos.z est négatif
    // vec3 fogColor = inScattering / max(extinction, 0.001); // Couleur approx du "brouillard"
    // vec3 finalColor = mix(fogColor, spriteColor.rgb, fogFactor);
    // FragColor = vec4(finalColor, spriteColor.a);
}