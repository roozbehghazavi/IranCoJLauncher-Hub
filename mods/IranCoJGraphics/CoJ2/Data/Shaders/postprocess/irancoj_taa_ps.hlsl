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
#define IRN_TAA_NEW   0.08  // share of the new frame: lower = smoother, slower to react
#define IRN_TAA_MARGIN 0.25 // the history may stray this share of the neighbourhood's range past it before it is held
#define IRN_TAA_CLIP  1.5    // (unused: the history is held to the neighbourhood's plain min / max)
#define IRN_TAA_VIEW  120.0  // cm: nearer is the first-person weapon and hands
#define IRN_TAA_MOTION 0.05  // share of the new frame per pixel moved: 10 px -> half, 20 px and more -> all of it

float3 Irn_Taa_Tap(float2 uv) { return tex2Dlod(s_clr, float4(uv, 0.0, 0.0)).rgb; }

// A sharp read between pixels (Catmull-Rom, 5 hardware-filtered taps): the history is fetched from where each pixel
// was last frame, which is almost never a pixel centre, and plain filtering there softened the image a little more
// every frame you moved - plainly visible at low resolutions (900p). Its slight overshoot is clamped below.
float3 Irn_Taa_Sharp(sampler s, float2 uv, float2 px)
{
    float2 pos = uv / px;
    float2 c = floor(pos - 0.5) + 0.5;
    float2 f = pos - c;
    float2 w0 = f * (-0.5 + f * (1.0 - 0.5 * f));
    float2 w1 = 1.0 + f * f * (-2.5 + 1.5 * f);
    float2 w2 = f * (0.5 + f * (2.0 - 1.5 * f));
    float2 w3 = f * f * (-0.5 + 0.5 * f);
    float2 w12 = w1 + w2;
    float2 t0 = (c - 1.0) * px;
    float2 t3 = (c + 2.0) * px;
    float2 t12 = (c + w2 / w12) * px;
    float3 r = tex2Dlod(s, float4(t12.x, t0.y, 0.0, 0.0)).rgb * (w12.x * w0.y)
             + tex2Dlod(s, float4(t0.x, t12.y, 0.0, 0.0)).rgb * (w0.x * w12.y)
             + tex2Dlod(s, float4(t12.x, t12.y, 0.0, 0.0)).rgb * (w12.x * w12.y)
             + tex2Dlod(s, float4(t3.x, t12.y, 0.0, 0.0)).rgb * (w3.x * w12.y)
             + tex2Dlod(s, float4(t12.x, t3.y, 0.0, 0.0)).rgb * (w12.x * w3.y);
    float w = w12.x * w0.y + w0.x * w12.y + w12.x * w12.y + w3.x * w12.y + w12.x * w3.y;
    return max(r / w, 0.0);
}

void main(PIX_PARAMS)
{
    float2 uv = V_UV_SCREEN_TC;
    float2 px = RENDER_TARGET_PARAMS.xy;

    // This frame was drawn up to half a pixel off (Irn_Jitter): it is read back where it really belongs, so neither
    // the new image nor the colour range the history is held to moves with the jitter. Read as drawn, distant detail
    // smaller than a pixel changed with every offset and dragged the history along - the image shook, more at low
    // resolutions - and shadow edges, drawn from the same shifted depth, flickered.
    // (only with the jitter that tells its offset: IRN_TAA_JITTER_PX from the graphics spec's common.hlsl; an older one
    // has no Irn_Jitter_Px, and without this test the pass failed to compile and the screen stayed black)
    #if defined(IRN_TAA_JITTER_PX)
        float2 v_unjitter = Irn_Jitter_Px() * float2(1.0, -1.0) * px;
    #else
        float2 v_unjitter = 0.0;
    #endif
    float2 uv_c = uv + v_unjitter;

    // The 3x3 neighbourhood in this frame: its mean and spread bound the history.
    float3 c = Irn_Taa_Tap(uv_c);
    float3 m1 = c, m2 = c * c;
    float3 lo = c, hi = c;
    [unroll]
    for (int y = -1; y <= 1; y++)
        [unroll]
        for (int x = -1; x <= 1; x++)
        {
            if (x == 0 && y == 0) continue;
            float3 s = Irn_Taa_Tap(uv_c + float2(x, y) * px);
            m1 += s; m2 += s * s;
            lo = min(lo, s); hi = max(hi, s);
        }
    // this frame's pixel read sharp too (the un-shift reads it between pixels), held to what is really around it
    float3 c_sharp = clamp(Irn_Taa_Sharp(s_clr, uv_c, px), lo, hi);
    // The history is held to the plain lowest and highest colours around the pixel. A range narrowed further to the
    // spread around the mean (mean +- 1.5 sigma) rejected the history of thin edges - a roof's or rock's rim a pixel
    // or two wide, which slips in and out of the 3x3 as the frame shifts - one frame in, one frame out: they flickered
    // from about 2 m on. (m1 / m2 are kept for IRN_TAA_CLIP, unused now.)

    // Where this pixel was last frame: its position from the depth and the camera direction, through last frame's
    // view-projection. irancojfx.dll keeps that matrix (the engine stores it only for its motion blur). The position
    // is camera + direction * depth: the engine's Pos_WS (camera - direction * depth) put every point behind the
    // camera for this pass. The first-person weapon and hands (closer than IRN_TAA_VIEW cm) move with the camera, so
    // their history is the same place on screen. Without a usable matrix the same place is blended too.
    float f_depth = Sample_f1(s_dpt_4, uv_c, 0.0);   // the depth of what belongs at this pixel (see v_unjitter)
    float4 v_pos_prv = Mul44(float4(CAMERA_POS_WS.xyz + V_CAM_DIR_WS_TC * f_depth, 1.0), LAST_FRAME_VIEWPROJ_XFORM);
    bool b_reproject = v_pos_prv.w > 0.001 && f_depth > IRN_TAA_VIEW;
    float2 uv_prv = b_reproject ? UV_Screen_From_Pos(v_pos_prv) : uv;

    // Held to the neighbourhood with a margin: on a high-contrast edge at low resolution the range jumps with every
    // shift of the frame, and a history held hard to it was snapped to this frame one time and let go the next - the
    // edge flickered. A little slack lets it settle; ghosts stay out (the margin is a quarter of the range).
    float3 v_margin = (hi - lo) * IRN_TAA_MARGIN + 1.0 / 255.0;
    float3 h = clamp(Irn_Taa_Sharp(s_hist, uv_prv, px), lo - v_margin, hi + v_margin);

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

        // ... and where the weapon WAS last frame: the history's alpha marks the weapon and hands (0, written below).
        // Standing still while the gun moves (a reload brings it to the face), the wall behind kept the gun's colours
        // as its history: held only to the wall's own colour range, a dark copy of the gun stayed on the wall until
        // you moved. Read around the spot too: the sharp history read reaches two pixels out.
        float f_was_gun = tex2Dlod(s_hist, float4(uv_prv, 0.0, 0.0)).a;
        f_was_gun = min(f_was_gun, tex2Dlod(s_hist, float4(uv_prv + float2( 1.5,  1.5) * px, 0.0, 0.0)).a);
        f_was_gun = min(f_was_gun, tex2Dlod(s_hist, float4(uv_prv + float2(-1.5,  1.5) * px, 0.0, 0.0)).a);
        f_was_gun = min(f_was_gun, tex2Dlod(s_hist, float4(uv_prv + float2( 1.5, -1.5) * px, 0.0, 0.0)).a);
        f_was_gun = min(f_was_gun, tex2Dlod(s_hist, float4(uv_prv + float2(-1.5, -1.5) * px, 0.0, 0.0)).a);
        if (f_was_gun < 0.99) f_new = 1.0;
    }

    // Blended by brightness (bright pixels count less): a pixel that is bright one frame and dark the next - a lit
    // edge as the frame shifts - can't swing the result back and forth.
    float f_w_new = f_new / (1.0 + dot(c_sharp, float3(0.299, 0.587, 0.114)));
    float f_w_hist = (1.0 - f_new) / (1.0 + dot(h, float3(0.299, 0.587, 0.114)));
    // alpha: 0 on the weapon and hands, 1 on the world - kept in the history (copy.mat copies it, the final pass to
    // the screen ignores it) for the test above next frame
    OUT.v_clr = float4(saturate((h * f_w_hist + c_sharp * f_w_new) / max(f_w_hist + f_w_new, 0.0001)),
                       f_depth > IRN_TAA_VIEW ? 1.0 : 0.0);

    #if defined(IRN_TAA_DEBUG)   // test: the left half red (the pass runs), the right half this frame as read here
        OUT.v_clr = uv.x < 0.5 ? float4(1.0, 0.0, 0.0, 1.0) : float4(c, 1.0);
    #endif
}
