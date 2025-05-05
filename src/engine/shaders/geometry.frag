#version 330 core

// Input from vertex shader
in vec3 FragPos;
in vec3 Normal;
in vec2 TexCoord;

// Output
out vec4 FragColor;

// Material parameters
uniform sampler2D diffuseTexture;
uniform sampler2D normalMap;
uniform sampler2D roughnessMap;
uniform sampler2D metalnessMap;
uniform sampler2D aoMap;

// Lighting parameters
uniform vec3 lightPosition;
uniform vec3 lightColor;
uniform vec3 ambientColor;
uniform vec3 viewPosition;

// PBR parameters
uniform float roughnessFactor = 0.5;
uniform float metalnessFactor = 0.0;
uniform float aoFactor = 1.0;

// Constants
const float PI = 3.14159265359;

// Function to calculate normal distribution
float DistributionGGX(vec3 N, vec3 H, float roughness)
{
    float a = roughness*roughness;
    float a2 = a*a;
    float NdotH = max(dot(N, H), 0.0);
    float NdotH2 = NdotH*NdotH;
    
    float num = a2;
    float denom = (NdotH2 * (a2 - 1.0) + 1.0);
    denom = PI * denom * denom;
    
    return num / denom;
}

// Function to calculate geometry function
float GeometrySchlickGGX(float NdotV, float roughness)
{
    float r = (roughness + 1.0);
    float k = (r*r) / 8.0;

    float num = NdotV;
    float denom = NdotV * (1.0 - k) + k;
    
    return num / denom;
}

// Function to calculate combined geometry function
float GeometrySmith(vec3 N, vec3 V, vec3 L, float roughness)
{
    float NdotV = max(dot(N, V), 0.0);
    float NdotL = max(dot(N, L), 0.0);
    float ggx2 = GeometrySchlickGGX(NdotV, roughness);
    float ggx1 = GeometrySchlickGGX(NdotL, roughness);
    
    return ggx1 * ggx2;
}

// Function to calculate Fresnel equation
vec3 FresnelSchlick(float cosTheta, vec3 F0)
{
    return F0 + (1.0 - F0) * pow(1.0 - cosTheta, 5.0);
}

void main()
{
    // Sample textures
    vec4 diffuse = texture(diffuseTexture, TexCoord);
    
    // Early discard for fully transparent pixels
    if (diffuse.a < 0.1)
        discard;
        
    // Get material properties
    vec3 albedo = diffuse.rgb;
    float roughness = roughnessFactor;
    float metalness = metalnessFactor;
    float ao = aoFactor;
    
    // Try to sample additional textures if available
    if (textureSize(roughnessMap, 0).x > 1)
        roughness = texture(roughnessMap, TexCoord).r;
    if (textureSize(metalnessMap, 0).x > 1)
        metalness = texture(metalnessMap, TexCoord).r;
    if (textureSize(aoMap, 0).x > 1)
        ao = texture(aoMap, TexCoord).r;
        
    // Normalize normal
    vec3 N = normalize(Normal);
    
    // Try to sample normal map if available
    if (textureSize(normalMap, 0).x > 1) {
        // Calculate tangent space
        vec3 Q1 = dFdx(FragPos);
        vec3 Q2 = dFdy(FragPos);
        vec2 st1 = dFdx(TexCoord);
        vec2 st2 = dFdy(TexCoord);
        
        vec3 T = normalize(Q1 * st2.y - Q2 * st1.y);
        vec3 B = -normalize(cross(N, T));
        mat3 TBN = mat3(T, B, N);
        
        // Sample normal map and transform to world space
        vec3 normalSample = texture(normalMap, TexCoord).rgb * 2.0 - 1.0;
        N = normalize(TBN * normalSample);
    }
    
    // Calculate view direction
    vec3 V = normalize(viewPosition - FragPos);
    
    // Calculate reflectance at normal incidence
    vec3 F0 = vec3(0.04); 
    F0 = mix(F0, albedo, metalness);
    
    // Reflectance equation
    vec3 Lo = vec3(0.0);
    
    // Calculate per-light radiance
    vec3 L = normalize(lightPosition - FragPos);
    vec3 H = normalize(V + L);
    float distance = length(lightPosition - FragPos);
    float attenuation = 1.0 / (1.0 + 0.09 * distance + 0.032 * (distance * distance));
    vec3 radiance = lightColor * attenuation;
    
    // Cook-Torrance BRDF
    float NDF = DistributionGGX(N, H, roughness);
    float G = GeometrySmith(N, V, L, roughness);
    vec3 F = FresnelSchlick(max(dot(H, V), 0.0), F0);
    
    vec3 kS = F;
    vec3 kD = vec3(1.0) - kS;
    kD *= 1.0 - metalness;
    
    vec3 numerator = NDF * G * F;
    float denominator = 4.0 * max(dot(N, V), 0.0) * max(dot(N, L), 0.0);
    vec3 specular = numerator / max(denominator, 0.001);
    
    // Add to outgoing radiance Lo
    float NdotL = max(dot(N, L), 0.0);
    Lo += (kD * albedo / PI + specular) * radiance * NdotL;
    
    // Ambient lighting
    vec3 ambient = ambientColor * albedo * ao;
    
    // Final color
    vec3 color = ambient + Lo;
    
    // HDR tonemapping
    color = color / (color + vec3(1.0));
    
    // Gamma correction
    color = pow(color, vec3(1.0/2.2)); 
    
    // Output final color
    FragColor = vec4(color, diffuse.a);
}