#version 330

// Input from vertex shader
in vec2 texcoord;

// Texture samplers
uniform sampler2D p3d_Texture0;  // Scene texture
uniform sampler2D lut_texture;    // Look-up table for color grading (optional)

// Color grading parameters
uniform vec3 color_filter;        // Color filter for tinting
uniform float contrast;           // Contrast adjustment
uniform float brightness;         // Brightness adjustment
uniform float saturation;         // Saturation adjustment
uniform float gamma;              // Gamma correction
uniform bool use_lut;             // Whether to use LUT texture

// Time of day parameters
uniform float day_night_blend;    // Blend between day (0) and night (1)
uniform vec3 day_tint;            // Daytime color tint
uniform vec3 night_tint;          // Nighttime color tint

// Output color
out vec4 fragColor;

// RGB to HSV conversion
vec3 rgb2hsv(vec3 c) {
    vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
    vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
    vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));
    
    float d = q.x - min(q.w, q.y);
    float e = 1.0e-10;
    return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
}

// HSV to RGB conversion
vec3 hsv2rgb(vec3 c) {
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

// Apply color LUT (Look-Up Table)
vec3 applyLUT(vec3 color) {
    // Skip if LUT not available or disabled
    if (!use_lut || textureSize(lut_texture, 0).x <= 1) {
        return color;
    }
    
    // Assume 256x16 LUT texture with 16x16 color grids
    float blue = color.b * 15.0;
    vec2 quad1;
    quad1.y = floor(floor(blue) / 4.0);
    quad1.x = floor(blue) - (quad1.y * 4.0);
    
    vec2 quad2;
    quad2.y = floor(ceil(blue) / 4.0);
    quad2.x = ceil(blue) - (quad2.y * 4.0);
    
    vec2 texpos1;
    texpos1.x = (quad1.x * 0.25) + 0.001 + (0.25 - 0.002) * color.r;
    texpos1.y = (quad1.y * 0.25) + 0.001 + (0.25 - 0.002) * color.g;
    
    vec2 texpos2;
    texpos2.x = (quad2.x * 0.25) + 0.001 + (0.25 - 0.002) * color.r;
    texpos2.y = (quad2.y * 0.25) + 0.001 + (0.25 - 0.002) * color.g;
    
    vec3 newcolor1 = texture(lut_texture, texpos1).rgb;
    vec3 newcolor2 = texture(lut_texture, texpos2).rgb;
    
    vec3 newcolor = mix(newcolor1, newcolor2, fract(blue));
    return newcolor;
}

void main() {
    // Sample original color
    vec4 original = texture(p3d_Texture0, texcoord);
    
    // Apply time-of-day tinting
    vec3 tint = mix(day_tint, night_tint, day_night_blend);
    vec3 color = original.rgb * tint;
    
    // Apply color filter
    color *= color_filter;
    
    // Apply brightness
    color = color * brightness;
    
    // Apply contrast
    color = (color - 0.5) * contrast + 0.5;
    
    // Apply saturation adjustment
    vec3 luminance = vec3(dot(color, vec3(0.299, 0.587, 0.114)));
    color = mix(luminance, color, saturation);
    
    // Apply gamma correction
    color = pow(color, vec3(1.0 / gamma));
    
    // Apply LUT color grading if available
    color = applyLUT(color);
    
    // Octopath-inspired color adjustments
    // Slightly enhanced blues in shadows, warmer highlights
    vec3 hsv = rgb2hsv(color);
    if (hsv.z < 0.5) {
        // Cooler shadows
        hsv.x = mix(hsv.x, 0.6, 0.2); // Shift toward blue
        hsv.y = min(hsv.y * 1.2, 1.0); // More saturated
    } else {
        // Warmer highlights
        hsv.x = mix(hsv.x, 0.08, 0.15); // Shift slightly toward yellow
    }
    color = hsv2rgb(hsv);
    
    // Output final color with original alpha
    fragColor = vec4(color, original.a);
}
            