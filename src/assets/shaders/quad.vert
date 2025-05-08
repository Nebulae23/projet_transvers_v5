#version 330

// Standard vertex attributes
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;

// Output to fragment shader
out vec2 texcoord;

void main() {
    // Pass texture coordinates to fragment shader
    texcoord = p3d_MultiTexCoord0;
    
    // Pass vertex position unchanged
    gl_Position = p3d_Vertex;
} 