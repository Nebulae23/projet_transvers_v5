#version 330

// Input from vertex shader
in vec2 texcoord;

// Texture samplers
uniform sampler2D p3d_Texture0;  // Scene texture
uniform sampler2D depth_texture;  // Depth texture

// Tilt-shift parameters
uniform float blur_amount;        // Amount of blur
uniform float focus_width;        // Width of focused area
uniform float focus_position;     // Y position of focused area (0-1)
uniform int samples;              // Number of blur samples

// Output color
out vec4 fragColor;

// Tilt-shift blur function
vec4 tiltShiftBlur() {
    // Initialize with center texel
    vec4 color = texture(p3d_Texture0, texcoord);
    float total = 1.0;
    
    // Calculate distance from focus position (normalized 0-1)
    float distance = abs(texcoord.y - focus_position);
    
    // Calculate blur factor based on distance from focus
    float blur_factor = smoothstep(0.0, focus_width, distance) * blur_amount;
    
    // If no blur needed, return original color
    if (blur_factor < 0.01) return color;
    
    // Apply blur based on distance from focus zone
    float dx = blur_factor / float(textureSize(p3d_Texture0, 0).x);
    float dy = blur_factor / float(textureSize(p3d_Texture0, 0).y);
    
    // Perform blur sampling
    for (int i = 1; i <= samples; i++) {
        float weight = float(samples + 1 - i) / float(samples);
        float offset = float(i) * 2.0;
        
        // Sample in four directions
        color += texture(p3d_Texture0, texcoord + vec2(dx * offset, 0.0)) * weight;
        color += texture(p3d_Texture0, texcoord - vec2(dx * offset, 0.0)) * weight;
        color += texture(p3d_Texture0, texcoord + vec2(0.0, dy * offset)) * weight;
        color += texture(p3d_Texture0, texcoord - vec2(0.0, dy * offset)) * weight;
        
        total += weight * 4.0;
    }
    
    // Normalize result
    return color / total;
}

void main() {
    // Apply tilt-shift blur
    fragColor = tiltShiftBlur();
    
    // Optional: Apply vignette effect for more diorama feel
    float vignette = 1.0 - smoothstep(0.5, 1.2, length(texcoord - vec2(0.5)));
    fragColor.rgb *= mix(1.0, vignette, 0.3);
}
            