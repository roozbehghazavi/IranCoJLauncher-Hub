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
    (r'\A', '#define IRN_GGX 1 //IranCoJ Edition: GGX sun specular (irancoj_ggx.hlsl)' + N)
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

graphics = {
    'version': '1.0.0',
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
