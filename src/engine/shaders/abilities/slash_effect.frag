#version 330 core
out vec4 FragColor;

in vec2 TexCoord;

uniform sampler2D texture1;
uniform float time; // Pour animer l'effet

void main()
{
    // TODO: Implémenter la logique du shader pour l'effet de coup
    // Exemple simple: texture animée ou distorsion
    vec2 distortedTexCoord = TexCoord + vec2(sin(TexCoord.y * 10.0 + time * 5.0) * 0.05, 0.0);
    vec4 texColor = texture(texture1, distortedTexCoord);

    // Effet de "flash" basé sur le temps ou une autre variable
    float intensity = smoothstep(0.0, 0.2, sin(time * 10.0)) * 0.5 + 0.5; // Varie l'intensité

    // Simuler un effet de lame brillante/métallique
    if (texColor.a > 0.1) { // Seulement si le pixel n'est pas transparent
        FragColor = vec4(texColor.rgb * intensity * vec3(1.5, 1.5, 2.0), texColor.a); // Teinte bleutée brillante
    } else {
        discard; // Ne pas dessiner les pixels transparents
    }
}