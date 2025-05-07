//Cg
//
// day_night_filter.glsl
// Applies color correction based on time of day
//

// Vertex shader input
void vshader(
    float4 vtx_position : POSITION,
    float2 vtx_texcoord0 : TEXCOORD0,
    uniform float4x4 mat_modelproj,
    out float4 l_position : POSITION,
    out float2 l_texcoord0 : TEXCOORD0)
{
    l_position = mul(mat_modelproj, vtx_position);
    l_texcoord0 = vtx_texcoord0;
}

// Fragment shader input
void fshader(
    float2 l_texcoord0 : TEXCOORD0,
    uniform sampler2D tex_0 : TEXUNIT0,
    uniform float4 day_tint,
    uniform float4 night_tint,
    uniform float blend_factor,
    out float4 o_color : COLOR)
{
    // Sample original texture
    float4 color = tex2D(tex_0, l_texcoord0);
    
    // Apply time-of-day color correction
    float4 tinted_color = lerp(color * day_tint, color * night_tint, blend_factor);
    
    // Apply additional night-time effects when blend_factor is high (night)
    float night_factor = saturate(blend_factor - 0.5) * 2.0;  // 0 to 1 scale for night effects
    
    // Reduce brightness and increase contrast slightly at night
    float luminance = dot(tinted_color.rgb, float3(0.299, 0.587, 0.114));
    float3 contrast_color = lerp(tinted_color.rgb, luminance > 0.5 ? float3(1,1,1) : float3(0,0,0), night_factor * 0.2);
    
    // Shift color to blue-ish for night
    contrast_color = lerp(contrast_color, contrast_color * float3(0.8, 0.9, 1.1), night_factor * 0.3);
    
    // Output final color
    o_color = float4(contrast_color, tinted_color.a);
} 