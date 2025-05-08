#version 330

// Input from vertex shader
in vec2 texcoord;

// Texture samplers
uniform sampler2D p3d_Texture0;  // Scene texture

// Day/night parameters
uniform vec4 day_tint;           // Color tint for daytime
uniform vec4 night_tint;         // Color tint for nighttime
uniform float blend_factor;      // Blend between day (0) and night (1)
uniform float fog_density;       // Fog density for night time
uniform float fog_distance;      // Distance at which fog starts

// Output color
out vec4 fragColor;

void main() {
    // Sample original color
    vec4 original = texture(p3d_Texture0, texcoord);
    
    // Apply time-of-day color tinting
    vec4 day_color = original * day_tint;
    vec4 night_color = original * night_tint;
    
    // Blend between day and night
    vec4 color = mix(day_color, night_color, blend_factor);
    
    // Apply fog effect for night time
    // Screen center tends to be less foggy, more fog at edges
    float distance_from_center = length(texcoord - vec2(0.5, 0.5));
    float fog_factor = max(0.0, distance_from_center - fog_distance) * fog_density * blend_factor;
    
    // Apply fog (more fog = more towards night_tint color)
    vec3 fog_color = night_tint.rgb * 0.7; // Darker fog
    color.rgb = mix(color.rgb, fog_color, clamp(fog_factor, 0.0, 0.6));
    
    // Reduce brightness at night
    color.rgb *= mix(1.0, 0.85, blend_factor);
    
    // Add slight blue tint to shadows at night
    if (blend_factor > 0.5) {
        float luminance = dot(color.rgb, vec3(0.299, 0.587, 0.114));
        if (luminance < 0.3) {
            // Dark areas get a blue tint
            color.rgb = mix(color.rgb, vec3(0.2, 0.3, 0.5), (blend_factor - 0.5) * 0.4);
        }
    }
    
    // Output final color
    fragColor = vec4(color.rgb, original.a);
} 