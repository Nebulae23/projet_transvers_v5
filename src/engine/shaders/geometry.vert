#version 330 core

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
}