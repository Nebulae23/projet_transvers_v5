# src/engine/initialize_hd2d.py

import os
import shutil
import pygame
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import sys

# Default shader content
DEFAULT_SHADERS = {
    "billboard.vert": """#version 330 core

// Input vertex data
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec2 aTexCoord;

// Output to fragment shader
out vec2 TexCoord;

// Matrices
uniform mat4 model;
uniform mat4 viewProj;

// Camera position
uniform vec3 cameraPosition;

// Billboard settings
uniform bool verticalBillboard = true;  // If true, only rotate around Y axis (Octopath style)

void main()
{
    // Get the model position (center of the billboard)
    vec3 modelPos = vec3(model[3][0], model[3][1], model[3][2]);
    
    // Get the scaled billboard size
    vec3 scale;
    scale.x = length(vec3(model[0][0], model[0][1], model[0][2]));
    scale.y = length(vec3(model[1][0], model[1][1], model[1][2]));
    scale.z = length(vec3(model[2][0], model[2][1], model[2][2]));
    
    // Calculate billboard-to-camera direction
    vec3 cameraToBillboard = normalize(modelPos - cameraPosition);
    
    // Create a billboard orientation
    vec3 up = vec3(0.0, 1.0, 0.0);
    vec3 right;
    
    if (verticalBillboard) {
        // For Octopath style, only rotate around Y axis
        // This keeps characters upright but facing the camera horizontally
        right = normalize(cross(up, cameraToBillboard));
        cameraToBillboard = normalize(cross(right, up));
    } else {
        // For full billboarding
        right = normalize(cross(up, cameraToBillboard));
        up = normalize(cross(cameraToBillboard, right));
    }
    
    // Create the billboarded vertex position
    vec3 pos = modelPos;
    pos += right * aPos.x * scale.x;
    pos += up * aPos.y * scale.y;
    
    // Apply view projection
    gl_Position = viewProj * vec4(pos, 1.0);
    
    // Pass texture coordinates to fragment shader
    TexCoord = aTexCoord;
}""",
    "billboard.frag": """#version 330 core

// Input from vertex shader
in vec2 TexCoord;

// Output
out vec4 FragColor;

// Textures
uniform sampler2D spriteTexture;

void main()
{
    // Sample texture
    vec4 texColor = texture(spriteTexture, TexCoord);
    
    // Discard transparent pixels
    if (texColor.a < 0.1)
        discard;
        
    // Output final color
    FragColor = texColor;
}""",
    "geometry.vert": """#version 330 core

// Input vertex attributes
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;
layout (location = 2) in vec2 aTexCoord;

// Output to fragment shader
out vec3 FragPos;
out vec3 Normal;
out vec2 TexCoord;

// Matrices
uniform mat4 model;
uniform mat4 viewProj;

// Lighting
uniform vec3 lightPosition;
uniform vec3 viewPosition;

void main()
{
    // Calculate fragment position in world space
    FragPos = vec3(model * vec4(aPos, 1.0));
    
    // Transform normal to world space
    // Note: This assumes uniform scaling; for non-uniform scaling,
    // we would need to use the inverse transpose of the model matrix
    Normal = mat3(model) * aNormal;
    
    // Pass texture coordinates
    TexCoord = aTexCoord;
    
    // Output position in clip space
    gl_Position = viewProj * vec4(FragPos, 1.0);
}""",
    "geometry.frag": """#version 330 core

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
}""",
    "pbr.vert": """#version 330 core

// Input vertex attributes
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;
layout (location = 2) in vec2 aTexCoord;
layout (location = 3) in vec3 aTangent;
layout (location = 4) in vec3 aBitangent;

// Output to fragment shader
out vec3 FragPos;
out vec2 TexCoord;
out vec3 Normal;
out mat3 TBN;

// Matrices
uniform mat4 model;
uniform mat4 viewProj;

void main()
{
    // Calculate fragment position in world space
    FragPos = vec3(model * vec4(aPos, 1.0));
    
    // Pass texture coordinates to fragment shader
    TexCoord = aTexCoord;
    
    // Transform normal to world space
    mat3 normalMatrix = transpose(inverse(mat3(model)));
    Normal = normalize(normalMatrix * aNormal);
    
    // Calculate TBN matrix for normal mapping
    vec3 T = normalize(normalMatrix * aTangent);
    vec3 B = normalize(normalMatrix * aBitangent);
    TBN = mat3(T, B, Normal);
    
    // Calculate final position
    gl_Position = viewProj * vec4(FragPos, 1.0);
}""",
    "pbr.frag": """#version 330 core

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
}"""
}

def initialize_hd2d_system():
    """Initialize the HD-2D rendering system by setting up required directories and files."""
    print("Initializing HD-2D rendering system...")
    
    # Ensure shaders directory exists
    shader_dir = os.path.join("src", "engine", "shaders")
    os.makedirs(shader_dir, exist_ok=True)
    
    # Create default shaders if they don't exist
    for filename, content in DEFAULT_SHADERS.items():
        shader_path = os.path.join(shader_dir, filename)
        if not os.path.exists(shader_path):
            try:
                with open(shader_path, 'w') as f:
                    f.write(content)
                print(f"Created shader: {shader_path}")
            except Exception as e:
                print(f"Failed to create shader {shader_path}: {e}")
    
    # Ensure graphics directory exists
    graphics_dir = os.path.join("src", "engine", "graphics")
    os.makedirs(graphics_dir, exist_ok=True)
    
    # Create __init__.py for graphics directory
    init_file = os.path.join(graphics_dir, "__init__.py")
    if not os.path.exists(init_file):
        try:
            with open(init_file, "w") as f:
                f.write("# Graphics module for HD-2D rendering\n")
            print(f"Created: {init_file}")
        except Exception as e:
            print(f"Failed to create {init_file}: {e}")
    
    # Check for required PyOpenGL installation
    try:
        import OpenGL
        print(f"OpenGL library found: {OpenGL.__version__}")
    except ImportError:
        print("OpenGL library not found. Installing PyOpenGL...")
        
        # Try to install PyOpenGL using pip
        try:
            import pip
            pip.main(['install', 'PyOpenGL'])
            print("PyOpenGL installed successfully.")
        except Exception as e:
            print(f"Failed to install PyOpenGL: {e}")
            print("Please install PyOpenGL manually: pip install PyOpenGL")
    
    # Check for glm installation (needed for 3D math)
    try:
        import glm
        print(f"GLM library found")
    except ImportError:
        print("GLM library not found. Installing PyGLM...")
        
        # Try to install PyGLM using pip
        try:
            import pip
            pip.main(['install', 'PyGLM'])
            print("PyGLM installed successfully.")
        except Exception as e:
            print(f"Failed to install PyGLM: {e}")
            print("Please install PyGLM manually: pip install PyGLM")
    
    print("HD-2D rendering system initialization complete.")
    return True

if __name__ == "__main__":
    initialize_hd2d_system() 