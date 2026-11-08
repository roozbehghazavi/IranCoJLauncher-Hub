// IranCoJ Edition: GGX specular for the sun (the deferred lighting pass, lighting_pp_ps.hlsl defines IRN_GGX), in place
// of the vanilla Phong gloss table, and metal. Included by common.hlsl just before Lit(); other materials keep vanilla
// shading.
//
// Trowbridge-Reitz distribution, height-correlated Smith visibility, Schlick Fresnel. The roughness comes from the
// game's own shininess (albedo alpha): 0..1 covered Phong powers 1..256 in vanilla, mapped here to the matching GGX
// roughness. Scaled by pi because the engine's diffuse is N.L * light (no 1/pi).

#define IRN_GGX_F0        0.04   // dielectric reflectance at normal incidence
#define IRN_GGX_INTENSITY 1.0
#define IRN_GGX_MASK      2.0    // shininess below 1/IRN_GGX_MASK also fades the highlight out (cloth, dirt, wood)
#define IRN_METAL_AMOUNT  0.85   // how far metal moves from the vanilla look to physically based metal
#define IRN_METAL_SHN     3.0    // ... scaled by shininess: polished parts fully, rusty or matte iron hardly at all

// N.L-weighted GGX distribution and visibility (no Fresnel), and the V.H the Fresnel term needs.
float Irn_Ggx_Dv(float3 v_lit_dir_n, float3 v_nrm_n, float3 v_view, float f_shn, out float f_vh)
{
    // Never normalize a zero vector (view exactly opposite the sun): one NaN pixel would poison the eye adaptation
    // and flip the exposure of the whole frame.
    float3 v_hlf = v_lit_dir_n + v_view;
    v_hlf *= rsqrt(max(dot(v_hlf, v_hlf), 0.000001));
    float f_nl = saturate(dot(v_nrm_n, v_lit_dir_n));
    float f_nv = saturate(dot(v_nrm_n, v_view)) + 0.0001;
    float f_nh = saturate(dot(v_nrm_n, v_hlf));
    f_vh = saturate(dot(v_view, v_hlf));

    float f_a2 = 2.0 / (exp2(f_shn * 8.0) + 2.0);
    float f_d = f_nh * f_nh * (f_a2 - 1.0) + 1.0;
    float f_ndf = f_a2 / (3.14159265 * f_d * f_d);
    float f_vis = 0.5 / (f_nl * sqrt(f_nv * f_nv * (1.0 - f_a2) + f_a2) + f_nv * sqrt(f_nl * f_nl * (1.0 - f_a2) + f_a2) + 0.00001);
    return min(f_ndf * f_vis * f_nl * 3.14159265, 512.0);   // finite: a mirror-sharp highlight can't blow up the exposure
}

FLOAT Irn_Ggx(FLOAT3 v_lit_dir_n, FLOAT3 v_nrm_n, float3 v_rfl_dir, FLOAT f_shn)
{
    float3 v_view = -reflect(v_rfl_dir, v_nrm_n);   // v_rfl_dir = reflect(camera -> surface, normal)
    float f_vh;
    float f_dv = Irn_Ggx_Dv(v_lit_dir_n, v_nrm_n, v_view, f_shn, f_vh);
    float f_fresnel = IRN_GGX_F0 + (1.0 - IRN_GGX_F0) * pow(1.0 - f_vh, 5.0);
    return min(f_dv * f_fresnel * IRN_GGX_INTENSITY * saturate(f_shn * IRN_GGX_MASK), 32.0);
}

#if defined(F_SPECULAR_MULTI) && defined(F_SHINES) && defined(DIFFUSE_ON) && defined(LIGHTING_SUN_ON) && defined(V_CLR)
    #define IRN_METAL_ON 1
    // Metal (f_metal from the normal buffer's alpha): no sun diffuse, a highlight tinted by its own colour (F0 = albedo),
    // the ambient kept as it is (there are no environment reflections yet, so metal in the shade would go black).
    float3 Irn_Metal(float3 v_out, float f_metal, shading_in IN)
    {
        float f_amount = f_metal * saturate(IN.f_shn * IRN_METAL_SHN) * IRN_METAL_AMOUNT;
        if (f_amount <= 0.0)
            return v_out;
        float3 v_view = -reflect(IN.v_rfl_dir, IN.v_nrm_n);
        float f_vh;
        float f_dv = Irn_Ggx_Dv(IN.c_lit.v_dir_n, IN.v_nrm_n, v_view, IN.f_shn, f_vh);
        float3 v_f0 = IN.v_clr;
        float3 v_fresnel = v_f0 + (1.0 - v_f0) * pow(1.0 - f_vh, 5.0);
        float3 v_metal = IN.c_lit.v_amb * IN.v_clr + IN.c_lit.v_clr * v_fresnel * min(f_dv, 32.0);
        return lerp(v_out, v_metal, f_amount);
    }
#endif
