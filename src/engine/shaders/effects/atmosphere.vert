#version 450 core

layout (location = 0) in vec3 aPos; // Position du vertex (quad plein écran ou skybox)

out vec3 viewDirection; // Direction du rayon de vue depuis la caméra (non normalisée)

uniform mat4 invProjectionMatrix; // Inverse de la matrice de projection
uniform mat4 invViewMatrix;       // Inverse de la matrice de vue

void main()
{
    // Pour un quad plein écran, aPos est en NDC [-1, 1]
    // Pour un skybox, aPos est la position du vertex du cube

    // Calculer la direction du rayon de vue dans l'espace monde
    // 1. Transformer la position NDC en espace caméra (vue)
    vec4 viewPos = invProjectionMatrix * vec4(aPos, 1.0);
    // 2. Mettre w à 0 pour obtenir une direction, puis transformer en espace monde
    viewDirection = vec3(invViewMatrix * vec4(viewPos.xyz / viewPos.w, 0.0));

    // Positionner le vertex à la distance maximale (z=1 en NDC) pour qu'il soit derrière tout
    // Cela assure que le ciel est toujours dessiné en arrière-plan.
    gl_Position = vec4(aPos.xy, 1.0, 1.0); // z=1, w=1
}