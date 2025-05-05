#version 330 core
out vec4 FragColor;

in vec2 TexCoord;
in float TimeFrag; // Temps reçu du vertex shader

uniform sampler2D portalTexture; // Texture pour l'effet de portail ou spectral
uniform vec3 summonColor = vec3(0.8, 0.2, 1.0); // Couleur violette/spectrale
uniform float time; // Temps global (peut être différent de TimeFrag si besoin)

void main()
{
    // TODO: Implémenter la logique du shader pour l'effet d'invocation
    // Exemple: texture de portail animée avec distorsion et couleurs spectrales

    // Distorsion des coordonnées de texture basée sur le temps pour un effet ondulant/instable
    vec2 distortedTexCoord = TexCoord + vec2(
        sin(TexCoord.y * 8.0 + TimeFrag * 3.0) * 0.03,
        cos(TexCoord.x * 8.0 + TimeFrag * 2.5) * 0.03
    );
    vec4 texColor = texture(portalTexture, distortedTexCoord);

    // Effet de "flickering" ou de variation d'intensité
    float intensity = 0.6 + 0.4 * abs(sin(TimeFrag * 5.0 + TexCoord.x * 10.0));

    // Combiner la couleur spectrale, la texture et l'intensité
    vec3 finalColor = summonColor * texColor.rgb * intensity;

    // Ajouter un contour ou un halo basé sur la distance au bord de la texture
    float edgeFactor = smoothstep(0.0, 0.1, texColor.a) * (1.0 - smoothstep(0.9, 1.0, texColor.a));
    finalColor += summonColor * edgeFactor * 0.5; // Léger halo de la couleur d'invocation

    float finalAlpha = texColor.a * intensity;
    if (finalAlpha < 0.1) discard;

    FragColor = vec4(finalColor, finalAlpha);
}