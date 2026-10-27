IranCoJ New Classes 2.0.3 (with the IranCoJ Skin Pack) - manual install (Linux / Wine, or without the installer)
====================================================================================================================

1. Copy everything in this zip into the game folder (the one with CoJBiBGame_x86.exe), merging folders and
   allowing files to be replaced.

2. Rename these two files in <game>/CoJ2/Data (add ".disabled" at the end):
     common_mp_meshes.rpack   ->  common_mp_meshes.rpack.disabled
     menu_ingame_net.rpack    ->  menu_ingame_net.rpack.disabled
   Without this the game uses its packed skins and menu pictures instead of the new ones.
   (If they already end in .disabled from the skin pack, leave them as they are.)

3. Linux (Wine / Proton) only: the mods load through dinput8.dll, which Wine ignores unless told to use it.
     Steam (Proton): game Properties > Launch Options:   WINEDLLOVERRIDES="dinput8=n,b" %command%
     Lutris / plain Wine: set the environment variable WINEDLLOVERRIDES=dinput8=n,b
                          (or winecfg > Libraries > add "dinput8" as "native, builtin")
   Check: put an empty file named newclasses_log.on in the game folder and start the game - newclasses.log
   appears next to it (delete both afterwards: without newclasses_log.on the mod writes no log).

mods.txt lists the client mods dinput8.dll loads (spectate, voicechat, directjoinfix, newclasses); the ones
you don't have are skipped. If you already have a mods.txt, make sure "newclasses.dll" is in it.

shadercache/ holds shaders the game would otherwise compile on the spot (the freezes when someone respawns);
new ones are added there as you play. It is safe to delete - it just fills again.

Uninstall: delete newclasses.dll (or its line in mods.txt) and the shadercache folder, rename the two .disabled
files back, and remove the files this zip added under CoJ2/Data.
