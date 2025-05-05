#version 450 core

// Ce shader n'a pas besoin de sortie couleur, car nous ne nous intéressons
// qu'à la valeur de profondeur qui est écrite automatiquement dans le depth buffer
// configuré comme texture de shadow map.

void main()
{
    // gl_FragDepth est écrit automatiquement par le pipeline de rastérisation
    // basé sur la valeur z de gl_Position calculée dans le vertex shader.
    // Aucune instruction n'est nécessaire ici.
}