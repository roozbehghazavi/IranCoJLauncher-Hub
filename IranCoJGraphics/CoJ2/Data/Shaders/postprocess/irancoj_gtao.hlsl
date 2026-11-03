// IranCoJ Edition: ground-truth ambient occlusion (GTAO, Jimenez et al. 2016) for the occlusion mask.
// shadows_blur_ps.hlsl calls Irn_Gtao in place of the vanilla normal-weighted SSAO, with the same number of
// depth samples per pixel (IRN_GTAO_SLICES x 2 sides x I_OCCLUSION_SAMPLES steps).
//
// Camera space here: Pos_CS = cam_dir * depth (cm), cam_dir.z = -1, and one pixel of the mask moves cam_dir.xy by
// INV_FRUSTUM_1.xy - so every sample's position is rebuilt exactly and the radius is a real world distance.

#define IRN_GTAO_SLICES   4
#define IRN_GTAO_RADIUS   120.0   // world radius, cm
#define IRN_GTAO_FALLOFF  0.6     // the outer part of the radius where occluders fade out (no halos)
#define IRN_GTAO_MAX      0.1     // largest radius on screen, as a fraction of the mask width
#define IRN_GTAO_POWER    1.5     // strength
#define IRN_GTAO_OPEN     0.75    // the mask value of an open surface (vanilla caps it there; lighting_pp multiplies the colour by it)

#define IRN_PI      3.14159265
#define IRN_PI_HALF 1.57079633

float Irn_ACos(float x)
{
    float a = abs(x);
    float r = (-0.156583 * a + IRN_PI_HALF) * sqrt(1.0 - a);
    return x >= 0.0 ? r : IRN_PI - r;
}

float3 Irn_Gtao_Pos(float2 v_uv, float2 v_cam_dir_xy)
{
    return float3(v_cam_dir_xy, -1.0) * Sample_f1(s_dpt_4, v_uv, 0.0);
}

// v_pix: the pixel (VPOS); v_cam_dir / v_pos / v_nrm: the centre's camera direction, position and normal (camera space).
float Irn_Gtao(float2 v_uv, float2 v_pix, float3 v_cam_dir, float3 v_pos, float3 v_nrm)
{
    float f_radius_px = min(IRN_GTAO_RADIUS / (-v_pos.z * abs(INV_FRUSTUM_1.x)), IRN_GTAO_MAX / RENDER_TARGET_PARAMS.x);
    float f_fade = saturate((f_radius_px - 2.0) / 4.0);   // far away the radius is under a few pixels: nothing to find
    if (f_fade <= 0.0)
        return IRN_GTAO_OPEN;

    float3 v_view = normalize(-v_pos);

    // A different slice rotation and step offset in each pixel of a 2x2 block; lighting_pp's 2x2 upsample averages them.
    float2 v_cell = fmod(floor(v_pix), 2.0);
    float f_rot = frac(v_cell.x * 0.5 + v_cell.y * 0.75);
    float f_jitter = frac(v_cell.x * 0.25 + v_cell.y * 0.5 + 0.125);

    float f_fall_range = IRN_GTAO_FALLOFF * IRN_GTAO_RADIUS;
    float f_fall_mul = -1.0 / f_fall_range;
    float f_fall_add = (IRN_GTAO_RADIUS - f_fall_range) / f_fall_range + 1.0;

    float f_visibility = 0.0;
    [loop]
    for (int s = 0; s < IRN_GTAO_SLICES; s++)
    {
        float f_phi = (s + f_rot) * (IRN_PI / IRN_GTAO_SLICES);
        float2 v_omega = float2(cos(f_phi), sin(f_phi));                // in pixels
        float3 v_dir = normalize(float3(v_omega * INV_FRUSTUM_1.xy, 0.0)); // the same direction in camera space

        // The normal projected into the slice plane, and its angle from the view vector.
        float3 v_ortho = v_dir - dot(v_dir, v_view) * v_view;
        float3 v_axis = normalize(cross(v_ortho, v_view));
        float3 v_proj_nrm = v_nrm - v_axis * dot(v_nrm, v_axis);
        float f_proj_len = length(v_proj_nrm);
        float f_cos_n = saturate(dot(v_proj_nrm, v_view) / max(f_proj_len, 0.0001));
        float f_n = (dot(v_ortho, v_proj_nrm) >= 0.0 ? 1.0 : -1.0) * Irn_ACos(f_cos_n);

        float f_low_0 = cos(f_n + IRN_PI_HALF);
        float f_low_1 = cos(f_n - IRN_PI_HALF);
        float f_horizon_0 = f_low_0;
        float f_horizon_1 = f_low_1;

        [loop]
        for (int j = 0; j < I_OCCLUSION_SAMPLES; j++)
        {
            float f_t = (j + f_jitter) / I_OCCLUSION_SAMPLES;
            float2 v_offset = v_omega * (f_t * f_t * (f_radius_px - 1.0) + 1.0);  // denser near the centre, never the centre itself

            float3 v_d_0 = Irn_Gtao_Pos(v_uv + v_offset * RENDER_TARGET_PARAMS.xy, v_cam_dir.xy + v_offset * INV_FRUSTUM_1.xy) - v_pos;
            float3 v_d_1 = Irn_Gtao_Pos(v_uv - v_offset * RENDER_TARGET_PARAMS.xy, v_cam_dir.xy - v_offset * INV_FRUSTUM_1.xy) - v_pos;
            float f_l_0 = length(v_d_0);
            float f_l_1 = length(v_d_1);
            float f_cos_0 = lerp(f_low_0, dot(v_d_0, v_view) / max(f_l_0, 0.001), saturate(f_l_0 * f_fall_mul + f_fall_add));
            float f_cos_1 = lerp(f_low_1, dot(v_d_1, v_view) / max(f_l_1, 0.001), saturate(f_l_1 * f_fall_mul + f_fall_add));
            f_horizon_0 = max(f_horizon_0, f_cos_0);
            f_horizon_1 = max(f_horizon_1, f_cos_1);
        }

        // Cosine-weighted visible arc between the two horizons, clamped to the hemisphere around the normal.
        float f_h_0 = f_n + clamp(-Irn_ACos(f_horizon_1) - f_n, -IRN_PI_HALF, IRN_PI_HALF);
        float f_h_1 = f_n + clamp(Irn_ACos(f_horizon_0) - f_n, -IRN_PI_HALF, IRN_PI_HALF);
        float f_sin_n = sin(f_n);
        float f_arc_0 = (f_cos_n + 2.0 * f_h_0 * f_sin_n - cos(2.0 * f_h_0 - f_n)) * 0.25;
        float f_arc_1 = (f_cos_n + 2.0 * f_h_1 * f_sin_n - cos(2.0 * f_h_1 - f_n)) * 0.25;
        f_visibility += f_proj_len * (f_arc_0 + f_arc_1);
    }
    f_visibility = pow(saturate(f_visibility / IRN_GTAO_SLICES), IRN_GTAO_POWER);
    return lerp(1.0, f_visibility, f_fade) * IRN_GTAO_OPEN;
}
