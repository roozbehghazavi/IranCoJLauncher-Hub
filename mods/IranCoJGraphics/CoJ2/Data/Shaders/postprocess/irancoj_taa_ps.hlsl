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
sampler s_dpt_4;   // depth: the full-resolution DPT (the quarter one is reused by the time this runs)
sampler s_hist;    // the last result

//#define IRN_TAA_DEBUG 1    // test only: the left half red, the right half this frame
#define IRN_TAA_NEW   0.1   // share of the new frame: lower = smoother, slower to react
#define IRN_TAA_CLIP  1.25   // the history may be this many standard deviations from the neighbourhood's mean
#define IRN_TAA_VIEW  120.0  // cm: nearer is the first-person weapon and hands
#define IRN_TAA_MOTION 0.05  // share of the new frame per pixel moved: 10 px -> half, 20 px and more -> all of it

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

    // Where this pixel was last frame: its position from the depth and the camera direction, through last frame's
    // view-projection. irancojfx.dll keeps that matrix (the engine stores it only for its motion blur). The position
    // is camera + direction * depth: the engine's Pos_WS (camera - direction * depth) put every point behind the
    // camera for this pass. The first-person weapon and hands (closer than IRN_TAA_VIEW cm) move with the camera, so
    // their history is the same place on screen. Without a usable matrix the same place is blended too.
    float f_depth = Sample_f1(s_dpt_4, uv, 0.0);
    float4 v_pos_prv = Mul44(float4(CAMERA_POS_WS.xyz + V_CAM_DIR_WS_TC * f_depth, 1.0), LAST_FRAME_VIEWPROJ_XFORM);
    bool b_reproject = v_pos_prv.w > 0.001 && f_depth > IRN_TAA_VIEW;
    float2 uv_prv = b_reproject ? UV_Screen_From_Pos(v_pos_prv) : uv;

    float3 h = clamp(tex2Dlod(s_hist, float4(uv_prv, 0.0, 0.0)).rgb, lo, hi);

    // How much of this frame: more the further the pixel moved (fast moves would otherwise drag a fading copy along),
    // all of it when it came from off screen, or when a world pixel's history lands where the weapon is now - the
    // weapon moves with the camera, so it was there last frame too and that history is the gun, not this wall.
    float f_moved = length((uv_prv - uv) / px);
    float f_new = max(IRN_TAA_NEW, saturate(f_moved * IRN_TAA_MOTION));
    if (any(uv_prv != saturate(uv_prv))) f_new = 1.0;
    if (b_reproject)
    {
        float f_near = Sample_f1(s_dpt_4, uv_prv, 0.0);
        f_near = min(f_near, Sample_f1(s_dpt_4, uv_prv + float2( 3.0, 0.0) * px, 0.0));
        f_near = min(f_near, Sample_f1(s_dpt_4, uv_prv + float2(-3.0, 0.0) * px, 0.0));
        f_near = min(f_near, Sample_f1(s_dpt_4, uv_prv + float2(0.0,  3.0) * px, 0.0));
        f_near = min(f_near, Sample_f1(s_dpt_4, uv_prv + float2(0.0, -3.0) * px, 0.0));
        if (f_near < IRN_TAA_VIEW) f_new = 1.0;
    }

    OUT.v_clr = float4(lerp(h, c, f_new), 1.0);

    #if defined(IRN_TAA_DEBUG)   // test: the left half red (the pass runs), the right half this frame as read here
        OUT.v_clr = uv.x < 0.5 ? float4(1.0, 0.0, 0.0, 1.0) : float4(c, 1.0);
    #endif
}
