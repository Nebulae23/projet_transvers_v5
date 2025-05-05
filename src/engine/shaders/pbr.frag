#version 330 core

// Input from vertex shader
in vec3 FragPos;
in vec2 TexCoord;
in vec3 Normal;
in mat3 TBN;

// Output
out vec4 FragColor;

// Material textures
uniform sampler2D diffuseTexture;
uniform sampler2D normalMap;
uniform sampler2D roughnessMap;
uniform sampler2D metalnessMap;
uniform sampler2D aoMap;
uniform sampler2D emissiveMap;

// Material properties
uniform vec3 albedoFactor = vec3(1.0);
uniform float roughnessFactor = 0.5;
uniform float metalnessFactor = 0.0;
uniform float aoFactor = 1.0;
uniform float emissiveFactor = 0.0;

// Lighting
uniform vec3 lightPositions[4];
uniform vec3 lightColors[4];
uniform int lightCount = 1;
uniform vec3 ambientLight = vec3(0.03);

// Camera
uniform vec3 camPos;

// Constants
const float PI = 3.14159265359;

// PBR functions
float DistributionGGX(vec3 N, vec3 H, float roughness)
{
    float a = roughness*roughness;
    float a2 = a*a;
    float NdotH = max(dot(N, H), 0.0);
    float NdotH2 = NdotH*NdotH;
    
    float nom   = a2;
    float denom = (NdotH2 * (a2 - 1.0) + 1.0);
    denom = PI * denom * denom;
    
    return nom / max(denom, 0.0000001);
}

float GeometrySchlickGGX(float NdotV, float roughness)
{
    float r = (roughness + 1.0);
    float k = (r*r) / 8.0;
    
    float nom   = NdotV;
    float denom = NdotV * (1.0 - k) + k;
    
    return nom / max(denom, 0.0000001);
}

float GeometrySmith(vec3 N, vec3 V, vec3 L, float roughness)
{
    float NdotV = max(dot(N, V), 0.0);
    float NdotL = max(dot(N, L), 0.0);
    float ggx2 = GeometrySchlickGGX(NdotV, roughness);
    float ggx1 = GeometrySchlickGGX(NdotL, roughness);
    
    return ggx1 * ggx2;
}

vec3 FresnelSchlick(float cosTheta, vec3 F0)
{
    return F0 + (1.0 - F0) * pow(max(1.0 - cosTheta, 0.0), 5.0);
}

void main()
{
    // Sample material textures
    vec4 albedoSample = texture(diffuseTexture, TexCoord);
    
    // Early alpha discard for transparent pixels
    if (albedoSample.a < 0.1)
        discard;
        
    // Material properties
    vec3 albedo = albedoSample.rgb * albedoFactor;
    float metalness = metalnessFactor;
    float roughness = roughnessFactor;
    float ao = aoFactor;
    
    // Sample optional material textures if available
    if (textureSize(roughnessMap, 0).x > 1)
        roughness = texture(roughnessMap, TexCoord).r * roughnessFactor;
        
    if (textureSize(metalnessMap, 0).x > 1)
        metalness = texture(metalnessMap, TexCoord).r * metalnessFactor;
        
    if (textureSize(aoMap, 0).x > 1)
        ao = texture(aoMap, TexCoord).r * aoFactor;
    
    // Calculate normal
    vec3 N = normalize(Normal);
    
    // Apply normal mapping if available
    if (textureSize(normalMap, 0).x > 1)
    {
        vec3 normalMapValue = texture(normalMap, TexCoord).rgb * 2.0 - 1.0;
        N = normalize(TBN * normalMapValue);
    }
    
    // View direction
    vec3 V = normalize(camPos - FragPos);
    
    // Calculate reflection at normal incidence based on metallicity
    vec3 F0 = vec3(0.04); 
    F0 = mix(F0, albedo, metalness);
    
    // Reflectance equation
    vec3 Lo = vec3(0.0);
    
    // Calculate lighting contribution
    for (int i = 0; i < lightCount; ++i)
    {
        // Per light calculation
        vec3 L = normalize(lightPositions[i] - FragPos);
        vec3 H = normalize(V + L);
        
        // Calculate light attenuation
        float distance = length(lightPositions[i] - FragPos);
        float attenuation = 1.0 / (1.0 + 0.09 * distance + 0.032 * distance * distance);
        vec3 radiance = lightColors[i] * attenuation;
        
        // Cook-Torrance BRDF
        float NDF = DistributionGGX(N, H, roughness);   
        float G   = GeometrySmith(N, V, L, roughness);    
        vec3 F    = FresnelSchlick(max(dot(H, V), 0.0), F0);
           
        // Calculate specular and diffuse components
        vec3 kS = F;
        vec3 kD = vec3(1.0) - kS;
        kD *= 1.0 - metalness;
        
        // Calculate specular term
        vec3 numerator    = NDF * G * F; 
        float denominator = 4.0 * max(dot(N, V), 0.0) * max(dot(N, L), 0.0) + 0.0001;
        vec3 specular = numerator / denominator;
        
        // Add contribution of this light
        float NdotL = max(dot(N, L), 0.0);
        Lo += (kD * albedo / PI + specular) * radiance * NdotL;
    }
    
    // Add ambient lighting
    vec3 ambient = ambientLight * albedo * ao;
    
    // Add emissive contribution
    vec3 emissive = vec3(0.0);
    if (textureSize(emissiveMap, 0).x > 1)
        emissive = texture(emissiveMap, TexCoord).rgb * emissiveFactor;
    
    // Combine all lighting components
    vec3 color = ambient + Lo + emissive;
    
    // Tone mapping (Reinhard operator)
    color = color / (color + vec3(1.0));
    
    // Gamma correction
    color = pow(color, vec3(1.0/2.2)); 
    
    // Set alpha from diffuse texture
    FragColor = vec4(color, albedoSample.a);
}