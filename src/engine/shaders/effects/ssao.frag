#version 450 core

out float FragColor; // Sortie : facteur d'occlusion (0.0 = occlus, 1.0 = non occlus)

in vec2 TexCoords;

// G-Buffer textures
uniform sampler2D gPosition; // Position dans l'espace vue
uniform sampler2D gNormal;   // Normale dans l'espace vue

// Texture de bruit pour la rotation aléatoire des échantillons
uniform sampler2D texNoise;

// Échantillons du noyau hémisphérique (passés via uniform)
uniform vec3 samples[64]; // 64 échantillons pré-calculés

// Paramètres SSAO
uniform int kernelSize = 64;
uniform float radius = 0.5;
uniform float bias = 0.025;
uniform float power = 1.0; // Pour accentuer l'effet

// Matrice de projection pour transformer les échantillons en espace écran
uniform mat4 projection;

// Taille de la texture de bruit (pour le tiling)
const vec2 noiseScale = vec2(1280.0/4.0, 720.0/4.0); // Supposons une résolution 1280x720 et une texture de bruit 4x4

void main()
{
    // Récupérer les données du G-buffer pour ce fragment
    vec3 fragPos = texture(gPosition, TexCoords).xyz;
    vec3 normal = normalize(texture(gNormal, TexCoords).rgb);

    // Obtenir un vecteur de rotation aléatoire depuis la texture de bruit
    vec3 randomVec = normalize(texture(texNoise, TexCoords * noiseScale).xyz);

    // Créer la matrice TBN pour orienter le noyau d'échantillonnage
    // Utilise la normale et le vecteur aléatoire comme tangente (Gram-Schmidt)
    vec3 tangent = normalize(randomVec - normal * dot(randomVec, normal));
    vec3 bitangent = cross(normal, tangent);
    mat3 TBN = mat3(tangent, bitangent, normal);

    // Calculer l'occlusion
    float occlusion = 0.0;
    for(int i = 0; i < kernelSize; ++i)
    {
        // Transformer l'échantillon du noyau de l'espace tangent vers l'espace vue
        vec3 samplePos = TBN * samples[i]; // Échantillon dans l'espace tangent
        samplePos = fragPos + samplePos * radius; // Position de l'échantillon dans l'espace vue

        // Projeter la position de l'échantillon sur l'écran
        vec4 offset = vec4(samplePos, 1.0);
        offset = projection * offset;      // Transformer en espace clip
        offset.xyz /= offset.w;            // Division perspective -> NDC [-1, 1]
        offset.xyz = offset.xyz * 0.5 + 0.5; // Transformer en coordonnées de texture [0, 1]

        // Obtenir la profondeur de l'échantillon depuis le G-buffer (position Z)
        // Note: Assurez-vous que gPosition stocke bien la profondeur linéaire dans l'espace vue
        float sampleDepth = texture(gPosition, offset.xy).z;

        // Comparer la profondeur de l'échantillon avec la profondeur stockée
        // 'samplePos.z' est la profondeur (distance) de l'échantillon dans l'espace vue
        // Ajouter un biais pour éviter l'auto-occlusion
        float rangeCheck = smoothstep(0.0, 1.0, radius / abs(fragPos.z - sampleDepth));
        occlusion += (sampleDepth >= samplePos.z + bias ? 1.0 : 0.0) * rangeCheck;
    }

    // Calculer le facteur d'occlusion final
    occlusion = 1.0 - (occlusion / float(kernelSize));
    FragColor = pow(occlusion, power); // Appliquer une puissance pour ajuster l'intensité
}