#version 450 core

layout (location = 0) in vec2 aPos;      // Position du coin du quad (0,0), (1,0), (0,1), (1,1)
layout (location = 1) in vec2 aTexCoords; // Coordonnées de texture

out vec2 TexCoords; // Passer les coordonnées de texture au fragment shader

// Uniforms pour positionner le sprite dans l'espace monde
uniform mat4 model;       // Transformation du sprite (position, rotation, échelle)

// Uniforms spécifiques au sprite
uniform vec2 spriteSize; // Taille du sprite
uniform vec2 uvOffset;   // Décalage UV pour l'animation
uniform vec2 uvScale;    // Échelle UV pour l'animation

// Matrice pour transformer de l'espace monde à l'espace lumière
uniform mat4 lightSpaceMatrix;

void main()
{
    // Calculer la position du vertex dans l'espace local du sprite
    vec2 vertexPos = aPos * spriteSize;

    // Appliquer la transformation modèle pour obtenir la position monde
    vec4 worldPos = model * vec4(vertexPos, 0.0, 1.0);

    // Transformer en espace lumière pour la shadow map
    gl_Position = lightSpaceMatrix * worldPos;

    // Passer les coordonnées de texture modifiées pour l'animation
    TexCoords = aTexCoords * uvScale + uvOffset;
}