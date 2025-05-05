#version 450 core

layout (location = 0) in vec2 aPos;      // Position du coin du quad (0,0), (1,0), (0,1), (1,1)
layout (location = 1) in vec2 aTexCoords; // Coordonnées de texture correspondantes

out vec2 TexCoords;

// Uniforms pour positionner et orienter le sprite dans l'espace monde/vue
uniform mat4 model;       // Transformation du sprite (position, rotation, échelle)
uniform mat4 view;        // Matrice de vue de la caméra
uniform mat4 projection;  // Matrice de projection (perspective ou ortho)

// Uniforms spécifiques au sprite
uniform vec2 spriteSize; // Taille du sprite en unités (pixels ou unités monde)
uniform vec2 uvOffset;   // Décalage UV pour l'animation de spritesheet
uniform vec2 uvScale;    // Échelle UV pour l'animation de spritesheet

void main()
{
    // Calculer la position du vertex dans l'espace local du sprite
    // aPos va de (0,0) à (1,1), on le met à l'échelle de spriteSize
    // et on le centre potentiellement si l'origine est au centre (optionnel)
    vec2 vertexPos = aPos * spriteSize; // Simple mise à l'échelle

    // Appliquer la transformation modèle (position, rotation, échelle du sprite)
    // On utilise vec4 car model est une mat4
    vec4 worldPos = model * vec4(vertexPos, 0.0, 1.0);

    // Transformer en espace écran
    gl_Position = projection * view * worldPos;

    // Passer les coordonnées de texture modifiées pour l'animation
    TexCoords = aTexCoords * uvScale + uvOffset;
}