#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec2 aTexCoord; // Pour textures éventuelles
layout (location = 2) in vec3 aColor;    // Pour couleur par vertex (ex: particules)

out vec2 TexCoord;
out vec3 VertexColor;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform float time; // Pour animation basée sur le temps

void main()
{
    // TODO: Ajouter des déformations ou animations spécifiques à la magie si nécessaire
    // Exemple: faire onduler les vertices
    vec3 pos = aPos;
    pos.y += sin(aPos.x * 5.0 + time * 3.0) * 0.1;

    gl_Position = projection * view * model * vec4(pos, 1.0);
    TexCoord = aTexCoord;
    VertexColor = aColor; // Transmettre la couleur du vertex
}