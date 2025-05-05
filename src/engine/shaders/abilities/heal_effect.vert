#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec2 aTexCoord;

out vec2 TexCoord;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform float time; // Pour animation (ex: expansion douce)

void main()
{
    // TODO: Ajouter une animation d'expansion ou de pulsation si désiré
    float scale = 1.0 + sin(time * 2.0) * 0.05; // Légère pulsation
    vec3 scaledPos = aPos * scale;

    gl_Position = projection * view * model * vec4(scaledPos, 1.0);
    TexCoord = aTexCoord;
}