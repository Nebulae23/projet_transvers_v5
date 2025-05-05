#version 450 core

out vec4 FragColor;

in vec2 TexCoords;

uniform sampler2D spriteTexture;
uniform vec4 spriteColor; // Couleur de teinte (multipliée) et alpha global

void main()
{
    // Échantillonner la texture du sprite
    vec4 texColor = texture(spriteTexture, TexCoords);

    // Si le pixel de la texture est presque transparent, le rejeter
    // (Seuil alpha pour éviter les artefacts sur les bords)
    if(texColor.a < 0.1)
        discard; // Ne pas dessiner ce fragment

    // Appliquer la couleur de teinte et l'alpha global
    FragColor = texColor * spriteColor;

    // Alternative : utiliser l'alpha de la texture et l'alpha global
    // FragColor = vec4(texColor.rgb * spriteColor.rgb, texColor.a * spriteColor.a);
}