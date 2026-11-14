#define PIXELSHADER Data\Shaders\Postprocess\irancoj_shafts_ps.hlsl

// IranCoJ Edition: light shafts. Drawn by glow_30.ppfx at a quarter of the screen, added to the game's glow (4C)
// in place of its own sun rays, so the shafts go through the game's bloom blur and tone mapping like the sun's glow.
//
// Each pixel walks towards the sun on screen and gathers the bright open sky it passes (the glow source 4B where
// the depth says sky): where a roof, a tree or a hill stands between, that stretch gathers nothing, so light falls
// in streaks past the edges of everything in front of the sun. Strongest looking at the sun, gone 60 degrees away.
// The start of each walk is offset per pixel and per frame; temporal anti-aliasing blends that into smooth shafts.

#include <common.hlsl>
#include <blur_camera_motion_tc.hlsl>

sampler s_clr;     // the glow source (4B): the bright part of the scene
sampler s_dpt_4;   // depth (DPT, full resolution)

#if !defined(IRN_SHAFT_STRENGTH)
    #define IRN_SHAFT_STRENGTH 0.6  // how much of the gathered sky is added
#endif
#define IRN_SHAFT_SAMPLES  16       // steps of each walk (the noise between them is blurred by the glow and TAA)
#define IRN_SHAFT_LENGTH   0.85     // share of the way to the sun walked
#define IRN_SHAFT_DECAY    0.93     // each step counts this much less than the one before
#define IRN_SHAFT_SKY      90000.0  // cm: further than this is open sky (or so far it is lost in the haze)

void main(PIX_PARAMS)
{
    float2 uv = V_UV_SCREEN_TC;
    OUT.v_clr = 0.0;

    // The sun on screen: its direction through the view-projection (a direction projects to its vanishing point).
    float4 v_sun = Mul44(float4(vSunDir, 0.0), VIEWPROJ_XFORM);
    float3 v_ray = normalize(V_CAM_DIR_WS_TC);
    float f_facing = saturate(dot(v_ray, vSunDir));
    f_facing = saturate((f_facing - 0.5) * 2.0);  // 0 at 60 degrees from the sun, 1 on it
    f_facing *= f_facing;
    if (v_sun.w <= 0.0 || f_facing <= 0.0) return;
    float2 uv_sun = UV_Screen_From_Pos(v_sun);

    float2 v_step = (uv_sun - uv) * (IRN_SHAFT_LENGTH / IRN_SHAFT_SAMPLES);
    // interleaved gradient noise, moved on every frame
    float2 v_px = uv / RENDER_TARGET_PARAMS.xy;
    float f_noise = frac(52.9829189 * frac(dot(v_px, float2(0.06711056, 0.00583715))) + frac(TIME * 7.123));
    float2 p = uv + v_step * f_noise;

    float3 v_sum = 0.0;
    float f_w = 1.0, f_wsum = 0.0;
    [loop]
    for (int i = 0; i < IRN_SHAFT_SAMPLES; i++)
    {
        float f_sky = step(IRN_SHAFT_SKY, Sample_f1(s_dpt_4, p, 0.0));
        v_sum += tex2Dlod(s_clr, float4(p, 0.0, 0.0)).rgb * (f_sky * f_w);
        f_wsum += f_w;
        f_w *= IRN_SHAFT_DECAY;
        p += v_step;
    }
    OUT.v_clr.rgb = v_sum / f_wsum * (f_facing * IRN_SHAFT_STRENGTH);
}
