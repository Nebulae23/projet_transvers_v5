//Cg
//
// fog_volume.glsl
// Volumetric fog shader for night fog system
//

// Vertex shader input
void vshader(
    float4 vtx_position : POSITION,
    float2 vtx_texcoord0 : TEXCOORD0,
    float4 vtx_color : COLOR,
    uniform float4 fogColor,
    uniform float fogDensity,
    uniform float4x4 mat_modelproj,
    out float4 l_position : POSITION,
    out float2 l_texcoord0 : TEXCOORD0,
    out float4 l_color : COLOR,
    out float3 l_worldPos : TEXCOORD1)
{
    // Transform vertex position
    l_position = mul(mat_modelproj, vtx_position);
    
    // Pass through texture coordinates
    l_texcoord0 = vtx_texcoord0;
    
    // Pass through vertex color with fog density as alpha
    l_color = vtx_color;
    l_color.a *= fogDensity;
    
    // Pass world position for depth calculations
    l_worldPos = vtx_position.xyz;
}

// Fragment shader input
void fshader(
    float2 l_texcoord0 : TEXCOORD0,
    float4 l_color : COLOR,
    float3 l_worldPos : TEXCOORD1,
    uniform float fogDensity,
    uniform float4 fogColor,
    uniform sampler2D tex_0 : TEXUNIT0,
    out float4 o_color : COLOR)
{
    // Sample texture if available
    float4 tex_color = tex2D(tex_0, l_texcoord0);
    
    // Mix texture with vertex color if texture exists
    float4 color = tex_color * l_color;
    
    // Apply base fog color
    color = lerp(color, fogColor, 0.8);
    
    // Add depth-based density
    float depth = length(l_worldPos);
    float depthFactor = 1.0 - exp(-depth * 0.01);
    
    // Apply density falloff to alpha
    color.a *= (depthFactor * fogDensity);
    
    // Add subtle swirl effect based on position
    float swirl = sin(l_worldPos.x * 0.05 + l_worldPos.y * 0.05 + fogDensity * 2.0) * 0.5 + 0.5;
    color.a *= (0.8 + swirl * 0.2);
    
    // Apply height-based density (thinner at top, thicker at bottom)
    float heightFactor = 1.0 - l_worldPos.z * 0.1;
    color.a *= clamp(heightFactor, 0.5, 1.0);
    
    // Adjust alpha for overall fog density
    color.a *= fogDensity;
    
    // Output final color
    o_color = color;
} 