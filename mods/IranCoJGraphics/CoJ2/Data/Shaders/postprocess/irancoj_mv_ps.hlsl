#define PIXELSHADER Data\Shaders\Postprocess\irancoj_mv_ps.hlsl

// IranCoJ Edition: motion vectors - for each pixel of the frame, where it was on screen last frame (Phase 5: the
// input FSR's upscaler needs). From the depth and the camera: the point is camera + direction * depth, taken through
// last frame's view-projection (irancojfx.dll keeps that matrix; the engine stores it only for its motion blur).
// The same reprojection the TAA pass does. Moving characters, horses and weapons need their own (later): here they
// move only with the camera.
//
// Out (IRN_MV, render resolution): rg = last frame's position - this one, in UV (0..1 of the screen); b = 1 on the
// first-person weapon and hands (nearer than IRN_MV_VIEW: they move with the camera, so their history is where they
// are now, motion 0); a = 1.

#include <common.hlsl>
#include <blur_camera_motion_tc.hlsl>

sampler s_clr;     // (unused: bound by the template)
sampler s_dpt_4;   // depth: the full DPT

#define IRN_MV_VIEW 120.0   // cm: nearer is the first-person weapon and hands (as IRN_TAA_VIEW)

void main(PIX_PARAMS)
{
    float2 uv = V_UV_SCREEN_TC;
    float f_depth = Sample_f1(s_dpt_4, uv, 0.0);
    float4 v_pos_prv = Mul44(float4(CAMERA_POS_WS.xyz + V_CAM_DIR_WS_TC * f_depth, 1.0), LAST_FRAME_VIEWPROJ_XFORM);
    bool b_world = f_depth > IRN_MV_VIEW;
    float2 uv_prv = (b_world && v_pos_prv.w > 0.001) ? UV_Screen_From_Pos(v_pos_prv) : uv;
    // No jitter correction: the point is rebuilt along the camera's own (unjittered) ray through this pixel, so it sits
    // at the pixel's unjittered place already and the vector carries no jitter - as FSR wants. (Subtracting the offset
    // here, 2026-11-16, gave a still scene vectors the size of the jitter: FSR shifted its history through the 8-step
    // cycle and the class screen and spectate view shook.)
    OUT.v_clr = float4(uv_prv - uv, b_world ? 0.0 : 1.0, 1.0);
}
