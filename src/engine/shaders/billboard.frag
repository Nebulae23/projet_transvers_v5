#version 330 core

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
} 