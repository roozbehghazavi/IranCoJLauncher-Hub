"""Builds the Edition's credits (edition/files/CoJ2/Data/Menu/scr/Credits_PC.scr) from tools/credits.txt.

The game reads Credits_PC.scr (UTF-16) when the Credits screen opens, so a loose copy replaces the original.
In credits.txt: "= Title" is a big heading, "- Role" a small heading, other lines are names, blank lines add
space, "#" lines are comments.

    python tools/edition_credits.py
"""

import os

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "credits.txt")
OUT = os.path.join(HERE, "..", "edition", "files", "CoJ2", "Data", "Menu", "scr", "Credits_PC.scr")

HEADER = """!Speed(f)
!DefaultFont(s)
!DefaultFontRes(i, s)
!DefaultSpace(f)
!HorizPos(f)
!LoadFont(s, s, i)
!LastLineSpacing(f)
!Line(s) //line with text to localization
!LineTextExplicit(s) //line with some national characters like polish ones
!LineSpace(f)
!Font(s)
!FontRes(i, s)
!Align(i) //0 - left, 1 - center (default), 2 - right, 3 - justify (not implemented)

DefaultSpace(3)
DefaultFont("TextBig")
Speed(60)
"""


def quote(text):
    return text.replace('"', "'")


def build():
    out = [HEADER]
    first = True
    for raw in open(SOURCE, encoding="utf-8").read().splitlines():
        line = raw.strip()
        if line.startswith("#"):
            continue
        if not line:
            out.append("LineSpace(50)")
        elif line.startswith("= "):
            if not first:
                out.append("LineSpace(130)")
            title = quote(line[2:]).replace("&", "&[AMPERSAND]&")
            out.append(f'Line("{title}") {{ Font("TextVeryBig") }}')
            out.append("LineSpace(70)")
            first = False
        elif line.startswith("- "):
            role = quote(line[2:]).replace("&", "&[AMPERSAND]&")
            out.append(f'Line("{role}") {{ Font("TextNormal") }}')
        else:
            out.append(f'LineTextExplicit("{quote(line).replace("&", "and")}")')
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-16", newline="\r\n") as f:
        f.write("\n".join(out) + "\n")
    print("wrote", os.path.normpath(OUT))


if __name__ == "__main__":
    build()
