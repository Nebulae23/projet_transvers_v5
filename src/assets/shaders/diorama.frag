#version 330

// Input from vertex shader
in vec2 texcoord;
in float depth_value;

// Texture samplers
uniform sampler2D p3d_Texture0;  // Diffuse texture
uniform sampler2D depth_texture;  // Depth texture (optional)
uniform sampler2D normal_texture; // Normal map (optional)

// Lighting parameters
uniform vec3 light_direction;
uniform vec3 light_color;
uniform float ambient_intensity;
uniform float depth_contrast;
uniform float edge_strength;

// Output color
out vec4 fragColor;

// Functions for edge detection
float getEdgeFactor(vec2 uv, float depth) {
    // Sample neighboring depth values
    float depth_up = texture(depth_texture, uv + vec2(0.0, 0.01)).r;
    float depth_down = texture(depth_texture, uv + vec2(0.0, -0.01)).r;
    float depth_left = texture(depth_texture, uv + vec2(-0.01, 0.0)).r;
    float depth_right = texture(depth_texture, uv + vec2(0.01, 0.0)).r;
    
    // Calculate differences
    float diff_x = abs(depth_left - depth_right);
    float diff_y = abs(depth_up - depth_down);
    
    // Combine differences for edge detection
    return clamp(diff_x + diff_y, 0.0, 1.0) * edge_strength;
}

void main() {
    // Sample base color
    vec4 base_color = texture(p3d_Texture0, texcoord);
    
    // Check alpha for early discard (optimization)
    if (base_color.a < 0.1) {
        discard;
    }
    
    // Calculate diorama effect based on depth
    float depth_factor = clamp(depth_value * depth_contrast, 0.0, 1.0);
    
    // Edge detection (if depth texture is available)
    float edge_factor = 0.0;
    if (textureSize(depth_texture, 0).x > 1) {
        edge_factor = getEdgeFactor(texcoord, depth_value);
    }
    
    // Calculate lighting (directional light + ambient)
    float light_intensity = ambient_intensity;
    
    // If normal map is available, use it for lighting
    if (textureSize(normal_texture, 0).x > 1) {
        vec3 normal = normalize(texture(normal_texture, texcoord).rgb * 2.0 - 1.0);
        float diffuse = max(0.0, dot(normal, -light_direction));
        light_intensity += diffuse * (1.0 - ambient_intensity);
    }
    
    // Combine lighting, depth effect, and edge detection
    vec3 final_color = base_color.rgb * light_intensity;
    
    // Darken edges for the cardboard cutout look
    final_color = mix(final_color, final_color * 0.3, edge_factor);
    
    // Apply depth-based shading (darker for further layers)
    final_color = final_color * (1.0 - depth_factor * 0.3);
    
    // Output final color with original alpha
    fragColor = vec4(final_color, base_color.a);
}
            