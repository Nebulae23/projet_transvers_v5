#version 450 core

out vec4 FragColor;

in vec3 viewDirection; // Direction du rayon de vue depuis la caméra (espace monde)

// Paramètres de l'atmosphère
uniform vec3 cameraPos;        // Position de la caméra (espace monde)
uniform float planetRadius = 6371e3; // Rayon de la planète (Terre)
uniform float atmosphereHeight = 80e3; // Hauteur de l'atmosphère pertinente
uniform vec3 sunDirection;     // Direction normalisée vers le soleil
uniform vec3 sunIntensity = vec3(20.0); // Intensité du soleil

// Coefficients de diffusion (pré-calculés ou ajustés)
uniform vec3 betaRayleigh = vec3(5.8e-6, 13.5e-6, 33.1e-6); // Pour R, G, B
uniform float betaMie = 21e-6;
uniform float rayleighScaleHeight = 8e3; // Hauteur d'échelle pour Rayleigh
uniform float mieScaleHeight = 1.2e3;   // Hauteur d'échelle pour Mie
uniform float mieAnisotropy = 0.76;     // Anisotropie de Mie (diffusion vers l'avant)

const int NUM_SAMPLES = 16; // Nombre d'échantillons le long du rayon
const int NUM_LIGHT_SAMPLES = 8; // Nombre d'échantillons pour la lumière

const float PI = 3.1415926535;

// Fonction de phase Henyey-Greenstein
float phaseFunctionMie(float cosTheta, float g) {
    float g2 = g * g;
    return (1.0 - g2) / (4.0 * PI * pow(1.0 + g2 - 2.0 * g * cosTheta, 1.5));
}

// Fonction de phase Rayleigh (isotrope)
float phaseFunctionRayleigh(float cosTheta) {
    return 3.0 / (16.0 * PI) * (1.0 + cosTheta * cosTheta);
}

// Fonction pour calculer l'intersection rayon-sphère
// Retourne la distance à l'intersection la plus proche, ou -1.0 si pas d'intersection
float intersectRaySphere(vec3 rayOrigin, vec3 rayDir, float sphereRadius) {
    float a = dot(rayDir, rayDir);
    float b = 2.0 * dot(rayOrigin, rayDir);
    float c = dot(rayOrigin, rayOrigin) - sphereRadius * sphereRadius;
    float discriminant = b * b - 4.0 * a * c;
    if (discriminant < 0.0) {
        return -1.0;
    }
    float t0 = (-b - sqrt(discriminant)) / (2.0 * a);
    float t1 = (-b + sqrt(discriminant)) / (2.0 * a);
    // Retourne l'intersection la plus proche devant l'origine du rayon
    if (t0 > 0.0) return t0;
    if (t1 > 0.0) return t1;
    return -1.0;
}


void main()
{
    vec3 rayDir = normalize(viewDirection);
    vec3 rayOrigin = cameraPos;

    // Calculer l'intersection du rayon de vue avec la sphère de l'atmosphère
    float atmosphereRadius = planetRadius + atmosphereHeight;
    float distToAtmosphere = intersectRaySphere(rayOrigin, rayDir, atmosphereRadius);

    // Si le rayon ne touche pas l'atmosphère (regarde vers l'espace), couleur noire
    if (distToAtmosphere < 0.0) {
        FragColor = vec4(0.0, 0.0, 0.0, 1.0);
        return;
    }

    // Calculer l'intersection avec la planète (pour déterminer si le rayon touche le sol)
    float distToPlanet = intersectRaySphere(rayOrigin, rayDir, planetRadius);

    // Déterminer la distance maximale du ray marching
    float maxDist = distToAtmosphere;
    if (distToPlanet > 0.0) {
        maxDist = min(maxDist, distToPlanet);
    }

    // Ray marching pour calculer la lumière diffusée
    float stepSize = maxDist / float(NUM_SAMPLES);
    vec3 totalRayleigh = vec3(0.0);
    vec3 totalMie = vec3(0.0);
    float opticalDepth = 0.0; // Transmittance accumulée le long du rayon de vue

    for (int i = 0; i < NUM_SAMPLES; ++i) {
        // Position de l'échantillon le long du rayon
        float currentDist = float(i) * stepSize + stepSize * 0.5; // Milieu du segment
        vec3 samplePos = rayOrigin + rayDir * currentDist;
        float height = length(samplePos) - planetRadius; // Hauteur au-dessus du sol

        // Si l'échantillon est sous le sol ou trop haut, l'ignorer
        if (height < 0.0 || height > atmosphereHeight) continue;

        // Calculer la densité optique à cette hauteur pour Rayleigh et Mie
        float densityRayleigh = exp(-height / rayleighScaleHeight);
        float densityMie = exp(-height / mieScaleHeight);
        vec3 currentOpticalDepth = (betaRayleigh * densityRayleigh + betaMie * densityMie) * stepSize;

        // Calculer la transmittance jusqu'à ce point
        float transmittance = exp(-opticalDepth);

        // Calculer la lumière incidente à ce point (ray marching vers le soleil)
        float lightStepSize = intersectRaySphere(samplePos, sunDirection, atmosphereRadius) / float(NUM_LIGHT_SAMPLES);
        float lightOpticalDepth = 0.0;
        for (int j = 0; j < NUM_LIGHT_SAMPLES; ++j) {
            vec3 lightSamplePos = samplePos + sunDirection * (float(j) * lightStepSize + lightStepSize * 0.5);
            float lightHeight = length(lightSamplePos) - planetRadius;
            if (lightHeight > 0.0 && lightHeight < atmosphereHeight) {
                lightOpticalDepth += (betaRayleigh * exp(-lightHeight / rayleighScaleHeight) +
                                      betaMie * exp(-lightHeight / mieScaleHeight)) * lightStepSize;
            }
        }
        vec3 lightTransmittance = exp(-lightOpticalDepth);

        // Calculer la diffusion à ce point
        float cosTheta = dot(rayDir, sunDirection);
        totalRayleigh += transmittance * densityRayleigh * phaseFunctionRayleigh(cosTheta) * lightTransmittance * stepSize;
        totalMie += transmittance * densityMie * phaseFunctionMie(cosTheta, mieAnisotropy) * lightTransmittance * stepSize;

        // Accumuler la profondeur optique pour le prochain pas
        opticalDepth += currentOpticalDepth.x; // Utiliser une composante (approximation)
    }

    // Combiner les contributions Rayleigh et Mie
    vec3 finalColor = sunIntensity * (totalRayleigh * betaRayleigh + totalMie * betaMie);

    // Optionnel: Ajouter le soleil lui-même s'il est visible
    float sunDot = dot(rayDir, sunDirection);
    if (sunDot > 0.999) { // Si on regarde presque directement le soleil
       finalColor += sunIntensity * exp(-opticalDepth) * 10.0; // Rendre le disque solaire très brillant
    }

    // Tone mapping simple pour éviter la saturation
    finalColor = finalColor / (finalColor + vec3(1.0));
    // Correction Gamma
    finalColor = pow(finalColor, vec3(1.0/2.2));

    FragColor = vec4(finalColor, 1.0);
}