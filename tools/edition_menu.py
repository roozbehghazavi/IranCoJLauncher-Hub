"""Source of the Edition's compiled menu packs in edition/files/CoJ2/Data/Menu.

Reads the original .xui files from a player's Data0.pak and writes edited copies into a scratch Edition's
CoJ2/Data/Menu/scr. Compile them there: debugconf.scr with ForceUiFromXML() + SaveUiPacks("PC"), start the
game, quit with the menu's Quit button, then ship the compiled packs and test in a real Edition, in normal
mode (hosting crashes in compile mode).

The class screen (MenuNetSelectClass.xui) is New Classes' version, which also carries Spectate's button:
pass the folder holding it (IranCoJMods_Sc NewClasses_mod/data/client/CoJ2/Data/Menu/scr, or an Edition's
CoJ2/Data/Menu/scr). In-game packs compiled from the game's own class screen lose those, and crash.

    python tools/edition_menu.py "<game>/CoJ2/Data0.pak" "<scratch edition>/CoJ2/Data/Menu/scr" "<mods' scr folder>"
"""

import os
import re
import sys
import zipfile

pak, out = sys.argv[1], sys.argv[2]
mod_sources = sys.argv[3] if len(sys.argv) > 3 else None
z = zipfile.ZipFile(pak)


# Later paks override earlier ones (Data3.pak carries the PC patch's screens, e.g. the scoreboard).
paks = []
for n in (3, 2, 1, 0):
    path = os.path.join(os.path.dirname(pak), f"Data{n}.pak")
    if os.path.isfile(path):
        archive = zipfile.ZipFile(path)
        paks.append((archive, {e.lower(): e for e in archive.namelist()}))


def read(name):
    """A mod's version of the screen when there is one (New Classes' class screen), else the game's newest."""
    if mod_sources and os.path.isfile(os.path.join(mod_sources, name)):
        with open(os.path.join(mod_sources, name), "rb") as f:
            return f.read().decode("latin1")
    for archive, entries in paks:
        entry = entries.get(("data/menu/scr/" + name).lower())
        if entry:
            return archive.read(entry).decode("latin1")
    raise SystemExit(f"{name} not found")


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


def keyframes(text, element_id, edit):
    """Rewrites each KeyFrame of the element's Timeline: edit(time, [props]) -> [props]."""
    m = re.search(r"<Timeline>\r?\n<Id>" + re.escape(element_id) + r"</Id>.*?</Timeline>", text, re.S)
    if not m:
        raise SystemExit(f"timeline {element_id} not found")

    def frame(k):
        time = int(re.search(r"<Time>(\d+)</Time>", k.group(0)).group(1))
        props = iter(edit(time, re.findall(r"<Prop>(.*?)</Prop>", k.group(0))))
        return re.sub(r"<Prop>.*?</Prop>", lambda _: f"<Prop>{next(props)}</Prop>", k.group(0))

    timeline = re.sub(r"<KeyFrame>.*?</KeyFrame>", frame, m.group(0), flags=re.S)
    return text[:m.start()] + timeline + text[m.end():]


def visual(text, visual_id):
    m = re.search(r"<XuiVisual>\r?\n<Properties>\r?\n<Id>" + re.escape(visual_id) + r"</Id>.*?</XuiVisual>\r?\n", text, re.S)
    if not m:
        raise SystemExit(f"visual {visual_id} not found")
    return m


def element(kind, element_id, props):
    lines = "".join(f"<{k}>{v}</{k}>\r\n" for k, v in props)
    return f"<{kind}>\r\n<Properties>\r\n<Id>{element_id}</Id>\r\n{lines}</Properties>\r\n</{kind}>\r\n"


# Persepolis Dust (ARGB)
PARCHMENT, GOLD, WOOD, SAND, DUST, WHITE = "0xfff3ebdd", "0xffe2b15e", "0xff5c4f40", "0xffa58967", "0xffb9ac98", "0xffffffff"


def restyle_button(v):
    """Style A: plain parchment text; focus = gold text on a dark band with a gold bar (irancoj_band.dds)."""
    for prop, value in (("ImagePath", "irn_band_0"), ("BaseImage", "irn_band"), ("NumFrames", "1"),
                        ("Color", WHITE), ("Material", "sprite_button.mat")):
        v = set_prop(v, "RandomBackground", prop, value)

    def band(time, props):  # Color, Opacity
        focused = 6 <= time <= 26
        selected = 38 <= time <= 70
        return [WHITE, "1.000000" if focused else "0.600000" if selected else "0.000000"]

    def text(time, props):  # TextColor, Outline, Opacity
        color = GOLD if 6 <= time <= 26 else WOOD if time >= 80 else PARCHMENT
        return [color, "false", "1.000000"]

    v = keyframes(v, "RandomBackground", band)
    v = keyframes(v, "TextPrezenter", text)
    for frame in ("Frame", "Frame1"):  # the old brush-stroke selection frames
        v = keyframes(v, frame, lambda time, props: ["false"])
    return set_prop(v, "TextPrezenter", "TextColor", PARCHMENT)


written = {}


def write(name, text):
    written[name] = text
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
ys = [292, 344, 396, 448, 500, 572]
for element_id, y in zip(order, ys):
    t = set_prop(t, element_id, "Position", pos(y, "64.000000"))
    t = set_prop(t, element_id, "Visual", "ButtonIrn")
    t = set_prop(t, element_id, "AutoAdjustWidth", "false")
    t = set_prop(t, element_id, "Width", "340.000000")
    t = set_prop(t, element_id, "Height", "48.000000")

# Header, "SOON" on Leaderboard, key hints; the version line in quiet dust.
extras = (
    element("MyImage", "I_IrnLogo", [("Width", "512.000000"), ("Height", "256.000000"),
                                      ("Position", "76.000000,90.000000,0.000000"), ("ImagePath", "irn_logo")])
    + element("MyText", "T_IrnSoon", [("Width", "60.000000"), ("Height", "48.000000"),
                                       ("Position", f"{64 + 340 - 72}.000000,352.000000,0.000000"),
                                       ("Text", "SOON"), ("TextColor", SAND), ("Font", "TextVerySmall"),
                                       ("TextStyle", "272")])
    + element("MyText", "T_IrnKeys", [("Width", "600.000000"), ("Height", "40.000000"),
                                       ("Position", "80.000000,664.000000,0.000000"),
                                       ("Text", "ENTER  Select        ESC  Back"), ("TextColor", DUST),
                                       ("Font", "TextSmall"), ("TextStyle", "272")])
)
first_button = t.index("<UINaviButton>")
t = t[:first_button] + extras + t[first_button:]
# The game writes its own version ("v1.1.0.0 WW") into T_GameVersion: hide it and show ours in its place.
t = set_prop(t, "T_GameVersion", "Show", "false")
t = set_prop(t, "T_GameVersion", "Opacity", "0.000000")
version = element("MyText", "T_IrnVersion", [("Width", "600.000000"), ("Height", "40.000000"),
                                             ("Position", "600.000000,664.000000,0.000000"),
                                             ("Text", "IranCoJ Edition 0.6"), ("TextColor", DUST),
                                             ("Font", "TextSmall"), ("TextStyle", "528")])
first_button = t.index("<UINaviButton>")
t = t[:first_button] + version + t[first_button:]
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

# ---------- button style (every screen), plus a left-aligned copy for the main menu ----------
t = read("CoJ2MenuSkin.xui")
m = visual(t, "ButtonV")
button = restyle_button(m.group(0))
main_button = button.replace("<Id>ButtonV</Id>", "<Id>ButtonIrn</Id>", 1)
main_button = set_prop(main_button, "TextPrezenter", "TextStyle", "4368")  # left instead of centred
main_button = set_prop(main_button, "TextPrezenter", "Position", "24.000000,0.000000,0.000000")
t = t[:m.start()] + button + main_button + t[m.end():]
write("CoJ2MenuSkin.xui", t)

# ---------- background: the film in full colour (Mat/menu_bckg*.mat), no paper, no revolver ----------
t = read("MenuBackground.xui")
t = set_prop(t, "background_base", "Opacity", "1.000000")
t = keyframes(t, "background_base", lambda time, props: ["0.000000" if props[0] == "0.000000" else "1.000000"])
t = set_prop(t, "I_Gun", "Show", "false")
t = set_prop(t, "background_film_back", "ImagePath", "black")  # under the film while it fades: black, not paper
write("MenuBackground.xui", t)


# ---------- dark panels and Persepolis colours on every main-menu screen ----------
# Only screens in the packs the Edition ships (MenuCommon, MenuMain, Dashboard, Background). In-game screens
# have their own packs, which can't be shipped (recompiled ones crash), so skin visuals made for them
# (*Ingame*) keep the original look - in game they still sit on the original paper.
MENU_SCREENS = """BackgroundLoading Curtain MenuCredits MenuLoading MenuOptionsControlsButtons MenuOptionsControlsKeyboard
    MenuOptionsControlsSticks MenuSavingProfileWarningDialog MenuYesNoDialog MenuPasswordDialog MenuProgressDialog
    DashboardAgreement DashboardBackground DashboardCreateProfile DashboardCreateProfile2 DashboardEditProfile
    DashboardFriends DashboardGamerProfile DashboardMain DashboardMessage DashboardMessageCompose DashboardMessages
    DashboardMsgBox DashboardNotification DashboardPlayers DashboardSaveNotification DashboardSignIn
    DashboardYesNoDialog DashboardPasswordDialog DashboardProgressDialog MenuLan MenuMplCustomMatch
    MenuMultiplayerChooseMaps MenuMultiplayerCreateGame MenuMultiplayerJoin MenuGamma MenuOptionsAudio
    MenuOptionsControls MenuOptionsGame MenuOptionsVideo MenuMain MenuMplStatsLeaderboard MenuMultiplayer
    MenuOptions DashboardSignIn DashboardSelectProfile""".split()
# In game: class selection, scoreboard, round end, pause menu and its dialogs.
INGAME_SCREENS = """MenuNetSelectClass MenuNetResults MenuNetResults_PC MenuNetSummary MenuNetLevelFinished MenuNetObjectivesMap
    MenuInGame MenuIngameDialog MenuOptionsInGame MenuMpl MenuMplChat""".split()
DARK_TEXT = {"0xff0f0f0f", "0xff070000", "0xff000000", "0xfe000000", "0xfd000000", "0xfb000000", "0xf2000000"}
HEADER = "0xff4a3f31"  # the blue header brushes, in dark wood
BRUSH = {"0xffc38428": "0xff2e2a24", "0xff579446": "0xff7a6038", "0xff3ded0b": GOLD, "0xffd5f75a": GOLD,
         "0xff4485ed": HEADER, "0xff4485eb": HEADER, "0xffbf190f": "0xff7a2e22"}
OTHER = {"0xffc38428": SAND, "0xff579446": GOLD, "0xff4485ed": HEADER, "0xff4485eb": HEADER}  # arrows, bars


def text_color(value):
    """Dark text (it sat on paper) -> parchment, keeping its alpha."""
    v = int(value, 16)
    luma = 0.3 * (v >> 16 & 255) + 0.59 * (v >> 8 & 255) + 0.11 * (v & 255)
    return value[:4] + PARCHMENT[4:] if value.lower() in DARK_TEXT or luma < 100 else value


HEADERS = {"0xff4485ed": HEADER, "0xff4485eb": HEADER, "0xffbf190f": "0xff7a2e22"}  # blue / red title brushes
IDLE = {"0xffc38428", "0xffce8419", "0xffceb217", "0xffceb219"}  # ochre brush = not focused (or disabled)
CLEAR = "0x00ffffff"


def put(b, prop, value):
    """Sets (or adds after Id) a property in one Properties block."""
    if re.search(f"<{prop}>.*?</{prop}>", b):
        return re.sub(f"<{prop}>.*?</{prop}>", f"<{prop}>{value}</{prop}>", b, count=1)
    return re.sub(r"(<Id>.*?</Id>)", lambda m: f"{m.group(1)}\r\n<{prop}>{value}</{prop}>", b, count=1)


def recolor(text):
    """Panels -> irn_panel_tile; dark text -> parchment. Brush strokes become flat: list rows, option rows and
    other buttons get the main menu's band (shown only when focused), title brushes a flat wood strip, and the
    scribbled selection outlines go."""
    text = text.replace("dialog_frame_a_tile", "irn_panel_tile")
    kind = {}
    for m in re.finditer(r"<Properties>\r?\n<Id>(.*?)</Id>(.*?)</Properties>", text, re.S):
        body = m.group(2)
        if re.search(r"<(?:BaseImage|ImagePath)>button_sel", body):
            kind[m.group(1)] = "outline"
        elif re.search(r"<(?:BaseImage|ImagePath)>button", body):
            c = re.search(r"<Color>(.*?)</Color>", body)
            kind[m.group(1)] = "header" if c and c.group(1).lower() in HEADERS else "band"

    def color(element_id, value):
        k = kind.get(element_id)
        if k == "band":
            return CLEAR if value.lower() in IDLE else WHITE
        if k == "header":
            return HEADERS.get(value.lower(), HEADER)
        return OTHER.get(value.lower(), value)

    def element(m):
        b = m.group(0)
        element_id = re.search(r"<Id>(.*?)</Id>", b).group(1)
        b = re.sub(r"<TextColor>(.*?)</TextColor>", lambda c: f"<TextColor>{text_color(c.group(1))}</TextColor>", b)
        k = kind.get(element_id)
        if k == "outline":
            return put(b, "Show", "false")
        if k in ("band", "header"):
            image = "irn_band" if k == "band" else "irn_flat"
            for prop, value in (("BaseImage", image), ("ImagePath", image + "_0"), ("NumFrames", "1"),
                                ("Material", "sprite_button.mat")):
                b = put(b, prop, value)
            if k == "band" and not re.search(r"<Color>", b):
                b = put(b, "Color", CLEAR)
        return re.sub(r"<Color>(.*?)</Color>", lambda c: f"<Color>{color(element_id, c.group(1))}</Color>", b)

    def timeline(m):
        b = m.group(0)
        element_id = re.search(r"<Id>(.*?)</Id>", b).group(1)
        names = re.findall(r"<TimelineProp>(.*?)</TimelineProp>", b)

        def frame(k):
            props = iter(re.findall(r"<Prop>(.*?)</Prop>", k.group(0)))
            new = [text_color(v) if n == "TextColor" else color(element_id, v) if n == "Color"
                   else "false" if n == "Show" and kind.get(element_id) == "outline" else v
                   for n, v in zip(names, props)]
            it = iter(new)
            return re.sub(r"<Prop>.*?</Prop>", lambda _: f"<Prop>{next(it)}</Prop>", k.group(0))

        return re.sub(r"<KeyFrame>.*?</KeyFrame>", frame, b, flags=re.S)

    text = re.sub(r"<Properties>\r?\n<Id>.*?</Properties>", element, text, flags=re.S)
    return re.sub(r"<Timeline>\r?\n<Id>.*?</Timeline>", timeline, text, flags=re.S)


t = written["CoJ2MenuSkin.xui"]
for m in reversed(list(re.finditer(r"<XuiVisual>\r?\n<Properties>\r?\n<Id>(.*?)</Id>.*?</XuiVisual>\r?\n", t, re.S))):
    if m.group(1) in ("ButtonV", "ButtonIrn"):
        continue
    t = t[:m.start()] + recolor(m.group(0)) + t[m.end():]
write("CoJ2MenuSkin.xui", t)

for screen in MENU_SCREENS + INGAME_SCREENS:
    name = screen + ".xui"
    write(name, recolor(written.get(name) or read(name)))

# ---------- profile pages: the softened background instead of paper, no revolvers ----------
t = written["DashboardBackground.xui"]
t = set_prop(t, "Background", "ImagePath", "irn_bg")
t = drop_prop(t, "Background", "Material")
for gun in ("I_Gun_1", "I_Gun_2"):
    t = set_prop(t, gun, "Show", "false")
    t = set_prop(t, gun, "Opacity", "0.000000")
write("DashboardBackground.xui", t)

# ---------- profile list (shown first): the four buttons in a grid lined up with the list panel ----------
t = written["DashboardSignIn.xui"]
grid = {"B_DeleteProfile": (24, 478), "B_Back": (24, 526), "B_CreateProfile": (354, 478), "B_SignIn": (354, 526)}
for button, (x, y) in grid.items():
    t = set_prop(t, button, "Position", f"{x}.000000,{y}.000000,0.000000")
    t = set_prop(t, button, "AutoAdjustWidth", "false")
    t = set_prop(t, button, "Width", "320.000000")
    t = set_prop(t, button, "Height", "42.000000")
write("DashboardSignIn.xui", t)
