#define PIXELSHADER Data\Shaders\Postprocess\irancoj_taa_ps.hlsl

// IranCoJ Edition: temporal anti-aliasing. The scene is drawn a fraction of a pixel off each frame (Irn_Jitter in
// common.hlsl), and this pass blends each frame into the history of the last ones, reprojected with the camera's
// last view-projection (the engine keeps it for its motion blur): edges and thin wires resolve to their true
// coverage, and shimmering highlights and foliage settle. The history is clipped to the colours around the pixel in
// the new frame, so moving things don't leave ghosts.
//
// Drawn by scene30.ppfx / screen_copy_30.ppfx right before the final pass, on that branch's image (CLR in game, PRV
// otherwise), into IRN_TAA_TMP: the final pass reads that, and it is copied into the history IRN_TAA_HIST.

#include <common.hlsl>
#include <blur_camera_motion_tc.hlsl>

sampler s_clr;     // this frame (CLR in game, PRV otherwise)
sampler s_dpt_4;   // depth (quarter resolution is enough for the camera's motion)
sampler s_hist;    // the last result

//#define IRN_TAA_DEBUG 1    // test only: the left half red, the right half this frame
#define IRN_TAA_NEW   0.1   // share of the new frame: lower = smoother, slower to react
#define IRN_TAA_CLIP  1.25   // the history may be this many standard deviations from the neighbourhood's mean

float3 Irn_Taa_Tap(float2 uv) { return tex2Dlod(s_clr, float4(uv, 0.0, 0.0)).rgb; }

void main(PIX_PARAMS)
{
    float2 uv = V_UV_SCREEN_TC;
    float2 px = RENDER_TARGET_PARAMS.xy;

    // The 3x3 neighbourhood in this frame: its mean and spread bound the history.
    float3 c = Irn_Taa_Tap(uv);
    float3 m1 = c, m2 = c * c;
    float3 lo = c, hi = c;
    [unroll]
    for (int y = -1; y <= 1; y++)
        [unroll]
        for (int x = -1; x <= 1; x++)
        {
            if (x == 0 && y == 0) continue;
            float3 s = Irn_Taa_Tap(uv + float2(x, y) * px);
            m1 += s; m2 += s * s;
            lo = min(lo, s); hi = max(hi, s);
        }
    float3 mean = m1 / 9.0;
    float3 sigma = sqrt(max(m2 / 9.0 - mean * mean, 0.0));
    lo = max(lo, mean - IRN_TAA_CLIP * sigma);
    hi = min(hi, mean + IRN_TAA_CLIP * sigma);

    // Where this pixel was last frame.
    float f_depth = Sample_f1(s_dpt_4, uv, 0.0);
    float4 v_pos_prv = Mul44(Pos_WS(f_depth, V_CAM_DIR_WS_TC), LAST_FRAME_VIEWPROJ_XFORM);
    float2 uv_prv = UV_Screen_From_Pos(v_pos_prv);

    float3 h = clamp(tex2Dlod(s_hist, float4(uv_prv, 0.0, 0.0)).rgb, lo, hi);
    float f_new = (any(uv_prv != saturate(uv_prv)) || v_pos_prv.w <= 0.0) ? 1.0 : IRN_TAA_NEW;   // came from off screen

    OUT.v_clr = float4(lerp(h, c, f_new), 1.0);

    #if defined(IRN_TAA_DEBUG)   // test: the left half red (the pass runs), the right half this frame as read here
        OUT.v_clr = uv.x < 0.5 ? float4(1.0, 0.0, 0.0, 1.0) : float4(c, 1.0);
    #endif
}
