#version 330 core
out vec4 FragColor;

in vec2 TexCoord;

uniform sampler2D auraTexture; // Texture pour l'aura ou l'effet lumineux
uniform vec3 healColor = vec3(0.7, 1.0, 0.7); // Couleur verdâtre/blanche typique du soin
uniform float time; // Pour animation douce

void main()
{
    // TODO: Implémenter la logique du shader pour l'effet de soin
    // Exemple: texture d'aura douce avec pulsation de couleur/intensité

    vec4 texColor = texture(auraTexture, TexCoord);

    // Effet de pulsation douce de l'intensité
    float intensity = 0.8 + 0.2 * abs(sin(time * 1.5)); // Pulsation douce

    // Calculer la distance du centre pour un effet de fondu radial
    float dist = distance(TexCoord, vec2(0.5));
    float radialFade = 1.0 - smoothstep(0.3, 0.5, dist); // Fondu vers les bords

    // Combiner la couleur, la texture, l'intensité et le fondu
    vec3 finalColor = healColor * texColor.rgb * intensity;
    float finalAlpha = texColor.a * radialFade * intensity;

    if (finalAlpha < 0.05) discard; // Optimisation: ne pas dessiner les pixels quasi transparents

    FragColor = vec4(finalColor, finalAlpha);
}