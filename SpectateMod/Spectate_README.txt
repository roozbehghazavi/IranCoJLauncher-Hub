IranCoJ Spectate  v1.0.7 beta
=============================

Spectate other players while you are dead, from the multiplayer class-selection
screen. Third person by default, first person optional.


WHAT'S NEW IN 1.0.7
-------------------
* Coming back from spectate, the buttons answer straight away. They used to be
  dead for about four seconds.
* SPECTATE is pressed the way every other button on the screen is pressed, so
  it behaves the same at any resolution. Pressing UPGRADE or changing class can
  no longer start spectating by mistake.

WHAT WAS NEW IN 1.0.6
---------------------
* Fixed spectate starting by itself when you pressed UPGRADE or changed class.
  The buttons share a row with SPECTATE, and a second cursor reading used the
  wrong coordinate space - so a click 500 pixels away still counted as a press
  on SPECTATE whenever the two happened to agree on height. That reading is
  gone; only the position the game itself reports is used now.

AND IN 1.0.5
------------
* SPECTATE is now an ordinary button. A click only counts when it lands on the
  button itself. Clicking anywhere else no longer activates whichever button
  happens to be highlighted - which is what made stray clicks start spectating,
  or flick through players, when you meant to pick a class.
* The button finds itself. Its position and size are measured from the menu at
  the moment you click, instead of being hard-coded. It therefore keeps working
  if the class screen is re-laid-out by another mod.
* The mouse is only ever held back while you are actually spectating. Nothing
  else can trigger it.

AND IN 1.0.4
------------
* Fixed the big one. Clicking SPECTATE while you were alive used to put the
  spectate bar up carrying a "you have to be dead first" message. That bar
  hides the class screen, blocks the mouse and takes over clicks - so one
  press, often an accidental one, left you unable to pick a class, unable to
  shoot, and with further clicks changing spectated players until you died.
  The button now simply does nothing while you are alive. Nothing is hidden,
  nothing is blocked.
* The mouse is never blocked except while you are actually spectating.

AND IN 1.0.3
------------
* Fixed the mouse going dead mid-match. Spectate could arm itself during the
  moment you are respawning - the game briefly looks the same as being dead -
  and if it did, mouse BUTTONS stayed blocked for the rest of the match. You
  could still look and move, but not shoot.
* Fixed the engine's debug boxes and lines sticking to a player for the rest of
  the match after that happened.
* Spectate no longer opens by itself while you are respawning.

AND IN 1.0.2
------------
* Closed doors now stop the camera. In 1.0.1 the camera collided with walls but
  went straight through doors, which gave away the inside of a building just as
  badly.
* The camera no longer slips through a wall you are standing against. It could
  drift out through the wall for a moment and then snap back; that is gone.

AND IN 1.0.1
------------
* Third-person camera collides with the world. Indoors it pulls in towards
  the player instead of passing through walls, so it can no longer be used to
  see into rooms you are not in.


INSTALL
-------
Copy the contents of this archive into your Call of Juarez: Bound in Blood
folder, keeping the folder structure. The files land like this:

    Call of Juarez Bound in Blood\
        dinput8.dll                     <- mod loader (replaces the old one)
        spectate.dll                    <- the spectate mod
        mods.txt                        <- list of mods to load

That's all. No launcher, no config, nothing to enable.

THE MENU PACK IS NOT IN THIS ARCHIVE, ON PURPOSE.

The SPECTATE button lives in a menu pack file
(CoJ2\Data\Menu\MenuIngameNetGamemode_Scr_PC.binui). It only ever needs
installing once, and other IranCoJ mods - the New Classes mod in particular -
put their own entries in that same file. If every Spectate update shipped it,
updating Spectate would quietly wipe the New Classes rows from your class
screen and you would have to install that mod again.

So:

  * Updating from an earlier Spectate, or you already run New Classes?
    This archive is all you need. Your menu pack already has the button.

  * Never installed Spectate or New Classes before?
    Also get IranCoJ_Spectate_MenuPack.zip and copy that in as well, once.
    Without it there is no SPECTATE button to press.

  * mods.txt is safe to copy over. It lists spectate.dll, voicechat.dll and
    directjoinfix.dll; any of those you do not have installed is skipped
    without complaint, so you end up with whichever mods you actually own.
    If you run something else as well (tppcam.dll, headhide.dll, ...), add its
    line back to mods.txt after copying.

  * dinput8.dll must be REPLACED, not skipped, even if you already have one.
    The mouse-button blocking lives in this file, not in spectate.dll. With an
    older loader the mod still runs, but a red marker appears while spectating
    and right-clicking damages players. If that happens to you, you skipped
    this file.

To uninstall, delete spectate.dll and remove its line from mods.txt. Keeping
the new dinput8.dll and the menu pack is harmless.


HOW TO USE
----------
1. Join a multiplayer match.
2. On the class-selection screen, press SPECTATE (next to the class buttons).
   While you are alive the button does nothing - spectating starts only once
   you are dead.
3. Once you are dead, the spectate bar appears:

       at the top:      <   [ watched player's name ]   >
       at the bottom:   BACK                        FPP/TPP

       BACK       return to class selection (ESC does the same)
       < and >    previous / next player
       FPP/TPP    switch between first and third person

The name strip sits at the top so it does not cover the chat panel.

In team modes you can only watch your own team. This is deliberate: watching
the other side would let a dead player call out enemy positions to their team.


THIRD PERSON vs FIRST PERSON
----------------------------
Third person is the default. It is built from the player's replicated position
and is rock solid. The camera collides with the world, so indoors it pulls in
towards the player rather than passing through walls.

First person sits on the engine's own eye position and follows the player's
real up/down aim, read from the game's own aim value - so when they look up,
you look up.

Two things first person cannot do, because of how the game draws players:

  * Their weapon is mostly out of frame. In first person the game draws a
    special weapon model that exists only for the player holding it. As a
    spectator you see their world model, whose gun is held at hip height.
  * Their shadow has no head, for you only. The head is hidden so it does not
    fill your screen, and a hidden part casts no shadow. Other players, and the
    player you are watching, see a perfectly normal character.


NOTES
-----
* Replaces one menu pack, MenuIngameNetGamemode_Scr_PC.binui, which is the one
  holding the class-selection screen. Nothing else in the menus is touched. If
  you have another mod that changes that same file, the two will conflict.
* Does not change gameplay, weapons, health, skins or any character. Nothing
  here affects what other players see.
* Writes no log files.
* Safe alongside the IranCoJ Skin Pack.
* Works at any resolution and any frame rate.


KNOWN LIMITATIONS
-----------------
* On servers that send few updates per second, the camera can look slightly
  stepped while a player moves. The mod measures the server's update rate and
  adapts its smoothing, but it cannot invent data that never arrived. On a
  healthy server this is not visible.
* Spectating starts only after you die, by design.
* The menu pack carries the SPECTATE button itself, and it ships separately so
  that updating Spectate never overwrites the class-screen entries belonging
  to other IranCoJ mods. See INSTALL.
* Chat is not shown while spectating. It lives on the scoreboard panel, which
  the game only draws while TAB is held, so it is not ours to move.
* Holding certain keys while spectating draws the engine's leftover debug
  overlays - boxes around bones, lines, screen blur. Harmless, affects only
  your own screen, and goes away when you stop holding the key.
* Coming back from spectate there is a brief moment - about a third of a
  second - before the class screen answers clicks again.

This is a beta. If something misbehaves, tell us what you did just before it
happened - that is usually enough to find it.

IranCoJ community.
