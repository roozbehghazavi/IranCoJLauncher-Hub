IranCoJ Graphics 1.2.1 - the Edition's remastered graphics, by Thomas (Roozbeh).

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
