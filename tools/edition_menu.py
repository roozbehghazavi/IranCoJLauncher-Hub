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
                                             ("Text", "&amp;IrnEditionVersion&amp;"), ("TextColor", DUST),
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
# In game, the menus' backdrop is a snapshot of the game (background_screenshot): blurred like the HUD's, not sepia.
t = set_prop(t, "background_screenshot", "Material", "irancoj_blur_pc.mat")
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
        b = re.sub(r"<(TextColor|DefaultFontColor)>(.*?)</\1>", lambda c: f"<{c.group(1)}>{text_color(c.group(2))}</{c.group(1)}>", b)
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
            new = [text_color(v) if n in ("TextColor", "DefaultFontColor") else color(element_id, v) if n == "Color"
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

# ---------- in game: class selection and scoreboard (design: tools/mockups/ingame_mockups.py) ----------
INK = "0xff0e0d0b"


def group_span(text, group_id, start=0):
    """(start, end) of the whole <AdvGroup>/<XuiGroup> whose Id is group_id, nesting included."""
    m = re.compile(r"<(AdvGroup|XuiGroup)>\r?\n<Properties>\r?\n<Id>" + re.escape(group_id) + r"</Id>").search(text, start)
    if not m:
        raise SystemExit(f"group {group_id} not found")
    depth, i = 0, m.start()
    for tag in re.finditer(r"<(/?)(AdvGroup|XuiGroup)>", text[m.start():]):
        depth += -1 if tag.group(1) else 1
        if depth == 0:
            return m.start(), m.start() + tag.end()
    raise SystemExit(f"group {group_id} not closed")


def in_group(text, group_id, edit, start=0):
    a, b = group_span(text, group_id, start)
    return text[:a] + edit(text[a:b]) + text[b:]


def after_element(text, element_id, new):
    """Inserts new right after the first element with this Id."""
    m = block(text, element_id)
    return text[:m.end()] + new + text[m.end():]


# These screens' code finds elements by their place among their parent's children, so nothing is inserted
# into them: new pieces go into existing images (textures) or elsewhere (the top and bottom bars are in
# HUD_Net.xui's backdrop, see edition.json).


def flat_texts(t, colors):
    """No heavy outline (it sat on paper); the named texts get their palette colour."""
    t = re.sub(r"(<MyText>\r?\n<Properties>(?:(?!</Properties>).)*?)<Outline>true</Outline>", r"\1<Outline>false</Outline>", t, flags=re.S)
    for element_id, color in colors.items():
        if re.search(r"<Id>" + re.escape(element_id) + r"</Id>", t):
            t = set_prop(t, element_id, "TextColor", color)
    return t


t = written["MenuNetSelectClass.xui"]
t = flat_texts(t, {"T_MapName": PARCHMENT, "T_ModeName": GOLD, "T_Timer": GOLD, "T_Wallet": GOLD,
                   "T_CashText": DUST, "T_TeamName": PARCHMENT, "T_Tip": DUST, "T_UpgradeInfoCost": GOLD})

# Middle panel (336x485): portrait, the loadout as rows under it (icon, name; up to three weapons), then the
# upgrade block - "NEXT UPGRADE" + stars with the cost on the right, what it adds under them, the button under
# that. Classes have two upgrades (Rancher and Redneck one); fully upgraded, the game leaves the block empty.
t = in_group(t, "G_ClassInfo", lambda g: set_prop(set_prop(set_prop(g, "I_ClassPicture", "Position", "88.000000,28.000000,0.000000"),
                                                            "I_ClassPicture", "Width", "160.000000"), "I_ClassPicture", "Height", "221.000000"))
for n in range(3):
    def weapon_row(g, n=n):
        g = set_prop(g, f"Weapon{n}", "Position", f"0.000000,{254 + 40 * n}.000000,0.000000")
        g = set_prop(g, f"Weapon{n}", "Height", "38.000000")
        g = set_prop(g, "T_Name", "Position", "56.000000,4.000000,0.000000")
        g = set_prop(g, "T_Name", "Width", "264.000000")
        g = set_prop(g, "T_Name", "TextStyle", "4368")  # left
        g = set_prop(g, "T_Name", "TextColor", PARCHMENT)
        g = set_prop(g, "Icons", "Position", "10.000000,2.000000,0.000000")
        g = set_prop(g, "Icons", "Width", "40.000000")
        g = set_prop(g, "Icons", "Height", "36.000000")
        for icon in ["Back"] + [f"I_Icon_{k}" for k in range(5)]:
            g = set_prop(g, icon, "Width", "36.000000")
            g = set_prop(g, icon, "Height", "36.000000")
            g = set_prop(g, icon, "Position", "0.000000,0.000000,0.000000")
        return g
    t = in_group(t, "G_ClassInfo", lambda g, f=weapon_row, n=n: in_group(g, f"Weapon{n}", f))
# The info's second line (what the upgrade adds) is the one beside the cost (the html's lines sit higher than
# an even split of its box: the cost is raised to meet it).
for element_id, (x, y, w, h) in {"H_UpgradeInfoLabel": (8, 378, 240, 58), "T_UpgradeInfoCost": (196, 390, 132, 32),
                                 "B_Upgrade": (8, 444, 320, 36), "T_WarningNotAvailable": (8, 444, 320, 36)}.items():
    t = set_prop(t, element_id, "Position", f"{x}.000000,{y}.000000,0.000000")
    t = set_prop(t, element_id, "Width", f"{w}.000000")
    t = set_prop(t, element_id, "Height", f"{h}.000000")
# The class list panel ran into the middle one: narrower, with a gap like the design.
t = in_group(t, "G_ClassSelect", lambda g: set_prop(set_prop(g, "Background", "Width", "320.000000"), "L_ClassList", "Width", "306.000000"))
t = set_prop(t, "T_UpgradeInfoCost", "TextStyle", "4624")  # right
t = set_prop(t, "B_Spawn", "Visual", "ButtonIrnPrimary")
for button in ("B_Upgrade", "B_ChangeTeam"):
    t = set_prop(t, button, "Visual", "ButtonIrnOutline")
t = set_prop(t, "H_UpgradeInfoLabel", "DefaultHorizontalAlign", "left")
# The buttons are two rows (Cancel over Quit Game, Change Team over Spawn): lower the group so both sit in the
# bottom bar (616..720) - the top row stuck out above it.
t = set_prop(t, "G_Buttons", "Position", "0.000000,520.000000,0.000000")
t = set_prop(t, "B_ChangeTeam", "Height", "34.000000")  # a gap above Spawn, like the design


def baseline(t, pairs):
    """Texts side by side in the top bar: one box and bottom alignment, so big and small text share a baseline."""
    for ids, (y, h) in pairs:
        for element_id in ids:
            t = set_prop(t, element_id, "Position", re.sub(r",[^,]*,", f",{y}.000000,",
                                                           re.search(r"<Id>" + element_id + r"</Id>.*?<Position>(.*?)</Position>", t, re.S).group(1), count=1))
            t = set_prop(t, element_id, "Height", f"{h}.000000")
            t = set_prop(t, element_id, "VerticalAlignDown", "true")
    return t


t = baseline(t, [(("T_MapName", "T_ModeName", "T_Timer"), (34, 50)), (("T_Wallet", "T_CashText", "T_TeamName"), (-67, 50))])
# Small labels sit ~3 px low beside the big text in the same box; the team star was below the team name.
t = set_prop(t, "T_CashText", "Position", "136.000031,-70.000000,0.000000")
t = set_prop(t, "I_TeamImage", "Position", "730.999939,-78.000000,0.000000")

# Spectate (Spectate mod's bar in the same screen) keeps its places - spectate.dll hit-tests those buttons at
# fixed rects (y=676), which is inside the bottom bar anyway; it gets the class screen's buttons and text.
t = set_prop(t, "T_SpecName", "TextColor", PARCHMENT)
write("MenuNetSelectClass.xui", t)

# Scoreboard (both: the game's compiled one is MenuNetResults, the PC patch adds MenuNetResults_PC): team-tinted
# headers, and a top bar under map / mode / settings / time - it is shown over the live game (Tab), where the
# HUD backdrop's bars are not up. The bar is the scene's first child (the code finds G_Results, G_GameInfo and
# the rest by name); inside the 90 px G_GameInfo group it was not drawn.
# The end-of-round screen (MenuNetSummary) has the same scoreboard and top texts; it sits on the HUD backdrop,
# whose top bar is already up, so it gets no bar of its own.
top_bar = element("MyImage", "I_IrnTopBar", [("Width", "1280.000000"), ("Height", "100.000000"), ("ImagePath", "irn_bar_top")])
for name in ("MenuNetResults.xui", "MenuNetResults_PC.xui", "MenuNetSummary.xui"):
    t = written[name]
    t = flat_texts(t, {"T_MapName": PARCHMENT, "T_ModeName": GOLD, "T_Timer": GOLD, "T_GameSettings": PARCHMENT,
                       "T_ServerName": PARCHMENT})
    t = baseline(t, [(("T_MapName", "T_ModeName", "T_Timer", "T_GameSettings"), (34, 50))])
    for group, panel in (("G_RedBackground", "irn_panel_red_tile"), ("G_BlueBackground", "irn_panel_blue_tile"),
                         ("G_Individual", "irn_panel_solo")):
        t = in_group(t, group, lambda g, panel=panel: set_prop(g, "Background", "ImagePath", panel))
    # Column titles in sand over the panel's rule, the team score in parchment (the team name keeps its colour).
    for element_id, color in (("H_HeaderList", DUST), ("H_Score", PARCHMENT)):
        t = re.sub(r"(<Id>" + element_id + r"</Id>(?:(?!</Properties>).)*?)(</Properties>)",
                   lambda m, color=color: m.group(1) + f"<DefaultFontColor>{color}</DefaultFontColor>\r\n" + m.group(2), t, flags=re.S)
    if name != "MenuNetSummary.xui":
        head = re.search(r"<XuiScene>\r?\n<Properties>.*?</Properties>\r?\n", t, re.S)
        t = t[:head.end()] + top_bar + t[head.end():]
    write(name, t)

def themed_scrollbars(t):
    """Scrollbars: slim wood track, gold handle, flat sand arrows (gold when focused) instead of brush strokes."""
    images = {"slider_bar.dds": ("irn_scroll_track", None), "slider_knob.dds": ("irn_scroll_knob", None),
              "arrow_right_0": ("irn_arrow_0", "irn_arrow"), "arrow_right_back": ("irn_arrow_0", "irn_arrow")}

    def element(m):
        b = m.group(0)
        path = re.search(r"<ImagePath>(.*?)</ImagePath>", b)
        if not path or path.group(1) not in images:
            return b
        image, base = images[path.group(1)]
        b = put(b, "ImagePath", image)
        if base:
            b = put(b, "BaseImage", base)
            b = put(b, "NumFrames", "1")
        b = put(b, "Material", "sprite_button.mat")
        element_id = re.search(r"<Id>(.*?)</Id>", b).group(1)
        return put(b, "Color", GOLD if element_id == "Focus" else SAND if base else WHITE)

    return re.sub(r"<Properties>\r?\n<Id>.*?</Properties>", element, t, flags=re.S)


# Spawn: the one solid gold button (dark text), like the mockup.
t = written["CoJ2MenuSkin.xui"]
primary = visual(t, "ButtonV").group(0).replace("<Id>ButtonV</Id>", "<Id>ButtonIrnPrimary</Id>", 1)
primary = set_prop(set_prop(primary, "RandomBackground", "BaseImage", "irn_flat"), "RandomBackground", "ImagePath", "irn_flat_0")
primary = keyframes(primary, "RandomBackground", lambda time, props: ["0xfff2c46e" if 6 <= time <= 26 else GOLD, "1.000000"])
primary = keyframes(primary, "TextPrezenter", lambda time, props: ["0x800e0d0b" if time >= 80 else INK, "false", "1.000000"])
primary = set_prop(set_prop(primary, "RandomBackground", "Color", GOLD), "TextPrezenter", "TextColor", INK)
# Upgrade, Change Team: a gold frame, gold text; the warm band inside when focused.
second = visual(t, "ButtonV").group(0).replace("<Id>ButtonV</Id>", "<Id>ButtonIrnOutline</Id>", 1)
second = set_prop(set_prop(second, "RandomBackground", "BaseImage", "irn_outline"), "RandomBackground", "ImagePath", "irn_outline_0")
second = keyframes(second, "RandomBackground", lambda time, props: ["0xfff2c46e" if 6 <= time <= 26 else GOLD, "1.000000"])
second = keyframes(second, "TextPrezenter", lambda time, props: ["0xfff2c46e" if 6 <= time <= 26 else WOOD if time >= 80 else GOLD, "false", "1.000000"])
second = set_prop(set_prop(second, "RandomBackground", "Color", GOLD), "TextPrezenter", "TextColor", GOLD)
end = visual(t, "ButtonV").end()
t = themed_scrollbars(t[:end] + primary + second + t[end:])
# The class list's scrollbar sat under the rows (both at x=0): bar to the left edge, rows beside it.
m = visual(t, "ListBoxNetEmptyV")
v = set_prop(set_prop(m.group(0), "LBScrollBar", "Position", "-6.000000,0.000000,0.000000"), "LBScrollBar", "Width", "24.000000")
v = set_prop(v, "ItemGroup", "Position", "22.000000,0.000000,0.000000")
v = set_prop(v, "ItemGroup", "Width", "378.000000")  # moved right by 22, so 22 narrower: the team highlight stays in the panel
v = set_prop(v, "ButtonDummy", "Width", "284.000000")  # the rows are copies of this: 22 + 284 = the list's 306
t = t[:m.start()] + v + t[m.end():]
m = visual(t, "ButtonNetV")  # the class rows' look (only they use it): the team highlight band as wide as the row
row = set_prop(set_prop(m.group(0), "ButtonNetV", "Width", "284.000000"), "RandomBackground", "Width", "284.000000")
t = t[:m.start()] + row + t[m.end():]
# Scoreboard rows: the game writes them as html with no colour (only yours in yellow), so the names fell back to
# black on the dark panels.
m = visual(t, "MyListStatisticsButtonVisual")
write("CoJ2MenuSkin.xui", t[:m.start()] + set_prop(m.group(0), "H_Info", "DefaultFontColor", PARCHMENT) + t[m.end():])

# In game, the loading backdrop is the same snapshot: blurred, not sepia.
t = written["BackgroundLoading.xui"]
t = set_prop(t, "MenuBackgroundIngame", "Material", "irancoj_blur_pc.mat")
t = set_prop(t, "Loading", "Material", "irancoj_loading.mat")  # its own copy of loading_bckg.mat with the map card (edition.json)
# Multiplayer loading (design: tools/mockups/loading_mockup.py). The map's own picture in colour behind, darker on
# the left, and the dark card under the objectives map are drawn by loading_bckg.mat (edition.json), so nothing is
# added here. Left: mode, map name, place and date, the story; right: the objectives map; bottom right: spinner.
# The place labels on the map keep their outline (they sit on the light map art). The game places the spinner
# (Drum) and "Loading..." under it itself, from the screen size, at the bottom right: the card stays left of them.
LEFT, MAP_X, MAP_Y = 96, 590, 108
STORY = "0xffdccfb6"  # the map's story / hint: light sand, so the body text doesn't read as plain white
for element_id, (x, y, w, h, color, font_, style) in {
        "T_Mode": (LEFT, 122, 460, 40, GOLD, "TextMedium", "4368"),
        "T_MapName": (LEFT, 150, 460, 60, PARCHMENT, "TextHuge", "4368"),
        "T_Flavour": (LEFT, 214, 460, 40, SAND, "TextNormal", "4368")}.items():
    t = set_prop(t, element_id, "Position", f"{x}.000000,{y}.000000,0.000000")
    for prop, value in (("Width", f"{w}.000000"), ("Height", f"{h}.000000"), ("TextColor", color), ("Font", font_),
                        ("TextStyle", style), ("Outline", "false"), ("VerticalAlignDown", "true")):
        t = set_prop(t, element_id, prop, value)
t = set_prop(t, "map", "Position", f"{MAP_X}.000000,{MAP_Y}.000000,0.000000")
for desc in ("T_Desc0", "T_Desc1"):  # inside the map group: placed back on the left, under the name
    for prop, value in (("Position", f"{LEFT - MAP_X}.000000,{272 - MAP_Y}.000000,0.000000"), ("Width", "460.000000"),
                        ("Height", "320.000000"), ("TextColor", STORY), ("TextStyle", "4368"), ("Outline", "false")):
        t = set_prop(t, desc, prop, value)
for element_id in ("Text", "T_Hint", "SubtitleText", "SubtitleText2", "T_Loading"):
    t = set_prop(set_prop(t, element_id, "TextColor", PARCHMENT), element_id, "Outline", "false")
write("BackgroundLoading.xui", t)

# "Please wait..." during loading is the key hint of the MenuLoading overlay: lower, under the map card.
t = written["MenuLoading.xui"]
t = set_prop(t, "ID_KEYHINT_1", "Position", "8.000000,650.000000,0.000000")
write("MenuLoading.xui", t)
