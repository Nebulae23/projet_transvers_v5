#version 330 core

// Entrées depuis le Vertex Shader
in vec2 v_TexCoords;   // Coordonnées de texture
in vec3 v_WorldPos;    // Position dans l'espace monde
in float v_ViewDepth;  // Profondeur en espace vue (distance caméra)

// Sortie
out vec4 FragColor;

// Texture du sprite
uniform sampler2D u_spriteTexture;
uniform vec4 u_baseColorFactor = vec4(1.0);

// Paramètres atmosphériques (brouillard simple)
uniform vec3 u_fogColor = vec3(0.5, 0.6, 0.7); // Couleur du brouillard
uniform float u_fogDensity = 0.02;            // Densité du brouillard (contrôle la rapidité de l'épaississement)
uniform float u_fogStartDistance = 10.0;      // Distance à partir de laquelle le brouillard commence
uniform float u_fogMaxDistance = 100.0;       // Distance à laquelle le brouillard est maximal (optionnel, pour clamp)

// Fonction de calcul du facteur de brouillard (exponentiel)
float calculateFogFactor(float distance) {
    // Option 1: Brouillard exponentiel simple
    // float fogFactor = exp(-u_fogDensity * distance);

    // Option 2: Brouillard exponentiel carré (plus dense)
    // float fogFactor = exp(-pow(u_fogDensity * distance, 2.0));

    // Option 3: Brouillard linéaire basé sur les distances start/max
    float fogRange = u_fogMaxDistance - u_fogStartDistance;
    float fogCoord = clamp((distance - u_fogStartDistance) / max(fogRange, 0.001), 0.0, 1.0);
    // Appliquer une courbe exponentielle au facteur linéaire pour un rendu plus naturel
    float fogFactor = exp(-u_fogDensity * fogCoord * fogCoord * 5.0); // Ajuster le * 5.0 pour la force

    return clamp(fogFactor, 0.0, 1.0);
}

void main()
{
    // Lire la couleur et l'alpha du sprite
    vec4 spriteColor = texture(u_spriteTexture, v_TexCoords) * u_baseColorFactor;

    // Alpha testing
    if (spriteColor.a < 0.1) {
        discard;
    }

    // Calculer le facteur de brouillard basé sur la profondeur en espace vue
    float fogFactor = calculateFogFactor(v_ViewDepth);

    // Mélanger la couleur du sprite avec la couleur du brouillard
    // Lerp(fogColor, spriteColor.rgb, fogFactor)
    vec3 finalColor = mix(u_fogColor, spriteColor.rgb, fogFactor);

    // Sortir la couleur finale avec l'alpha original du sprite
    FragColor = vec4(finalColor, spriteColor.a);

    // Alternative: Appliquer le brouillard aussi à l'alpha (moins courant)
    // FragColor = vec4(finalColor, spriteColor.a * fogFactor);
}