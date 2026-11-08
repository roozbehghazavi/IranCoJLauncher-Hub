#define PIXELSHADER Data\Shaders\Postprocess\irancoj_fx_ps.hlsl

// IranCoJ Edition: the final pass of the scene, drawn to the backbuffer before the HUD (it takes the place of the
// engine's last copy in screen_copy_30/30simple/32 and scene30/32.ppfx, so every pipeline gets it and the HUD never does).
// In one pass: adaptive sharpening, edge anti-aliasing and a light grade, then the same output steps the vanilla
// copy did (curves, output and saturation correction, window gamma).

#include <common.hlsl>
#include <copy_tc.hlsl>

// The values (Settings > Graphics > Remastered), written by the launcher:
//   IRN_SHARPEN   0 off .. 1 strongest          IRN_AA        1 edge anti-aliasing on, 0 off
//   IRN_VIBRANCE  lifts dull colours the most   IRN_CONTRAST  gentle S-curve, 0 off
//   IRN_SPLIT     test only: left half vanilla, right half processed, a gold line between
#include <irancoj_fx_settings.hlsl>

sampler s_tex;
sampler s_tex2;

CONST_FLOAT3 editor_simple_pp;

#if defined(CURVES_ON) || defined(CURVES_SATURATION_ON)
    sampler s_crv;

    FLOAT3 Irn_Curves(FLOAT3 c)
    {
        FLOAT3 k;
        k.r = tex1D(s_crv, c.r).r;
        k.g = tex1D(s_crv, c.g).g;
        k.b = tex1D(s_crv, c.b).b;
        #if defined(F_CURVES)
            return saturate(lerp(c, k, F_CURVES));
        #else
            return k;
        #endif
    }

    FLOAT3 Irn_CurvesSaturation(FLOAT3 c)
    {
        FLOAT l = Luminance(c);
        FLOAT s = tex1D(s_crv, l).a;
        #if defined(F_CURVES_SATURATION)
            s = saturate(s * F_CURVES_SATURATION_SCALE + F_CURVES_SATURATION_BIAS);
        #endif
        return saturate(lerp(l, c, s));
    }
#endif

// The vanilla copy's output steps, in its order (the window gamma is left to the caller, it comes last).
float4 Irn_Vanilla(float4 v)
{
    #if defined(B_BRIGHTNESS_CONTRAST_OUT_ON)
        v.xyz = saturate(v.xyz * editor_simple_pp.y + editor_simple_pp.x);
    #endif
    #if defined(B_GAMMA_OUT_ON)
        v.xyz = Gamma_Encode(v.xyz);
    #endif
    #if defined(F_BLEND_VALUE)
        v.w = F_BLEND_VALUE;
    #endif
    #if defined(V_BLEND_FACTOR)
        v *= V_BLEND_FACTOR;
    #endif
    #if defined(CURVES_ON)
        v.xyz = Irn_Curves(v.xyz);
    #endif
    #if defined(OUT_CORRECTION_ON)
        v.rgb = saturate(v.rgb * F_OUT_SCALE + F_OUT_BIAS);
    #endif
    #if defined(CURVES_SATURATION_ON)
        v.xyz = Irn_CurvesSaturation(v.xyz);
    #endif
    #if defined(SAT_CORRECTION_ON)
        FLOAT f_luminance = saturate(Luminance(v.rgb));
        v.rgb = saturate(lerp(f_luminance, v.rgb, F_OUT_SATURATION));
    #endif
    return v;
}

float3 Irn_Tap(float2 uv) { return Sample_Gamma(s_tex, uv, 0.0).rgb; }
float Irn_Luma(float3 c) { return dot(c, float3(0.299, 0.587, 0.114)); }
float Irn_L(float2 uv) { return sqrt(Irn_Luma(Irn_Tap(uv))); } // perceptual luma for the edge search

#define IRN_AA_EDGE     0.125   // local contrast an edge needs, relative to its brightest pixel
#define IRN_AA_EDGE_MIN 0.0312  // ... and at least this (dark areas)
#define IRN_AA_SUBPIX   0.75    // how much single-pixel detail (wires, far fences) is smoothed

void main(PIX_PARAMS)
{
    float2 uv = V_UV_TC;
    float2 px = RENDER_TARGET_PARAMS.xy; // one texel of the scene (it is the backbuffer's size)

    float4 centre = Sample_Gamma(s_tex, uv, 0.0);
    float3 e = centre.rgb;
    float3 n = Irn_Tap(uv + float2(0.0, -px.y));
    float3 s = Irn_Tap(uv + float2(0.0,  px.y));
    float3 w = Irn_Tap(uv + float2(-px.x, 0.0));
    float3 o = Irn_Tap(uv + float2( px.x, 0.0));

    // Contrast-adaptive sharpening: strong where the area is flat, held back on edges that are already hard, so no halos.
    float3 mn = min(e, min(min(n, s), min(w, o)));
    float3 mx = max(e, max(max(n, s), max(w, o)));
    float3 amp = sqrt(saturate(min(mn, 2.0 - mx) / max(mx, 1e-4)));
    float3 wgt = amp * (-1.0 / lerp(8.0, 5.0, IRN_SHARPEN));
    float3 c = saturate((e + (n + s + w + o) * wgt) / (1.0 + 4.0 * wgt));
    c = lerp(e, c, step(0.001, IRN_SHARPEN));

    #if IRN_AA
        // Edge anti-aliasing, FXAA 3.11 quality (12-step edge search): find the edge's direction and both of its ends,
        // then resample the pixel at its sub-pixel distance from the edge. Edge pixels take that result unsharpened.
        float lM = Irn_L(uv);
        float lS = Irn_L(uv + float2(0.0, px.y));
        float lE = Irn_L(uv + float2(px.x, 0.0));
        float lN = Irn_L(uv - float2(0.0, px.y));
        float lW = Irn_L(uv - float2(px.x, 0.0));
        float lMax = max(max(lN, lW), max(lE, max(lS, lM)));
        float lMin = min(min(lN, lW), min(lE, min(lS, lM)));
        float range = lMax - lMin;

        if (range >= max(IRN_AA_EDGE_MIN, lMax * IRN_AA_EDGE))
        {
            float lNW = Irn_L(uv - px);
            float lSE = Irn_L(uv + px);
            float lNE = Irn_L(uv + float2(px.x, -px.y));
            float lSW = Irn_L(uv + float2(-px.x, px.y));

            float lNS = lN + lS, lWE = lW + lE;
            float lNESE = lNE + lSE, lNWNE = lNW + lNE, lNWSW = lNW + lSW, lSWSE = lSW + lSE;
            float edgeHorz = abs(-2.0 * lW + lNWSW) + abs(-2.0 * lM + lNS) * 2.0 + abs(-2.0 * lE + lNESE);
            float edgeVert = abs(-2.0 * lS + lSWSE) + abs(-2.0 * lM + lWE) * 2.0 + abs(-2.0 * lN + lNWNE);
            bool horz = edgeHorz >= edgeVert;

            float subpix = saturate(abs(((lNS + lWE) * 2.0 + lNWSW + lNESE) / 12.0 - lM) / range);
            subpix = (-2.0 * subpix + 3.0) * subpix * subpix;

            // The neighbour across the edge with the steeper step.
            float lengthSign = horz ? px.y : px.x;
            if (!horz) { lN = lW; lS = lE; }
            float gN = lN - lM, gS = lS - lM;
            bool pairN = abs(gN) >= abs(gS);
            float gradient = max(abs(gN), abs(gS)) * 0.25;
            if (pairN) lengthSign = -lengthSign;
            float lLocal = (pairN ? lN + lM : lS + lM) * 0.5;

            // Walk along the edge both ways until its luma leaves the local average.
            float2 posB = uv;
            if (horz) posB.y += lengthSign * 0.5; else posB.x += lengthSign * 0.5;
            float2 offNP = horz ? float2(px.x, 0.0) : float2(0.0, px.y);
            float2 posN = posB - offNP, posP = posB + offNP;
            float endN = Irn_L(posN) - lLocal, endP = Irn_L(posP) - lLocal;
            bool doneN = abs(endN) >= gradient, doneP = abs(endP) >= gradient;
            const float steps[11] = { 1.0, 1.0, 1.0, 1.0, 1.5, 2.0, 2.0, 2.0, 2.0, 4.0, 8.0 };
            [loop]
            for (int i = 0; i < 11 && !(doneN && doneP); i++)
            {
                if (!doneN) { posN -= offNP * steps[i]; endN = Irn_L(posN) - lLocal; doneN = abs(endN) >= gradient; }
                if (!doneP) { posP += offNP * steps[i]; endP = Irn_L(posP) - lLocal; doneP = abs(endP) >= gradient; }
            }

            float dstN = horz ? uv.x - posN.x : uv.y - posN.y;
            float dstP = horz ? posP.x - uv.x : posP.y - uv.y;
            bool mBelow = lM - lLocal < 0.0;
            bool good = (dstN < dstP) ? ((endN < 0.0) != mBelow) : ((endP < 0.0) != mBelow);
            float offset = good ? 0.5 - min(dstN, dstP) / (dstP + dstN) : 0.0;
            offset = max(offset, subpix * subpix * IRN_AA_SUBPIX);

            float2 posM = uv;
            if (horz) posM.y += offset * lengthSign; else posM.x += offset * lengthSign;
            c = Irn_Tap(posM);
        }
    #endif

    OUT.v_clr = Irn_Vanilla(float4(c, centre.a));

    // Grade, after the level's own curves (else they flatten it again): vibrance (dull colours gain the most, skin and
    // sky stay natural), then a soft S-curve around mid grey.
    float3 g = OUT.v_clr.rgb;
    float l = Irn_Luma(g);
    float sat = max(g.r, max(g.g, g.b)) - min(g.r, min(g.g, g.b));
    g = saturate(lerp(l, g, 1.0 + IRN_VIBRANCE * (1.0 - sat)));
    OUT.v_clr.rgb = lerp(g, g * g * (3.0 - 2.0 * g), IRN_CONTRAST);

    #if IRN_SPLIT
        OUT.v_clr.rgb = (uv.x < 0.5) ? Irn_Vanilla(centre).rgb : OUT.v_clr.rgb;
        OUT.v_clr.rgb = (abs(uv.x - 0.5) < px.x) ? float3(0.886, 0.694, 0.369) : OUT.v_clr.rgb;
    #endif

    #if defined(B_GAMMA_WINDOW_OUT_ON)
        OUT.v_clr.xyz = Gamma_Win_Encode(OUT.v_clr.xyz);
    #endif
}
