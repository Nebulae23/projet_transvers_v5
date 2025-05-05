#version 330 core

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
} 