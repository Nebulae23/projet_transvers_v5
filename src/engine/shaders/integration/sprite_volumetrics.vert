#version 330 core

// Attributs de sommet
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec2 aTexCoords;

// Matrices
uniform mat4 u_modelMatrix;
uniform mat4 u_viewMatrix;
uniform mat4 u_projectionMatrix;

// Sorties vers le Fragment Shader
out vec2 v_TexCoords;       // Coordonnées de texture
out vec3 v_WorldPos;        // Position dans l'espace monde
out vec4 v_ViewPos;         // Position dans l'espace vue (utile pour échantillonner les volumes 3D)
out vec4 v_ClipPos;         // Position en espace clip (utile pour échantillonner les volumes en espace écran)

void main()
{
    // Position en espace monde
    vec4 worldPos = u_modelMatrix * vec4(aPos, 1.0);
    v_WorldPos = worldPos.xyz;

    // Position en espace vue
    v_ViewPos = u_viewMatrix * worldPos;

    // Position finale en espace clip
    v_ClipPos = u_projectionMatrix * v_ViewPos;
    gl_Position = v_ClipPos;

    // Passer les coordonnées de texture
    v_TexCoords = aTexCoords;
}