#version 330 core

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
}