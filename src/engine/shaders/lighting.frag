#version 450 core

out vec4 FragColor;

in vec2 TexCoords;

uniform sampler2D gPosition;
uniform sampler2D gNormal;
uniform sampler2D gAlbedoSpec;

struct Light {
    vec3 Position;
    vec3 Color;
    float Linear;
    float Quadratic;
    float Intensity;
};
const int NR_LIGHTS = 32; // Nombre maximum de lumières
uniform Light lights[NR_LIGHTS];
uniform vec3 viewPos;
uniform int activeLights; // Nombre de lumières actives réellement utilisées

void main()
{
    // Récupérer les données du G-buffer
    vec3 FragPos = texture(gPosition, TexCoords).rgb;
    vec3 Normal = texture(gNormal, TexCoords).rgb;
    vec4 AlbedoSpec = texture(gAlbedoSpec, TexCoords);
    vec3 Albedo = AlbedoSpec.rgb;
    float SpecularStrength = AlbedoSpec.a;

    // Propriétés du matériau (simplifié pour l'instant)
    float Shininess = 32.0; // À terme, pourrait venir d'une texture ou d'un uniform

    // Calcul de l'éclairage
    vec3 lighting = Albedo * 0.1; // Lumière ambiante faible
    vec3 viewDir = normalize(viewPos - FragPos);

    for(int i = 0; i < activeLights; ++i)
    {
        // Atténuation
        float distance = length(lights[i].Position - FragPos);
        float attenuation = 1.0 / (1.0 + lights[i].Linear * distance + lights[i].Quadratic * (distance * distance));

        // Diffus
        vec3 lightDir = normalize(lights[i].Position - FragPos);
        float diff = max(dot(Normal, lightDir), 0.0);
        vec3 diffuse = lights[i].Color * diff * Albedo;

        // Spéculaire (Blinn-Phong)
        vec3 halfwayDir = normalize(lightDir + viewDir);
        float spec = pow(max(dot(Normal, halfwayDir), 0.0), Shininess);
        vec3 specular = lights[i].Color * spec * SpecularStrength;

        // Ajouter la contribution de la lumière
        lighting += (diffuse + specular) * attenuation * lights[i].Intensity;
    }

    FragColor = vec4(lighting, 1.0);
}