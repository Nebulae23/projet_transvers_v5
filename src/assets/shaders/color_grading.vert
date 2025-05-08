#version 330

// Standard vertex attributes
uniform mat4 p3d_ModelViewProjectionMatrix;
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;

// Output to fragment shader
out vec2 texcoord;

void main() {
    // Transform vertex position
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    
    // Pass texture coordinates to fragment shader
    texcoord = p3d_MultiTexCoord0;
}
            