#version 450 core

layout (location = 0) in vec3 aPos;

uniform mat4 lightSpaceMatrix; // Matrice combinée projection * vue depuis la lumière
uniform mat4 model;            // Matrice de transformation du modèle

void main()
{
    // Transformer la position du vertex en espace lumière
    // Le résultat sera utilisé implicitement par OpenGL pour le test de profondeur
    gl_Position = lightSpaceMatrix * model * vec4(aPos, 1.0);
}