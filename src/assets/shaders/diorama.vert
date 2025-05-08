#version 330

// Standard vertex attributes
uniform mat4 p3d_ModelViewProjectionMatrix;
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;

// Additional depth information
uniform float depth_offset;
uniform float depth_scale;

// Output to fragment shader
out vec2 texcoord;
out float depth_value;

void main() {
    // Transform vertex position
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    
    // Pass texture coordinates to fragment shader
    texcoord = p3d_MultiTexCoord0;
    
    // Calculate depth value for diorama effect
    // This scales the Z value to create the layered cardboard effect
    depth_value = (gl_Position.z / gl_Position.w) * depth_scale + depth_offset;
}
            