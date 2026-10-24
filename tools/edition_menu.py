"""Source of the Edition's compiled menu packs in edition/files/CoJ2/Data/Menu.

Reads the original .xui files from a player's Data0.pak and writes edited copies into a scratch Edition's
CoJ2/Data/Menu/scr. Compile them there: debugconf.scr with ForceUiFromXML() + SaveUiPacks("PC"), start the
game, quit with the menu's Quit button. Then ship only MenuCommon_Scr_PC.binui (rewritten in place) and
MenuMain_Scr/Skn_PC.binui (written to Documents) - never the other packs the compile rewrites.
Test in a real Edition, in normal mode (hosting crashes in compile mode).

    python tools/edition_menu.py "<game>/CoJ2/Data0.pak" "<scratch edition>/CoJ2/Data/Menu/scr"
"""

import os
import re
import sys
import zipfile

pak, out = sys.argv[1], sys.argv[2]
z = zipfile.ZipFile(pak)
read = lambda name: z.read("Data/Menu/scr/" + name).decode("latin1")


def block(text, element_id):
    """The whole <UINaviButton>…</UINaviButton> (or other element) whose Properties start with this Id."""
    m = re.search(r"<(\w+)>\r?\n<Properties>\r?\n<Id>" + re.escape(element_id) + r"</Id>.*?</\1>\r?\n", text, re.S)
    if not m:
        raise SystemExit(f"{element_id} not found")
    return m


def set_prop(text, element_id, prop, value):
    """Sets (or adds, right after Id) a property inside one element's Properties."""
    m = block(text, element_id)
    b = m.group(0)
    if re.search(f"<{prop}>.*?</{prop}>", b):
        b = re.sub(f"<{prop}>.*?</{prop}>", f"<{prop}>{value}</{prop}>", b, count=1)
    else:
        b = b.replace(f"<Id>{element_id}</Id>", f"<Id>{element_id}</Id>\r\n<{prop}>{value}</{prop}>", 1)
    return text[:m.start()] + b + text[m.end():]


def drop_prop(text, element_id, prop):
    m = block(text, element_id)
    b = re.sub(f"<{prop}>.*?</{prop}>\r?\n", "", m.group(0), count=1)
    return text[:m.start()] + b + text[m.end():]


def nav(text, element_id, up, down):
    for prop, value in (("NavUp", up), ("NavTabBackward", up), ("NavDown", down), ("NavTabForward", down)):
        text = set_prop(text, element_id, prop, value)
    return text


def pos(y, x="80.000000"):
    return f"{x},{y:.6f},0.000000"


def write(name, text):
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, name), "wb") as f:
        f.write(text.encode("latin1"))
    print("wrote", name)


# ---------- main menu ----------
t = read("MenuMain.xui")
# B_Multiplayer is Play: the Edition's CoJ2_x86.dll sends it straight to MenuLan, and the game focuses it by default.
# Single player is removed, not hidden: the menu code re-enables it at runtime by Id, and the hidden button
# then took the default focus (a missing Id is skipped). Extra content must stay - the code keeps a pointer
# to it - so it is hidden, disabled and unfocusable instead.
m = block(t, "B_Singleplayer")
t = t[:m.start()] + t[m.end():]
for prop, value in (("Show", "false"), ("Enabled", "false"), ("CanFocus", "false")):
    t = set_prop(t, "B_ExtraContent", prop, value)
t = nav(t, "B_Test", "B_Quit", "B_Multiplayer")

# Leaderboard: a copy of Options, greyed out until the leaderboard DLL fills it.
options = block(t, "B_Options").group(0)
leaderboard = options.replace("<Id>B_Options</Id>", "<Id>B_Leaderboard</Id>")
leaderboard = re.sub(r"<Text>.*?</Text>", "<Text>Leaderboard</Text>", leaderboard, count=1)
leaderboard = re.sub(r"<PressPath>.*?</PressPath>\r?\n", "", leaderboard, count=1)
leaderboard = leaderboard.replace("<Id>B_Leaderboard</Id>", "<Id>B_Leaderboard</Id>\r\n<Enabled>false</Enabled>", 1)
start = block(t, "B_Options").start()
t = t[:start] + leaderboard + t[start:]
t = set_prop(t, "B_Multiplayer", "Text", "Play")

order = ["B_Multiplayer", "B_Leaderboard", "B_Options", "B_Credits", "B_SelectProfile", "B_Quit"]
ys = [346, 388, 430, 472, 514, 580]
for element_id, y in zip(order, ys):
    t = set_prop(t, element_id, "Position", pos(y))
# Keyboard order skips the disabled Leaderboard button.
active = ["B_Multiplayer", "B_Options", "B_Credits", "B_SelectProfile", "B_Quit"]
for i, element_id in enumerate(active):
    t = nav(t, element_id, active[i - 1], active[(i + 1) % len(active)])
t = nav(t, "B_Leaderboard", "B_Multiplayer", "B_Options")
write("MenuMain.xui", t)

# ---------- Play (the LAN screen) ----------
t = read("MenuLan.xui")
t = set_prop(t, "ID_FIND_GAME", "Text", "Join a Game")
t = set_prop(t, "ID_CREATE_GAME", "Text", "Host a Game")
t = set_prop(t, "ScreenName", "Text", "Play")
t = set_prop(t, "T_EsrbNotice_$", "Show", "false")
write("MenuLan.xui", t)

# ---------- server list and host screen: no ESRB line ----------
for name in ("MenuMultiplayerJoin.xui", "MenuMultiplayerCreateGame.xui"):
    t = read(name)
    t = set_prop(t, "T_EsrbNotice_$", "Show", "false")
    write(name, t)
