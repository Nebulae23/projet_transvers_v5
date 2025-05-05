#version 330 core
out vec4 FragColor;

in vec2 TexCoord;
in vec3 VertexColor; // Couleur venant du vertex shader

uniform sampler2D texture1; // Texture pour l'effet (ex: rune, particule)
uniform vec3 effectColor;   // Couleur principale de l'effet
uniform float time;         // Pour animation

void main()
{
    // TODO: Implémenter la logique du shader pour l'effet magique
    // Exemple: combiner texture, couleur de vertex, et animation temporelle

    vec4 texColor = texture(texture1, TexCoord);

    // Utiliser la couleur du vertex si disponible, sinon la couleur uniforme
    vec3 baseColor = VertexColor.r > 0.0 || VertexColor.g > 0.0 || VertexColor.b > 0.0 ? VertexColor : effectColor;

    // Effet de pulsation ou de scintillement
    float intensity = 0.7 + 0.3 * sin(TexCoord.x * 10.0 + TexCoord.y * 5.0 + time * 4.0);

    // Combiner la couleur de base, la texture et l'intensité
    vec3 finalColor = baseColor * texColor.rgb * intensity;

    // Ajouter un effet de "glow" simple basé sur la distance au centre (si pertinent)
    // float dist = distance(TexCoord, vec2(0.5));
    // finalColor += baseColor * (1.0 - smoothstep(0.0, 0.5, dist)) * 0.5;

    // Assurer une certaine transparence basée sur la texture alpha
    float alpha = texColor.a;
    if (alpha < 0.1) discard; // Ne pas dessiner les pixels trop transparents

    FragColor = vec4(finalColor, alpha);
}