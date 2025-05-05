#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec2 aTexCoord;

out vec2 TexCoord;
out float TimeFrag; // Transmettre le temps pour des effets temporels dans le fragment shader

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform float time; // Temps global

void main()
{
    // TODO: Ajouter des effets spécifiques à l'invocation (ex: distorsion, apparition)
    // Exemple: faire apparaître les vertices depuis le centre
    float appearFactor = smoothstep(0.0, 1.0, time); // Simple apparition linéaire sur 1 seconde
    vec3 pos = aPos * appearFactor;

    gl_Position = projection * view * model * vec4(pos, 1.0);
    TexCoord = aTexCoord;
    TimeFrag = time; // Passer le temps au fragment shader
}