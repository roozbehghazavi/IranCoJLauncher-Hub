// IranCoJ Edition: GGX specular for the sun (the deferred lighting pass, lighting_pp_ps.hlsl defines IRN_GGX), in place
// of the vanilla Phong gloss table. Included by common.hlsl just before Lit(); other materials keep vanilla shading.
//
// Trowbridge-Reitz distribution, height-correlated Smith visibility, Schlick Fresnel. The roughness comes from the
// game's own shininess (albedo alpha): 0..1 covered Phong powers 1..256 in vanilla, mapped here to the matching GGX
// roughness. Scaled by pi because the engine's diffuse is N.L * light (no 1/pi).

#define IRN_GGX_F0        0.04   // dielectric reflectance at normal incidence
#define IRN_GGX_INTENSITY 1.0
#define IRN_GGX_MASK      2.0    // shininess below 1/IRN_GGX_MASK also fades the highlight out (cloth, dirt, wood)

FLOAT Irn_Ggx(FLOAT3 v_lit_dir_n, FLOAT3 v_nrm_n, float3 v_rfl_dir, FLOAT f_shn)
{
    float3 v_view = -reflect(v_rfl_dir, v_nrm_n);   // v_rfl_dir = reflect(camera -> surface, normal)
    float3 v_hlf = normalize(v_lit_dir_n + v_view);
    float f_nl = saturate(dot(v_nrm_n, v_lit_dir_n));
    float f_nv = saturate(dot(v_nrm_n, v_view)) + 0.0001;
    float f_nh = saturate(dot(v_nrm_n, v_hlf));
    float f_vh = saturate(dot(v_view, v_hlf));

    float f_a2 = 2.0 / (exp2(f_shn * 8.0) + 2.0);
    float f_d = f_nh * f_nh * (f_a2 - 1.0) + 1.0;
    float f_ndf = f_a2 / (3.14159265 * f_d * f_d);
    float f_vis = 0.5 / (f_nl * sqrt(f_nv * f_nv * (1.0 - f_a2) + f_a2) + f_nv * sqrt(f_nl * f_nl * (1.0 - f_a2) + f_a2) + 0.00001);
    float f_fresnel = IRN_GGX_F0 + (1.0 - IRN_GGX_F0) * pow(1.0 - f_vh, 5.0);

    return f_ndf * f_vis * f_fresnel * f_nl * 3.14159265 * IRN_GGX_INTENSITY * saturate(f_shn * IRN_GGX_MASK);
}
