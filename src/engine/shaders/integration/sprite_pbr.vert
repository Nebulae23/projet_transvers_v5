#version 330 core

// Attributs de sommet (depuis le VBO)
layout (location = 0) in vec3 aPos;      // Position locale du sommet du sprite (ex: -0.5 à 0.5)
layout (location = 1) in vec2 aTexCoords; // Coordonnées de texture (UV)

// Matrices de transformation (Uniforms)
uniform mat4 u_modelMatrix;       // Matrice pour placer/orienter/mettre à l'échelle le sprite dans le monde
uniform mat4 u_viewMatrix;        // Matrice de la caméra
uniform mat4 u_projectionMatrix;  // Matrice de projection de la caméra

// Sorties vers le Fragment Shader
out vec2 v_TexCoords;       // Coordonnées de texture interpolées
out vec3 v_WorldPos;        // Position du fragment dans l'espace monde
out vec3 v_Normal;          // Normale du fragment dans l'espace monde (peut être constante pour les sprites)
// Optionnel: Position en espace vue pour certains calculs d'éclairage/effets
// out vec3 v_ViewPos;

void main()
{
    // Calculer la position du sommet dans l'espace monde
    vec4 worldPos = u_modelMatrix * vec4(aPos, 1.0);
    v_WorldPos = worldPos.xyz;

    // Calculer la position finale du sommet dans l'espace clip (écran)
    gl_Position = u_projectionMatrix * u_viewMatrix * worldPos;

    // Passer les coordonnées de texture au fragment shader
    v_TexCoords = aTexCoords;

    // Calculer la normale dans l'espace monde
    // Pour un sprite simple face à la caméra, la normale pourrait être calculée
    // pour toujours faire face à la caméra, ou être une constante (ex: Z+ monde).
    // Ici, on suppose une normale constante pointant vers Z+ dans l'espace modèle,
    // puis transformée en espace monde.
    // mat3 normalMatrix = transpose(inverse(mat3(u_modelMatrix))); // Correct mais coûteux
    mat3 normalMatrix = mat3(u_modelMatrix); // Approximation si pas de mise à l'échelle non uniforme
    vec3 modelNormal = vec3(0.0, 0.0, 1.0); // Normale locale (sprite dans le plan XY)
    v_Normal = normalize(normalMatrix * modelNormal);

    // Optionnel: Calculer la position en espace vue
    // vec4 viewPos = u_viewMatrix * worldPos;
    // v_ViewPos = viewPos.xyz;
}