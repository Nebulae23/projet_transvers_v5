#version 450 core

out vec4 FragColor;

in vec2 TexCoords;

uniform sampler2D hdrBuffer; // Le framebuffer contenant les couleurs HDR
uniform float exposure;      // Contrôle de l'exposition
uniform float gamma = 2.2;   // Correction Gamma

// Tone mapping ACES Filmic (approximation)
// Source: https://knarkowicz.wordpress.com/2016/01/06/aces-filmic-tone-mapping-curve/
vec3 ACESFilmicToneMapping(vec3 color)
{
    color *= exposure;
    color = (color * (2.51 * color + 0.03)) / (color * (2.43 * color + 0.59) + 0.14);
    return pow(color, vec3(1.0 / gamma)); // Appliquer la correction gamma ici
}

// Tone mapping Reinhard simple
vec3 ReinhardToneMapping(vec3 color)
{
    color *= exposure;
    color = color / (color + vec3(1.0));
    return pow(color, vec3(1.0 / gamma)); // Appliquer la correction gamma ici
}


void main()
{
    // Récupérer la couleur HDR depuis le buffer
    vec3 hdrColor = texture(hdrBuffer, TexCoords).rgb;

    // Appliquer le tone mapping (choisir l'un ou l'autre)
    vec3 mappedColor = ACESFilmicToneMapping(hdrColor);
    // vec3 mappedColor = ReinhardToneMapping(hdrColor);

    // Le gamma est déjà appliqué dans les fonctions de tone mapping ci-dessus

    FragColor = vec4(mappedColor, 1.0);
}