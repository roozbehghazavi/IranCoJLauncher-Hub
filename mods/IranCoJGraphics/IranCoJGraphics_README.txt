IranCoJ Graphics 1.5.1 - the Edition's remastered graphics, by Thomas (Roozbeh).

Everything is set in the IranCoJ Launcher: Settings > Graphics & Sound > Remastered or Vanilla, and each feature on
its own in the Remastered group. The launcher writes irancojfx.ini and edited copies of the game's own pipeline
scripts and shaders (from your install); Vanilla removes them again. Nothing of the game itself is shipped.

- Lighting: GGX sun highlights (physically based shine from the game's own shininess maps), metal that reflects the
  sun in its own colour, ground-truth ambient occlusion (GTAO), soft 5x5 shadow edges on a 4096 shadow map with a
  shadow bias that keeps small shadows (window sills, frames) at every distance.
- Image: temporal anti-aliasing (stable edges, no shimmer on wires, fences and foliage; the game's own MSAA is turned
  off with it), FXAA 3.11 quality edge smoothing, sharpening, filmic tone mapping and a light colour grade.
- Distance: every map's baked detail and draw distances scaled as the map loads (irancojfx.dll, nothing written to
  disk), vegetation drawn three times further, shadow cascades and culling, 16x texture filtering.
- So the remastered shaders run: the precompiled shaders in the game's rpacks are hidden in Remastered mode (named
  back in Vanilla), and the Edition's exe may use 4 GB.

irancojfx.dll also logs every shader the engine fails to compile to irancojfx.log (with irancojfx_shader_fail_*.hlsl
next to it), for anyone working on the shaders.

1.1.1: joining servers with Remastered on works again: the map check the game runs before loading a map (the
"wrong map crc" error) now reads the map files as they are, not with the scaled distances.

1.2.0: temporal anti-aliasing works: no shaking when still, no trails when moving. The engine keeps last frame's
camera only for its motion blur, so irancojfx.dll keeps it; the pass reads the full-resolution depth, rebuilds each
pixel's position the right way round, keeps the first-person weapon in place, drops history the weapon covered and
trusts history less the further a pixel moved. Tombstone and other maps' water no longer glows yellow.

1.2.1: rain maps (Utah, mp23 and others) are no longer smeared grey in Remastered: the depth effects compile
even with No DOF & Motion Blur installed. The map's baked lighting is always read as it is on disk.


1.2.2: temporal anti-aliasing holds still at every resolution: the frame is read back where it really belongs
(it is drawn up to half a pixel off each time, from 8 evenly spread offsets), so distant detail no longer shakes at
low resolutions. Shadows no longer flicker on ground and objects: the shadow pass aims at the real surface. Moving
is sharper: the history and the new frame are read with a sharp filter, not blurred a little more each frame.

1.2.3: thin edges (roofs, rock rims) no longer flicker with temporal anti-aliasing at low resolutions: the
history gets a little slack before it is held to the pixels around it, bright pixels weigh less in the blend, and
the blend is a touch smoother.

1.3.0: the game draws through Vulkan with DXVK 3.1.1 (dxvk/, zlib licence, by Philip Rebohle and the DXVK
contributors). The launcher puts its d3d9.dll next to the game when the PC has a graphics card with Vulkan 1.4
(Settings > Display > Renderer; DirectX 9 otherwise), points it at the dedicated card on laptops and turns vertical
sync off once. Frame times are much steadier: no more 100 ms stalls during play. Temporal anti-aliasing no longer
leaves a copy of your gun on the wall when it moves while you stand still (reloading).

1.4.0: render resolution (Settings > Graphics > Remastered, with temporal anti-aliasing): the world is drawn at
85%, 75% or 67% of your resolution and temporal anti-aliasing rebuilds it at full size - more frames per second, the
HUD and text stay sharp. irancojfx.dll sizes the engine's post-process buffers and full-screen passes to the scale;
the Edition's exe (1.3.0) loads it at start, before the engine creates those buffers.

1.4.1: sharpening is AMD FidelityFX Super Resolution 1's RCAS (MIT licence, (c) 2021 Advanced Micro Devices, Inc.):
crisper after an upscale, no halos. Temporal anti-aliasing keeps each pixel's depth in its history (half floats) and
drops history whose depth doesn't match - players running past no longer leave a trail or a ghost.

1.5.0: light shafts and distant haze (Settings > Graphics > Remastered, each on its own). Light shafts take the
place of the game's sun rays: looking towards the sun, light streams past roofs, trees and hills (a quarter-size
pass into the game's glow, from the depth and the open sky). Distant haze adds a light haze in the map's own fog
colour beyond 100 m, thicker in low ground - play distances stay clear. Neither costs a measurable frame rate.

1.5.1: temporal anti-aliasing keeps its history the same length of time at any frame rate. At a fixed share per
frame it lasted about a second at 13 fps, and moving players (and their name tags) smeared like jelly; at a low
frame rate each new frame now counts for more (8% at 60 fps, about 32% at 13).
