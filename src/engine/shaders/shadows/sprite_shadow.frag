#version 450 core

in vec2 TexCoords;

uniform sampler2D spriteTexture;

// Ce shader est utilisé pour générer la shadow map pour les sprites.
// Il n'a pas besoin de sortie couleur, seulement d'écrire la profondeur
// et de rejeter les fragments transparents.

void main()
{
    // Échantillonner la texture du sprite
    float alpha = texture(spriteTexture, TexCoords).a;

    // Si le pixel du sprite est transparent ou quasi-transparent,
    // ne pas écrire dans la shadow map (le fragment est rejeté).
    if (alpha < 0.5) // Seuil ajustable
        discard;

    // Si le fragment n'est pas rejeté, sa profondeur (calculée dans le vertex shader
    // et interpolée) sera automatiquement écrite dans le depth buffer (la shadow map).
}