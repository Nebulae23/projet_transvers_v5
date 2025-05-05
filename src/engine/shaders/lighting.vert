#version 450 core

layout (location = 0) in vec3 aPos;
layout (location = 1) in vec2 aTexCoords;

out vec2 TexCoords;

void main()
{
    // Le quad de rendu prend tout l'écran, donc on passe directement les coordonnées de texture
    TexCoords = aTexCoords;
    // Les coordonnées du quad sont en NDC (-1 à 1), z=0 pour être toujours devant
    gl_Position = vec4(aPos.x, aPos.y, 0.0, 1.0);
}