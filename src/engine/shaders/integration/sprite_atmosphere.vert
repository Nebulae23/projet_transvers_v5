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
out float v_ViewDepth;      // Profondeur en espace vue (distance à la caméra)
// Optionnel: Position en espace clip pour certains calculs de brouillard écran
// out vec4 v_ClipPos;

void main()
{
    // Position en espace monde
    vec4 worldPos = u_modelMatrix * vec4(aPos, 1.0);
    v_WorldPos = worldPos.xyz;

    // Position en espace vue
    vec4 viewPos = u_viewMatrix * worldPos;
    // La profondeur est la coordonnée Z négative en espace vue (convention OpenGL)
    v_ViewDepth = -viewPos.z;

    // Position finale en espace clip
    gl_Position = u_projectionMatrix * viewPos;
    // v_ClipPos = gl_Position; // Si nécessaire pour brouillard écran

    // Passer les coordonnées de texture
    v_TexCoords = aTexCoords;
}