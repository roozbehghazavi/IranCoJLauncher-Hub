IranCoJ Skin Pack v2.1.0 - singleplayer characters on the multiplayer classes
============================================================================

Run the setup and point it at your CoJ2 folder - it finds it on its own
if the game is installed normally. Nothing else to do.

To remove it, use Apps & Features, or run unins000.exe in this folder.
The uninstaller deletes every file the mod added and puts the mesh bundle
back. Do not just rename the rpack by hand: with the loose skin files
still present the game draws every submesh at once and characters come
out as a pile of overlapping faces.

WHAT YOU GET
------------
  class      free-for-all         team modes           voice
  --------------------------------------------------------------------
  Hombre     Juarez               (same)               Juarez
  Miner      Rattler              (same)               Rattler
  Native     RunningRiver         (same)               Native01
  Officer    Barnsby              BarnsbyTeam          Barnsby
  Rifleman   Professional_A_Coat  Professional_A_Coat  -
  Scout      SeeingFarther        (same)               SeeingFarther
  Sniper     PumaPaw              (same)               Native01
  Spy        William              WilliamTeam          William
  Trapper    ODonell              (same)               Boss
  Veteran    Thomas               (same)               Thomas
  Vigilante  Ray                  RayTeam              Ray

Each class also gets its own death and pain voice from the singleplayer
cast. No weapon or map changes: the class scripts are the dedicated
server's own copies, so the client agrees with the server on every value
that is not a skin or a voice.

Your own head and hat are hidden from your own view the way the game does
it for the stock classes: the _player variant of each skin pulls in
man_player.skt, which makes the head materials invisible. The head mesh
stays, so your shadow still has one and everyone else sees you normally.

CHANGING A SKIN
---------------
Everything is plain text under Data\Player. Net_<class>_up0.scr holds the
SkinName used in free-for-all; Net_<class>_Blue_up0.scr and the _Red_ one
hold the team-mode skin. skins.txt lists every name that works and marks
which accept the blue/red team tint.

A name that does not resolve is a hard crash on this engine, not a
fallback, so copy them exactly - capitals included.

Report problems with: the class, the game mode, and the map.
