"""Writes the "graphics" block of edition.json: the remastered graphics' edits of the player's own pipeline scripts
and shaders (applied by the launcher's GraphicsApplier for the chosen settings, removed in Vanilla mode).

{{name}} in a replacement is a graphics value (launcher GraphicsSettings.RewriteValues), "when" limits a file to some
values, "scale" multiplies the number a pattern captures as (?<n>...). Every rule here was tested in game.

usage: python tools/edition_graphics.py          (edits edition.json in place)
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
EDITION = os.path.join(HERE, '..', 'edition.json')
N = '\r\n'
D0, D1 = 'CoJ2/Data0.pak', 'CoJ2/Data1.pak'


def rw(path, pak, entry, replace=(), scale=(), when=None):
    r = {'path': 'CoJ2/' + path, 'pak': pak, 'entry': entry}
    if when:
        r['when'] = when
    r['replace'] = [list(p) for p in replace]
    if scale:
        r['scale'] = [list(p) for p in scale]
    return r


AO = {'ao': ['half', 'full']}
rewrites = []

# The final pass (irancoj_fx_ps.hlsl, IranCoJ Graphics mod) in place of the engine's last copy to the backbuffer,
# drawn before the HUD; its template is the player's own copy.mtt.
rewrites.append(rw('Data/Shaders/postprocess/irancoj_fx.mtt', D1, 'Data/Shaders/postprocess/copy.mtt',
                   [(r'copy_ps\.hlsl', 'irancoj_fx_ps.hlsl')]))
final = (r'(?<=screen_copy_30_setup\.ppfx"\)(?:(?!SetRenderTarget|!include)[\s\S])*)'
         r'QuadScreen\("copy(_gamma_win)?(?:_blinn)?(_out)?\.mat"')
for f in ('Effects/screen_copy_30.ppfx', 'Effects/screen_copy_30simple.ppfx', 'Effects/screen_copy_32.ppfx',
          'scene30.ppfx', 'scene32.ppfx'):
    rewrites.append(rw('Data/Postprocess/' + f, D0, 'Data/Postprocess/' + f, [(final, 'QuadScreen("irancoj_fx$1$2.mat"')]))

# Soft shadow edges: a (2r+1)^2 grid of hardware-filtered taps in place of the single tap.
pcf = ('FLOAT Irn_Shadows_PCF(float3 v_uv_shadowmap)' + N +
       '                {' + N +
       '                    // IranCoJ Edition: hardware-filtered taps around the point (each already a 2x2 compare)' + N +
       '                    FLOAT f_sum = 0.0;' + N +
       '                    float2 v_texel = TEX_INV_SIZE_s_shadowmap.xy;' + N +
       '                    for (int y = -{{pcf_r}}; y <= {{pcf_r}}; y++)' + N +
       '                        for (int x = -{{pcf_r}}; x <= {{pcf_r}}; x++)' + N +
       '                            f_sum += Shadows_Calc(float3(v_uv_shadowmap.xy + float2(x, y) * v_texel, v_uv_shadowmap.z));' + N +
       '                    return f_sum / {{pcf_n}};' + N +
       '                }' + N + N + '                ')
rewrites.append(rw('Data/Shaders/Common/shadows.hlsl', D1, 'Data/Shaders/Common/shadows.hlsl', [
    (r'(?=FLOAT Shadows_Calc_PCF\(float3 v_uv_shadowmap\))', pcf),
    (r'(Shadows_Calc_PCF\(float3 v_uv_shadowmap\)\s*\{\s*FLOAT f_shadow = 1\.0;\s*#if defined\(SHADER_PATH_PS3\) \|\| '
     r'\(HSM_MODE == HSMM_NVIDIA\)\s*)f_shadow = Shadows_Calc\(v_uv_shadowmap\);', '$1f_shadow = Irn_Shadows_PCF(v_uv_shadowmap);')
], when={'shadow_filter': ['medium', 'high']}))

# Shadow bias: lookups are pushed off each surface by [2, 8, 32, 128] cm per cascade, sized for the vanilla 1024
# shadow map; with finer shadow texels the launcher shrinks it (else small shadows like window sills vanish as you
# step back). Tested in game at 4096 / cascades x1.5: [0.75, 3, 12, 48] - no acne.
rewrites.append(rw('Data/Scripts/varlist_shadows_bias.scr', D0, 'Data/Scripts/varlist_shadows_bias.scr', [
    (r'\[2\.0+, 8\.0+, 32\.0+, 128\.0+\]', '[{{bias0}}, {{bias1}}, {{bias2}}, {{bias3}}]')
], when={'shadow_bias': ['on']}))

# Ambient occlusion (and the cloud shadow mask) at half or full resolution (vanilla: quarter), Normal pipeline only:
# its own buffer IRN_SHD, averaged down into the vanilla 4_SHD for rain and the forward materials.
rewrites.append(rw('Data/Postprocess/scene30_init_core.ppfx', D0, 'Data/Postprocess/scene30_init_core.ppfx', [
    (r'\z', N + '//IranCoJ Edition: full-resolution occlusion / cloud shadow mask (Normal pipeline)' + N +
     'BufferScreenFormat("IRN_SHD", 1, "A8R8G8B8", "temp")' + N)], when={'ao': ['full']}))
rewrites.append(rw('Data/Postprocess/scene30_init_core.ppfx', D0, 'Data/Postprocess/scene30_init_core.ppfx', [
    (r'\z', N + '//IranCoJ Edition: half-resolution occlusion / cloud shadow mask and its depth (Normal pipeline)' + N +
     'BufferScreenFormat("IRN_SHD", 2, "A8R8G8B8", "temp")' + N + 'BufferScreenFormat("IRN_DPT_2", 2, "R32F", "temp")' + N)],
    when={'ao': ['half']}))
rewrites.append(rw('Data/Postprocess/Effects/depth_resolve_30.ppfx', D0, 'Data/Postprocess/Effects/depth_resolve_30.ppfx', [
    (r'\z', N + 'SetRenderTarget("IRN_DPT_2", "") //IranCoJ Edition: half-resolution depth' + N +
     '    QuadScreen("copy_2_depth.mat", "std", 2)' + N)], when={'ao': ['half']}))
down = (N + '        SetRenderTarget("4_SHD", "") //IranCoJ Edition: averaged down for rain and forward materials' + N +
        '            SetTexture(8, "IRN_SHD")' + N + '                QuadScreen("copy_blinn.mat", "std", 4)')
rewrites.append(rw('Data/Postprocess/Effects/opq_shadows_30.ppfx', D0, 'Data/Postprocess/Effects/opq_shadows_30.ppfx', [
    (r'\ASetRenderTarget\("4_SHD", ""\)(\s*)SetTexture\(8, "DPT_4_32F"\)', 'SetRenderTarget("IRN_SHD", "")$1SetTexture(8, "{{ao_depth}}")'),
    (r'QuadScreen\("(shadows_blur|shadows_blur_noclouds|ssao)\.mat", "std", 4\)', 'QuadScreen("$1.mat", "std", {{ao_div}})' + down)
], when=AO))
rewrites.append(rw('Data/Postprocess/Effects/opq_lighting_setup_tex.ppfx', D0, 'Data/Postprocess/Effects/opq_lighting_setup_tex.ppfx', [
    (r'SetTexture\(8, "4_SHD"\)', 'SetTexture(8, "IRN_SHD")'),
    (r'SetTexture\(9, "DPT_4_32F"\)', 'SetTexture(9, "{{ao_depth}}")')
], when=AO))
rewrites.append(rw('Data/Shaders/postprocess/lighting_pp_vs.hlsl', D1, 'Data/Shaders/postprocess/lighting_pp_vs.hlsl', [
    (r'RENDER_TARGET_PARAMS\.zw \* 0\.25\)', 'RENDER_TARGET_PARAMS.zw * {{ao_texel}})'),
    (r'RENDER_TARGET_PARAMS\.xyxy \* 4\.0', 'RENDER_TARGET_PARAMS.xyxy * {{ao_point}}')
], when=AO))
# GTAO (the mod's irancoj_gtao.hlsl) in place of the vanilla SSAO loop; i_occlusion_samples sets its steps.
rewrites.append(rw('Data/Shaders/postprocess/shadows_blur_ps.hlsl', D1, 'Data/Shaders/postprocess/shadows_blur_ps.hlsl', [
    (r'(?=#if defined\(SHADER_PATH_X360\)\s*\[maxtempreg)',
     '#if defined(OCCLUSION_ON)' + N + '    #include <irancoj_gtao.hlsl> //IranCoJ Edition' + N + '#endif' + N + N),
    (r'(?s)FLOAT f_occlusion = 0\.0;.*?f_out_ssao = min\(f_out_ssao, 0\.75\);//fix: light edges',
     'f_out_ssao = Irn_Gtao(V_UV_SCREEN_TC, V_POS_SS_TC.xy, v_cam_dir_ss, v_pos_center.xyz, v_nrm); //IranCoJ Edition: GTAO')
], when=AO))
# With TAA the depth this pass reads was drawn up to half a pixel off (Irn_Jitter), but its view ray goes through the
# pixel's centre: the point it rebuilds sits a little in front of or behind the real surface, and on ground seen at a
# shallow angle that flipped the shadow test every frame - shadows flickering on and off, the more the bigger the
# pixels (900p). The ray is aimed where the depth texel really is. The mask is drawn at 1/{{ao_div}} of the screen
# with AO on, at the vanilla quarter without: the offset in its pixels is the screen's divided by that.
def shd_unjitter(div):
    return [(r'(float3 v_cam_dir_ss = Cam_Dir_Out_PP\(V_POS_SS_TC\);)',
             '$1' + N + '        #if defined(IRN_TAA_JITTER_PX) //IranCoJ Edition: the ray where this depth texel really is (TAA jitter)' + N +
             '            float4 v_irn_pos_ss = V_POS_SS_TC;' + N +
             '            v_irn_pos_ss.xy += Irn_Jitter_Px() * float2(-1.0, 1.0) / ' + div + ';' + N +
             '            v_cam_dir_ss = Cam_Dir_Out_PP(v_irn_pos_ss);' + N +
             '        #endif')]
rewrites.append(rw('Data/Shaders/postprocess/shadows_blur_ps.hlsl', D1, 'Data/Shaders/postprocess/shadows_blur_ps.hlsl',
                   shd_unjitter('{{ao_div}}.0'), when={'taa': ['on'], 'ao': ['half', 'full']}))
rewrites.append(rw('Data/Shaders/postprocess/shadows_blur_ps.hlsl', D1, 'Data/Shaders/postprocess/shadows_blur_ps.hlsl',
                   shd_unjitter('4.0'), when={'taa': ['on'], 'ao': ['vanilla']}))
rewrites.append(rw('Data/Scripts/varlist_occlusion.scr', D0, 'Data/Scripts/varlist_occlusion.scr', [
    (r'VarInt\( "i_occlusion_samples", 3 \)', 'VarInt( "i_occlusion_samples", {{ao_rings}} ) //IranCoJ Edition: vanilla 3')
], when=AO))

# Tone mapping: a filmic curve normalised to each level's own white point, blended with vanilla Reinhard.
filmic = ('//IranCoJ Edition: filmic tonemapping (IRN_FILMIC 0 = vanilla Reinhard, 1 = filmic)' + N +
          '#define IRN_FILMIC {{tonemap}}' + N +
          'float3 Irn_Filmic(float3 x)' + N + '{' + N +
          '    return ((x * (0.22 * x + 0.03) + 0.002) / (x * (0.22 * x + 0.30) + 0.06)) - 0.0333333;' + N + '}' + N + N + N)
tm = ('OUT_Clr_0.xyz = (v_clr_scaled * (v_clr_scaled * INV_WHITELUMINANCE + 1.0)) / (1.0 + v_clr_scaled);' + N +
      '        float f_irn_white = clamp(rsqrt(max(INV_WHITELUMINANCE, 0.001)), 1.0, 32.0);' + N +
      '        float f_irn_bias = clamp(1.0 + 0.38 * log(f_irn_white * 0.5), 0.6, 2.0);' + N +
      '        float3 v_irn = Irn_Filmic(v_clr_scaled * f_irn_bias) / Irn_Filmic(f_irn_white * f_irn_bias).xxx;' + N +
      '        OUT_Clr_0.xyz = lerp(OUT_Clr_0.xyz, v_irn, IRN_FILMIC);' + N)
rewrites.append(rw('Data/Shaders/postprocess/tonemapping_ps.hlsl', D1, 'Data/Shaders/postprocess/tonemapping_ps.hlsl', [
    (r'(?=#if !defined\(GLOW_ON\)\s*sampler s_blur;)', filmic),
    (r'OUT_Clr_0\.xyz = \(v_clr_scaled \* \(v_clr_scaled \* INV_WHITELUMINANCE \+ 1\.0\)\) / \(1\.0 \+ v_clr_scaled\);\r?\n', tm)
], when={'tonemap': ['0.6', '1']}))

# Texture sharpness: every material and the terrain take their anisotropy from values.mtt (vanilla 4x).
rewrites.append(rw('Data/Shaders/Common/values.mtt', D1, 'Data/Shaders/Common/values.mtt', [
    (r'export int i_tex_aniso_def = 4;', 'export int i_tex_aniso_def = {{aniso}}; //IranCoJ Edition: vanilla 4')
], when={'aniso': ['8', '16']}))

# The material fade bands (the maps' mesh_shader_lod / terrain_shader_lod) follow the detail distance.
rewrites.append(rw('Data/Shaders/Common/common.mtt', D1, 'Data/Shaders/Common/common.mtt', [
    (r'float f_scale = 0\.01;', 'float f_scale = {{shader_band}}; //IranCoJ Edition: shader LOD bands (vanilla 0.01)')
], when={'detail': ['2', '5', '10']}))

# GGX sun specular (the mod's irancoj_ggx.hlsl), only where lighting_pp_ps.hlsl defines IRN_GGX.
LIGHT = {'lighting': ['modern']}
rewrites.append(rw('Data/Shaders/postprocess/lighting_pp_ps.hlsl', D1, 'Data/Shaders/postprocess/lighting_pp_ps.hlsl', [
    (r'\A(#define PIXELSHADER[^\r\n]*\r?\n)',
     '$1#define IRN_GGX 1 //IranCoJ Edition: GGX sun specular (irancoj_ggx.hlsl)' + N +
     '//#define IRN_METAL_DEBUG 1 //IranCoJ Edition: test only, the left half shows the metal mask' + N)
], when=LIGHT))
rewrites.append(rw('Data/Shaders/Common/common.hlsl', D1, 'Data/Shaders/Common/common.hlsl', [
    (r'(?m)^(?=[ \t]*FLOAT3 Lit\(shading_in IN\))',
     '        #if defined(IRN_GGX) //IranCoJ Edition' + N + '            #include <irancoj_ggx.hlsl>' + N + '        #endif' + N + N),
    (r'F_SPECULAR_MULTI = Specular_Shading_Phong\(IN\);',
     '#if defined(IRN_GGX) && defined(F_SHINES) && defined(DIFFUSE_ON) //IranCoJ Edition' + N +
     '                        F_SPECULAR_MULTI = Irn_Ggx(IN.c_lit.v_dir_n, IN.v_nrm_n, IN.v_rfl_dir, F_SHINES);' + N +
     '                    #else' + N + '                        F_SPECULAR_MULTI = Specular_Shading_Phong(IN);' + N + '                    #endif'),
    (r'#if defined\(F_SPECULAR_MULTI\) && defined\(F_SHINES\) && !defined\(VERTEXSHADER\)',
     '#if defined(F_SPECULAR_MULTI) && defined(F_SHINES) && !defined(VERTEXSHADER) && !defined(IRN_GGX)')
], when=LIGHT))

# Metal, packed into the normal buffer's alpha (a 4th render target disturbed the engine's frame: the sun went out at
# some camera angles). That channel only carried subsurface scattering, which metal never has: it now holds SSS x 0.5,
# or 1 for a material whose surface type is SRF_METAL. Every writer is encoded, and the sun lighting (its only reader)
# decodes it.
rewrites.append(rw('Data/Shaders/master/Templates/templates.mtt', D1, 'Data/Shaders/master/Templates/templates.mtt', [
    (r'string __out_nrm_a = \(b_sss_on\) \? "\(" \+ __sss \+ "\)" : "0\.0";',
     'string __out_nrm_a = (b_sss_on) ? "(" + __sss + ") * 0.5" : "0.0"; //IranCoJ Edition: SSS x0.5, or 1 = metal' + N +
     '            string __out_nrm_a = (e_srf_id == SRF_METAL) ? "1.0" : __out_nrm_a;')
], when=LIGHT))
rewrites.append(rw('Data/Shaders/master/Templates/grass.mtt', D1, 'Data/Shaders/master/Templates/grass.mtt', [
    (r'saturate\(dot\(" \+ s_t00_rgb \+ ",1\.0/3\.0\)\)\)";',
     'saturate(dot(" + s_t00_rgb + ",1.0/3.0)) * 0.5)"; //IranCoJ Edition: SSS x0.5')
], when=LIGHT))
rewrites.append(rw('Data/Shaders/master/Templates/fx.mtt', D1, 'Data/Shaders/master/Templates/fx.mtt', [
    (r'string __out_nrm = "half4\(0\.5,0\.5,1,0\.5\)";',
     'string __out_nrm = "half4(0.5,0.5,1,0.25)"; //IranCoJ Edition: SSS x0.5')
], when=LIGHT))
rewrites.append(rw('Data/Shaders/postprocess/lighting_pp_ps.hlsl', D1, 'Data/Shaders/postprocess/lighting_pp_ps.hlsl', [
    (r'FLOAT f_sss = v_nrm\.w;',
     'FLOAT f_irn_metal = step(0.75, v_nrm.w); //IranCoJ Edition: the alpha is SSS x0.5, or 1 = metal' + N +
     '    FLOAT f_sss = saturate(v_nrm.w * 2.0) * (1.0 - f_irn_metal);'),
    (r'FLOAT3 v_out = Lit\(c_shading_in\);',
     'FLOAT3 v_out = Lit(c_shading_in);' + N + '    #if defined(IRN_METAL_ON) //IranCoJ Edition: metal (irancoj_ggx.hlsl)' + N +
     '        v_out = Irn_Metal(v_out, f_irn_metal, c_shading_in);' + N + '    #endif'),
    (r'OUT\.v_clr\.xyz = Encode_Clr\(OUT\.v_clr\.xyz\);',
     '#if defined(IRN_METAL_DEBUG) //IranCoJ Edition: test view, the left half shows the metal mask' + N +
     '        if (V_UV_0_TC.x < 0.5) OUT.v_clr.xyz = f_irn_metal.xxx;' + N +
     '    #endif' + N + '    OUT.v_clr.xyz = Encode_Clr(OUT.v_clr.xyz);')
], when=LIGHT))

# Temporal anti-aliasing (the mod's irancoj_taa_ps.hlsl / .mat): the scene is drawn a sub-pixel off each frame and
# blended into a history reprojected with the camera's last view-projection. The material's template is the player's
# own blur_camera_motion.mtt (its vertex shader gives the world-space camera direction), with a history sampler.
TAA = {'taa': ['on']}
rewrites.append(rw('Data/Shaders/postprocess/irancoj_taa.mtt', D1, 'Data/Shaders/postprocess/blur_camera_motion.mtt', [
    (r'BlendFunc\(SRC_ALPHA, INV_SRC_ALPHA, ONE, ONE\);', '//IranCoJ Edition: TAA writes its result (no blending)'),
    # the motion blur's float and int constants: the TAA shader has neither, and a constant the shader lacks may fail it
    (r'(?s)extern float FPS;.*?Define\("I_SAMPLES", i_samples\);', '//IranCoJ Edition: no constants (the motion blur\'s are not used)'),
    (r'(?s)int i_cst_i_current = i_const_int_first;.*?Define\(s_cst_name \+ "000", s_cst_000\);', '//IranCoJ Edition: no constants'),
    (r'use PP_TMU\(s_sampler = "s_clr", i_user_map = 8, e_filter = LINEAR_NO_MIP, e_tile = MIRROR\);',
     'use PP_TMU(s_sampler = "s_clr", i_user_map = 8, e_filter = LINEAR_NO_MIP, e_tile = CLAMP);'),
    (r'(use PP_TMU\(s_sampler = "s_dpt_4", i_user_map = 9, e_filter = NO_FILTERING, e_tile = CLAMP\);)',
     '$1' + N + '				use PP_TMU(s_sampler = "s_hist", i_user_map = 10, e_filter = LINEAR_NO_MIP, e_tile = CLAMP);'),
    (r'#include <blur_camera_motion_ps\.hlsl>', '#include <irancoj_taa_ps.hlsl>')
], when=TAA))
# The history lives across frames (no "temp": the engine may reuse a temp buffer's memory within the frame). Half floats:
# the alpha carries each pixel's depth to the next frame (negative on the weapon), which rejects the history of a
# character that moved (irancoj_taa_ps.hlsl).
rewrites.append(rw('Data/Postprocess/scene30_init_core.ppfx', D0, 'Data/Postprocess/scene30_init_core.ppfx', [
    (r'\z', N + '//IranCoJ Edition: temporal anti-aliasing (history kept between frames, and the pass result)' + N +
     'BufferScreenFormat("IRN_TAA_HIST", 1, "A16B16G16R16F", "")' + N + 'BufferScreenFormat("IRN_TAA_TMP", 1, "A16B16G16R16F", "temp")' + N)
], when=TAA))
# In both final-copy branches (in game the image is in CLR, at other times in PRV): TAA on that source into our own
# IRN_TAA_TMP, the history copied from it, and the final pass reads IRN_TAA_TMP. The game's buffers are never written
# (writing PRV, which the in-game branch reads again, turned the screen white).
def taa_block(src):
    return ('//IranCoJ Edition: temporal anti-aliasing of ' + src + ' (irancoj_taa.mat), the history kept for the next frame' + N +
            '            SetRenderTarget("IRN_TAA_TMP", "")' + N + '                SetTexture(8, "' + src + '")' + N +
            '                SetTexture(9, "DPT")' + N + '                SetTexture(10, "IRN_TAA_HIST")' + N +
            '                    QuadScreen("irancoj_taa.mat", "std", 1)' + N +
            '            SetRenderTarget("IRN_TAA_HIST", "")' + N + '                SetTexture(8, "IRN_TAA_TMP")' + N +
            '                    QuadScreen("copy.mat", "std", 1)' + N +
            '            SetTextureVar(9, "s_curves") //IranCoJ Edition: slot 9 back to the colour curves (TAA had the depth there)' + N + N +
            '            ')
for f in ('scene30.ppfx', 'Effects/screen_copy_30.ppfx'):
    rewrites.append(rw('Data/Postprocess/' + f, D0, 'Data/Postprocess/' + f, [
        (r'!include\("screen_copy_30_setup\.ppfx"\)(\s*)SetTexture\(8, "CLR"\)',
         taa_block('CLR') + '!include("screen_copy_30_setup.ppfx")$1SetTexture(8, "IRN_TAA_TMP")'),
        (r'!include\("screen_copy_30_setup\.ppfx"\)(\s*)SetTexture\(8, "PRV"\)',
         taa_block('PRV') + '!include("screen_copy_30_setup.ppfx")$1SetTexture(8, "IRN_TAA_TMP")')
    ], when=TAA))
# The jitter: every main-camera vertex shader (not shadow maps, reflections, sprites) a sub-pixel off, the same
# offset for all shaders of a frame (from the engine's TIME). The offset is one of 8 evenly spread points (Halton 2,3),
# picked per frame: a random offset bunched up and left gaps, so the history never settled evenly. Irn_Jitter_Px is
# also there for pixel shaders: the TAA pass reads the frame back where it really belongs (irancoj_taa_ps.hlsl).
jitter = (
    '        //IranCoJ Edition: TAA jitter - the scene a sub-pixel off, a new offset each frame' + N +
    '        #if defined(IRN_TAA)' + N +
    '            #define IRN_TAA_JITTER_PX 1   // irancoj_taa_ps.hlsl un-shifts the frame only when this is here' + N +
    '            // this frame\'s offset in pixels (x right, y up), within half a pixel' + N +
    '            float2 Irn_Jitter_Px()' + N + '            {' + N +
    '                float f_i = floor(frac(sin(floor(TIME * 997.0) * 12.9898) * 43758.5453) * 8.0);' + N +
    '                float2 v_j = float2(0.0625, 0.8889);' + N +
    '                v_j = (f_i < 6.5) ? float2(0.875, 0.5556) : v_j;' + N +
    '                v_j = (f_i < 5.5) ? float2(0.375, 0.2222) : v_j;' + N +
    '                v_j = (f_i < 4.5) ? float2(0.625, 0.7778) : v_j;' + N +
    '                v_j = (f_i < 3.5) ? float2(0.125, 0.4444) : v_j;' + N +
    '                v_j = (f_i < 2.5) ? float2(0.75, 0.1111) : v_j;' + N +
    '                v_j = (f_i < 1.5) ? float2(0.25, 0.6667) : v_j;' + N +
    '                v_j = (f_i < 0.5) ? float2(0.5, 0.3333) : v_j;' + N +
    '                return v_j - 0.5;' + N + '            }' + N +
    '        #endif' + N +
    '        #if defined(IRN_TAA) && defined(VERTEXSHADER) && !defined(TECH_SHD_ON) && !defined(TECH_RFL_ON)' + N +
    '            float4 Irn_Jitter(float4 v_pos)' + N + '            {' + N +
    '                v_pos.xy += Irn_Jitter_Px() * 2.0 * RENDER_TARGET_PARAMS.xy * v_pos.w;' + N +
    '                return v_pos;' + N + '            }' + N +
    '        #else' + N + '            #define Irn_Jitter(v) (v)' + N + '        #endif' + N + N)
rewrites.append(rw('Data/Shaders/Common/common.hlsl', D1, 'Data/Shaders/Common/common.hlsl', [
    (r'(?m)^(?=[ \t]*float4 Pos_Out\(float4 v_pos\))', '#define IRN_TAA 1' + N + jitter),
    (r'return Mul44\(v_pos, COMBINED_XFORM\);', 'return Irn_Jitter(Mul44(v_pos, COMBINED_XFORM));'),
    (r'(float4 Pos_Out_WS\(float4 v_pos\)\s*\{\s*)return Mul44\(v_pos, VIEWPROJ_XFORM\);', '$1return Irn_Jitter(Mul44(v_pos, VIEWPROJ_XFORM));'),
    (r'(float4 Pos_Out_CS\(float4 v_pos\)\s*\{\s*)return Mul44\(v_pos, PROJECTION_XFORM\);', '$1return Irn_Jitter(Mul44(v_pos, PROJECTION_XFORM));')
], when=TAA))

# Light shafts (the mod's irancoj_shafts_ps.hlsl / .mat), in place of the game's sun rays: drawn at a quarter of the
# screen into the glow (glow_30.ppfx), where each pixel walks towards the sun and gathers the open sky it passes, so
# light streams past roofs, trees and hills; the glow's own blur, the tone mapping and TAA smooth it. Tested in game
# at 1080p and 1440p: no measurable cost. The template is the player's blur_camera_motion.mtt (as for TAA), added.
SHAFTS = {'shafts': ['on']}
rewrites.append(rw('Data/Shaders/postprocess/irancoj_shafts.mtt', D1, 'Data/Shaders/postprocess/blur_camera_motion.mtt', [
    (r'BlendFunc\(SRC_ALPHA, INV_SRC_ALPHA, ONE, ONE\);', 'BlendFunc(ONE, ONE); //IranCoJ Edition: light shafts are added to the glow'),
    (r'(?s)extern float FPS;.*?Define\("I_SAMPLES", i_samples\);', '//IranCoJ Edition: no constants (the motion blur\'s are not used)'),
    (r'(?s)int i_cst_i_current = i_const_int_first;.*?Define\(s_cst_name \+ "000", s_cst_000\);', '//IranCoJ Edition: no constants'),
    (r'use PP_TMU\(s_sampler = "s_clr", i_user_map = 8, e_filter = LINEAR_NO_MIP, e_tile = MIRROR\);',
     'use PP_TMU(s_sampler = "s_clr", i_user_map = 8, e_filter = LINEAR_NO_MIP, e_tile = CLAMP);'),
    (r'#include <blur_camera_motion_ps\.hlsl>', '#include <irancoj_shafts_ps.hlsl>')
], when=SHAFTS))
rewrites.append(rw('Data/Postprocess/Effects/glow_30.ppfx', D0, 'Data/Postprocess/Effects/glow_30.ppfx', [
    # the game's sun rays: their mask, and the slices added to the glow
    (r'(?s)// SUN RAYS\s*If\("f_sun_rays_factor".*?\n\}\s*', ''),
    (r'(?s)(QuadScreen\("add\.mat", "std", 4\))\s*If\("f_sun_rays_factor".*?\n        \}',
     '$1' + N + N + '        //IranCoJ Edition: light shafts (irancoj_shafts.mat) in place of the game\'s sun rays' + N +
     '        SetTexture(8, "4B")' + N + '        SetTexture(9, "DPT")' + N + '            QuadScreen("irancoj_shafts.mat", "std", 4)')
], when=SHAFTS))

# Distant haze, in the game's own fog pass (fog_pp_ps.hlsl): beyond 100 m, in the map's fog colour (the same colour
# the map's fog has in that direction, sun glow included), its density falling off with height above the camera -
# valleys and a town seen from a hill get hazier, hills and the skyline less. Play distances stay clear (asked for:
# a competitive shooter must not lose visibility; 20 m and double the density was too much).
rewrites.append(rw('Data/Shaders/postprocess/fog_pp_ps.hlsl', D1, 'Data/Shaders/postprocess/fog_pp_ps.hlsl', [
    (r'(OUT\.v_clr = Fog\(f_cam_dir_length, normalize\(-v_cam_dir\), vSunDir\);)', '$1' + N + N + N.join([
        '    //IranCoJ Edition: distant haze - thicker below the camera (valleys, a town seen from a hill), thinner above',
        '    // (hills, the sky line), in the map\'s own fog colour; nothing within IRN_HAZE_START. The density falls off',
        '    // exponentially with height, integrated along the view: d0 * exp(-k * height above the camera).',
        '    #define IRN_HAZE_DENSITY 1.2e-6   // per cm, at the camera\'s height',
        '    #define IRN_HAZE_FALLOFF 2.5e-4   // per cm of height (it halves every 28 m up)',
        '    #define IRN_HAZE_START   10000.0  // cm: nothing nearer (play distances stay clear)',
        '    float f_irn_s = min(IRN_HAZE_START, f_cam_dir_length);',
        '    float f_irn_a = IRN_HAZE_FALLOFF * -v_cam_dir.y / max(f_cam_dir_length, 1.0);',
        '    float f_irn_tau = (abs(f_irn_a) > 1e-8)',
        '        ? (exp(clamp(-f_irn_a * f_irn_s, -30.0, 30.0)) - exp(clamp(-f_irn_a * f_cam_dir_length, -30.0, 30.0))) / f_irn_a',
        '        : f_cam_dir_length - f_irn_s;',
        '    OUT.v_clr.w *= exp(-IRN_HAZE_DENSITY * max(f_irn_tau, 0.0));']))
], when={'haze': ['on']}))

# Materials that lived only in the rpacks' precompiled caches (hidden in Remastered mode so the remastered shader
# sources are compiled): rebuilt from the player's own files.
rewrites.append(rw('Data/Shaders/postprocess/lighting_pp_stencil_simple.mat', D1, 'Data/Shaders/postprocess/lighting_pp_stencil.mat', [
    (r'use mtt\(b_stencil_on = TRUE\);', 'use mtt(b_stencil_on = TRUE, b_simple_on = TRUE); //IranCoJ Edition: the Simple pipeline rain lighting')
]))
rewrites.append(rw('Data/FX/fx_long_trace.mat', D0, 'Data/FX/trace.mat', [
    # at the end: the material parser wants its directives first (a comment before !include is a syntax error)
    (r'\z', N + '//IranCoJ Edition: the long bullet traces the engine asks for, as trace.mat' + N)
]))
# ChromEd writes a map's river material only into the map's rpack cache (Tombstone: no source in any pak, nor in its
# editor files), so hidden it drew as the engine's default - a glowing yellow river. Rebuilt on the game's river
# template with the values read out of TombStone.rpack's compiled copy (its constants and transforms): a murky
# green-grey river, opaque at 80 cm. The one change: the reflection is the map's own cubemap (s_water_cubemap,
# tombstone_rfl.dds in Data2) - the original's Battle_river_big_rfl is only in textures1.rpack, which the HD pack
# (needed for Remastered) turns off. The map CRC doesn't cover materials.
tombstone_river = N.join([
    'import "liquid.mtt"',
    '',
    'sub material()',
    '{',
    '    extern float TIME;',
    '    extern string s_water_cubemap;',
    '',
    '    mtx m_nrm_0_xfm = translate( 0.3  * TIME, -0.0106 * TIME, 0.0) * rotate(0.0, 0.0,  5.0) * scale(3.2,  1.3, 1.0);',
    '    mtx m_nrm_1_xfm = translate(-0.3  * TIME, -0.0114 * TIME, 0.0) * rotate(0.0, 0.0, -2.0) * scale(3.24, 1.2, 1.3);',
    '    mtx m_nrm_2_xfm = translate( 0.04 * TIME, -0.009  * TIME, 0.0) * rotate(0.0, 0.0,  7.0) * scale(0.5,  0.6, 1.2);',
    '    mtx m_nrm_3_xfm = translate(-0.04 * TIME, -0.01   * TIME, 0.0) * rotate(0.0, 0.0, -7.0) * scale(0.67, 0.4, 0.025);',
    '',
    '    use mtt_liquid(',
    '        e_opq_order = or_seetrough_1,',
    '        e_nrm_order = 2,',
    '        e_trn_order = 2,',
    '        e_bdf_order = 2,',
    '',
    '        f_blend_distance = 16.0,',
    '',
    '        v_deep_color = [0.42, 0.45, 0.3],',
    '        f_deep_distance = 80.0,',
    '        f_deep_opacity = 0.95,',
    '',
    '        f_deform_strength = 0.2,',
    '        f_deform_falloff = 2500.0,',
    '',
    '        s_env = s_water_cubemap,',
    '        v_env_factor = [0.72, 0.724, 0.718],',
    '        f_env_fresnel_power = 2.0,',
    '',
    '        v_liquid_clr = [1.0, 1.0, 1.0, 0.0],',
    '',
    '        s_nrm_0 = "water_waves_n.dds",',
    '        f_nrm_0_scale = 0.4,',
    '        m_nrm_0_xfm = m_nrm_0_xfm,',
    '        s_nrm_1 = "water_waves_n.dds",',
    '        f_nrm_1_scale = 0.5,',
    '        m_nrm_1_xfm = m_nrm_1_xfm,',
    '        s_nrm_2 = "water_waves_2_n.dds",',
    '        f_nrm_2_scale = 1.0,',
    '        m_nrm_2_xfm = m_nrm_2_xfm,',
    '        s_nrm_3 = "water_waves_2_n.dds",',
    '        f_nrm_3_scale = 1.0,',
    '        m_nrm_3_xfm = m_nrm_3_xfm,',
    '',
    '        f_spc_power = 555.0',
    '    );',
    '}',
    '',
    '//IranCoJ Edition: Tombstone\'s river, rebuilt from its compiled copy in TombStone.rpack (no source exists)',
    ''])
rewrites.append(rw('Data/MapsNet/Tombstone/river/tombstone_river.mat', D1, 'Data/Shaders/master/Templates/river_a.mat', [
    (r'(?s)\A.*\z', tombstone_river)
]))

def liquid(note, nrm, env, deep, deep_distance, fresnel, deform, shadows=None, deep_opacity=None, blur=None, env_tex=None):
    """A water material on liquid.mtt with the values read out of a compiled copy. nrm: (texture, scale, translate x,
    translate y, rotate, scale xyz) per normal map; fresnel (scale, bias, power); deform (strength, distance, falloff);
    blur (strength, distance, falloff, falloff shift, fresnel power) or None; env_tex: the reflection cubemap (else the
    map's s_water_cubemap)."""
    num = lambda x: repr(float(x))
    vec = lambda v: '[' + ', '.join(num(x) for x in v) + ']'
    lines = ['import "liquid.mtt"', '', 'sub material()', '{', '    extern float TIME;', '    extern string s_water_cubemap;', '']
    for i, (_, _, tx, ty, rot, sc) in enumerate(nrm):
        lines.append(f'    mtx m_nrm_{i}_xfm = translate({num(tx)} * TIME, {num(ty)} * TIME, 0.0) * rotate(0.0, 0.0, {num(rot)}) '
                     f'* scale({num(sc[0])}, {num(sc[1])}, {num(sc[2])});')
    args = ['e_opq_order = or_seetrough_1', 'e_nrm_order = 2', 'e_trn_order = 2', 'e_bdf_order = 2',
            'f_blend_distance = 16.0', f'v_deep_color = {vec(deep)}', f'f_deep_distance = {num(deep_distance)}']
    if deep_opacity is not None:
        args.append(f'f_deep_opacity = {num(deep_opacity)}')
    args += [f'f_deform_strength = {num(deform[0])}', f'f_deform_distance = {num(deform[1])}']
    if deform[2]:
        args.append(f'f_deform_falloff = {num(deform[2])}')
    if blur:
        args += [f'f_blur_strength = {num(blur[0])}', f'f_blur_distance = {num(blur[1])}', f'f_blur_falloff = {num(blur[2])}',
                 f'f_blur_falloff_shift = {num(blur[3])}', f'f_blur_fresnel_power = {num(blur[4])}']
    if shadows:
        args.append(f'e_shadows = {shadows}')
    args += [f's_env = "{env_tex}"' if env_tex else 's_env = s_water_cubemap', f'v_env_factor = {vec(env)}', f'f_env_fresnel_scale = {num(fresnel[0])}',
             f'f_env_fresnel_bias = {num(fresnel[1])}', f'f_env_fresnel_power = {num(fresnel[2])}',
             'v_liquid_clr = [1.0, 1.0, 1.0, 0.0]']
    for i, (tex, scale, *_ ) in enumerate(nrm):
        args += [f's_nrm_{i} = "{tex}"', f'f_nrm_{i}_scale = {num(scale)}', f'm_nrm_{i}_xfm = m_nrm_{i}_xfm']
    args.append('f_spc_power = 555.0')
    lines += ['    use mtt_liquid(', ',\r\n'.join('        ' + a for a in args), '    );', '}', '', '//IranCoJ Edition: ' + note, '']
    return N.join(lines)


# The Battle river (Civil.rpack's compiled copy; also in Battle, Medallion and Villa Attack; community maps' copies
# such as harbor_water.mat carry the same values): a dark river, opaque at 379 cm. Its reflection
# Battle_river_big_rfl is only in textures1.rpack (off with the HD pack), and so is Civil's own s_water_cubemap
# (VillageDefend_rfl; civil.scr is in the map CRC): without one the river is a flat green swamp. Frisco_rfl (Data2)
# instead, a river-side sky - blue sky and clouds over green banks.
battle_river = liquid('the Battle river, rebuilt from its compiled copy in Civil.rpack (no source exists)',
                      nrm=[('water_waves_n.dds', 2.0, 0.08, 0.051, 5.0, (16.0, 0.55, 1.0)),
                           ('water_waves_2_n.dds', 2.5, -0.01, -0.03, -2.0, (16.4, 0.52, 1.3)),
                           ('water_waves_n.dds', 1.5, -0.081, 0.055, -5.0, (14.0, 0.5, 1.2)),
                           ('water_waves_2_n.dds', 2.0, 0.001, 0.005, -1.0, (0.4, 0.025, 0.025))],
                      env=(0.22, 0.2, 0.2), deep=(0.12, 0.13, 0.08), deep_distance=379.0, deep_opacity=1.0,
                      fresnel=(1.5, 0.5, 1.0), deform=(0.25, 100.0, 2500.0), shadows='e_shadows_pp_simple',
                      blur=(1.0, 500.0, 5000.0, 500.0, 1.0), env_tex='Frisco_rfl.dds')
# Juarez's water (Juarez.rpack's compiled copy): two normal maps, opaque at 100 cm, no shadows. Its Juarez_rfl is
# only in textures1.rpack too.
juarez_water = liquid('Juarez\'s water, rebuilt from its compiled copy in Juarez.rpack (no source exists)',
                      nrm=[('water_waves_n.dds', 0.5, 0.08, 0.051, 5.0, (16.0, 0.55, 1.0)),
                           ('water_waves_n.dds', 0.5, -0.081, -0.055, -5.0, (14.0, 0.5, 1.2))],
                      env=(0.26, 0.27, 0.25), deep=(0.14, 0.15, 0.1), deep_distance=100.0, deep_opacity=1.0,
                      fresnel=(1.5, 0.5, 1.0), deform=(0.2, 32.0, None), shadows='e_shadows_none',
                      env_tex='Frisco_rfl.dds')
for path, text in [('Data/Maps/Battle/River/battle_river_a.mat', battle_river),   # Civil, Fort Stanton
                   ('Data/Maps/Battle/River/battle_river_b.mat', battle_river),   # Battle Camp (no compiled copy: as _a)
                   ('Data/Maps/Juarez/Water/juarez_water_a.mat', juarez_water)]:  # Fort Stanton
    rewrites.append(rw(path, D1, 'Data/Shaders/master/Templates/river_a.mat', [(r'(?s)\A.*\z', text)]))

# The other water materials maps name (their .exp files) with no source in any pak and no compiled copy in any of
# the game's rpacks (vanilla drew them as the default material too): each from the game's nearest template.
for path, template in [
        ('Data/Maps/Battle/River/battle_shore.mat', 'shore_a'),            # McCall's Villa
        ('Data/Maps/Battle/River/battle_water_flat_b.mat', 'water_flat_b'),  # McCall's Villa
        ('Data/Shaders/Liquid/Templates/water_shore_a.mat', 'shore_a'),    # Civil, Frisco, Prison Break 2
        ('Data/World/water_shore.mat', 'shore_a'),                         # Adobes, Coffeyville, Magnificent, ...
        ('Data/Shaders/Water/water_default.mat', 'water_a')]:              # The Dungeon
    rewrites.append(rw(path, D1, f'Data/Shaders/master/Templates/{template}.mat', [
        (r'\z', N + f'//IranCoJ Edition: this material is only in the rpack caches; the game\'s {template}.mat in its place' + N)
    ]))

# Depth of field: the No DOF & Motion Blur mod switches it off by taking the fDOF* variables out of varlist_pp.scr, so
# dofs.mtt's "extern float fDOF..." fails, and with it every depth_effects_*.mat that imports it. Vanilla never
# notices (it uses the rpack caches), but compiled from source the rain variant drew the engine's default material
# over the whole screen. The game's own values, DOF power 0, in place of the externs: it compiles with or without
# the mod, and the DOF stays off (in Remastered also without the mod).
rewrites.append(rw('Data/Shaders/postprocess/dofs.mtt', D1, 'Data/Shaders/postprocess/dofs.mtt', [
    (r'extern float fDOFdistance;', 'float fDOFdistance = 500.0; //IranCoJ Edition: not extern (the No DOF mod removes the variables)'),
    (r'extern float fDOFFarDistance;', 'float fDOFFarDistance = 2.0;'),
    (r'extern float fDOFNearDistance;', 'float fDOFNearDistance = 0.5;'),
    (r'extern float fDOFFarOffset;', 'float fDOFFarOffset = 1.0;'),
    (r'extern float fDOFNearOffset;', 'float fDOFNearOffset = 1.0;'),
    (r'extern float fDOFpower;', 'float fDOFpower = 0.0;')
]))

graphics = {
    'version': '1.1.8',
    'rewrites': rewrites,
    'vegetation': {
        'files': ['_grass.scr', '_foliage.scr'],
        'scale': [r'(?<=(?:GenerationRange|ReleaseRange|ExtinctionDistance|ExtinctionRange|BlendRange)\(\s*)(?<n>\d+(?:\.\d+)?)'],
        'replace': [[r'MaxShadowMapIndex\(\s*0\s*\)', 'MaxShadowMapIndex(3)']]
    }
}

raw = open(EDITION, encoding='utf-8').read()
spec = json.loads(raw)
spec['graphics'] = graphics
nl = '\r\n' if '\r\n' in raw else '\n'
out = json.dumps(spec, indent=2, ensure_ascii=False) + '\n'
open(EDITION, 'w', encoding='utf-8', newline='').write(out.replace('\n', nl))
print('graphics: %d rewrites' % len(rewrites))
