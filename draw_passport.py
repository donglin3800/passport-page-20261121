# draw_passport.py — renders the invented passport spread for the Republic
# of Meridia (a country that isn't there) to entry.png, 1024x724.
# Pure Pillow, deterministic: same input always yields the same bytes.
# Run: python3 draw_passport.py  (writes entry.png next to this script)
import math
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 724

FD = "/usr/share/fonts/truetype/dejavu"
FL = "/usr/share/fonts/truetype/liberation"


def font(path, size):
    return ImageFont.truetype(path, size)


SANS = FL + "/LiberationSans-Regular.ttf"
SANSB = FL + "/LiberationSans-Bold.ttf"
SANSI = FL + "/LiberationSans-Italic.ttf"
SERIFB = FL + "/LiberationSerif-Bold.ttf"
MONOB = FD + "/DejaVuSansMono-Bold.ttf"

PAPER = (247, 242, 228)
INK = (15, 61, 74)          # deep teal
INK_SOFT = (28, 92, 104)
GOLD = (166, 124, 26)
GOLD_LT = (176, 138, 46)
GREY = (107, 111, 106)
RULE = (120, 130, 120)

# ---------------------------------------------------------------- MRZ (ICAO 9303 TD3)
VALS = {c: i for i, c in enumerate("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")}
VALS["<"] = 0


def check_digit(s):
    total = 0
    for i, ch in enumerate(s):
        total += VALS[ch] * (7, 3, 1)[i % 3]
    return str(total % 10)


def build_mrz():
    # Line 1: P<MER + name field (39 chars)
    name = "VOSS<<ELENA<MARIS"
    line1 = ("P<MER" + name).ljust(44, "<")
    # Line 2: doc(9)+cd, nat(3), dob(6)+cd, sex(1), exp(6)+cd,
    #         personal(14)+cd, composite cd
    doc = "MD4829137"
    dob, exp = "880314", "330611"
    personal = "M19880314<<<<<"
    assert len(doc) == 9 and len(personal) == 14
    composite_src = (doc + check_digit(doc) + dob + check_digit(dob)
                     + exp + check_digit(exp) + personal
                     + check_digit(personal))
    line2 = (doc + check_digit(doc) + "MER" + dob + check_digit(dob) + "F"
             + exp + check_digit(exp) + personal + check_digit(personal)
             + check_digit(composite_src))
    assert len(line1) == 44 and len(line2) == 44, (len(line1), len(line2))
    return line1, line2


def verify_mrz(l1, l2):
    ok = True
    def ck(field, got, what):
        nonlocal ok
        want = check_digit(field)
        if want != got:
            print(f"MRZ FAIL {what}: field={field} want {want} got {got}")
            ok = False
    ck(l2[0:9], l2[9], "doc")
    ck(l2[13:19], l2[19], "dob")
    ck(l2[21:27], l2[27], "expiry")
    ck(l2[28:42], l2[42], "personal")
    comp = l2[0:10] + l2[13:20] + l2[21:28] + l2[28:43]
    ck(comp, l2[43], "composite")
    assert l1.startswith("P<MER") and "VOSS<<ELENA<MARIS" in l1
    assert l2[10:13] == "MER" and l2[13:19] == "880314" and l2[20] == "F"
    assert l2[21:27] == "330611"
    print("MRZ verify:", "OK" if ok else "FAILED")
    print(" ", l1)
    print(" ", l2)
    return ok


# ---------------------------------------------------------------- helpers
def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def field(d, x, y, label, value, vfnt, label_fill=GREY, value_fill=INK):
    d.text((x, y), label, font=font(SANS, 10), fill=label_fill)
    d.text((x, y + 13), value, font=vfnt, fill=value_fill)


def guilloche(base):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for cx, cy, r0 in ((256, 362, 60), (768, 362, 60), (256, 362, 300),
                       (768, 362, 300)):
        for k in range(7):
            r = r0 + k * 9
            od.ellipse([cx - r, cy - r, cx + r, cy + r],
                       outline=(20, 96, 110, 14), width=1)
    for y in range(0, H, 16):
        pts = [(x, y + 3 * math.sin(x / 55.0 + y / 40.0)) for x in range(0, W + 8, 8)]
        od.line(pts, fill=(20, 96, 110, 9), width=1)
    base.alpha_composite(ov)


def coat_of_arms(d, cx, cy, r):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GOLD, width=3)
    d.ellipse([cx - r + 5, cy - r + 5, cx + r - 5, cy + r - 5],
              outline=GOLD, width=1)
    # sun: gold disc with rays over three waves
    d.ellipse([cx - 9, cy - 13, cx + 9, cy + 5], fill=GOLD)
    for a in range(0, 360, 45):
        x1 = cx + 12 * math.cos(math.radians(a))
        y1 = cy - 4 + 12 * math.sin(math.radians(a))
        x2 = cx + 17 * math.cos(math.radians(a))
        y2 = cy - 4 + 17 * math.sin(math.radians(a))
        d.line([x1, y1, x2, y2], fill=GOLD, width=2)
    for j, wy in enumerate((cy + 9, cy + 14, cy + 19)):
        d.arc([cx - 14, wy - 5, cx + 14, wy + 5], 0, 180,
              fill=INK_SOFT, width=2)


def portrait():
    """Flat-illustration passport photo, drawn 2x then downscaled."""
    S = 2
    pw, ph = 140 * S, 160 * S
    im = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # background: pale blue-grey
    d.rectangle([0, 0, pw, ph], fill=(178, 196, 209, 255))
    d.rectangle([0, 0, pw, 26], fill=(190, 206, 217, 255))
    skin = (192, 138, 94, 255)
    skin_dk = (172, 120, 80, 255)
    hair = (51, 36, 28, 255)
    top_c = (39, 75, 90, 255)
    cx = pw // 2
    # shoulders / top
    d.polygon([(0, ph), (0, 236), (52, 196), (88, 186), (192, 186),
               (228, 196), (pw, 236), (pw, ph)], fill=top_c)
    # collar V
    d.polygon([(118, 188), (140, 188), (140, 214), (129, 224), (118, 214)],
              fill=(226, 220, 205, 255))
    # neck
    d.rectangle([118, 158, 162, 196], fill=skin_dk)
    d.rectangle([118, 158, 162, 172], fill=skin)
    # ears
    d.ellipse([66, 96, 84, 122], fill=skin)
    d.ellipse([196, 96, 214, 122], fill=skin)
    # head
    d.ellipse([70, 22, 210, 172], fill=skin)
    # hair: cap over top of head + tied-back bun + side strands
    d.pieslice([70, 22, 210, 172], 180, 360, fill=hair)
    d.ellipse([186, 8, 224, 46], fill=hair)          # bun
    d.polygon([(70, 60), (86, 60), (80, 150), (66, 150)], fill=hair)
    d.polygon([(210, 60), (194, 60), (200, 150), (214, 150)], fill=hair)
    # eyebrows
    d.arc([96, 84, 128, 100], 200, 340, fill=hair, width=4)
    d.arc([152, 84, 184, 100], 200, 340, fill=hair, width=4)
    # eyes
    for ex in (104, 160):
        d.ellipse([ex, 104, ex + 20, 114], fill=(250, 248, 240, 255))
        d.ellipse([ex + 7, 105, ex + 13, 113], fill=(30, 22, 18, 255))
        d.line([ex - 2, 103, ex + 22, 103], fill=hair, width=3)
    # nose
    d.line([138, 112, 136, 132], fill=skin_dk, width=3)
    d.line([136, 132, 144, 136], fill=skin_dk, width=3)
    # lips: calm, closed
    d.line([120, 148, 160, 148], fill=(150, 80, 66, 255), width=4)
    d.arc([120, 142, 160, 156], 0, 180, fill=(150, 80, 66, 255), width=2)
    # cheek shading
    d.ellipse([88, 122, 112, 138], fill=(198, 148, 108, 90))
    d.ellipse([168, 122, 192, 138], fill=(198, 148, 108, 90))
    return im.resize((140, 160), Image.LANCZOS)


def stamp_layer(w, h, shape, ink, lines, title=None):
    """One ink stamp on a transparent layer, drawn 2x, returned at 1x."""
    S = 2
    im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    m = 10 * S
    if shape == "oval":
        d.ellipse([m, m, w * S - m, h * S - m], outline=ink, width=4 * S)
        d.ellipse([m + 8 * S, m + 8 * S, w * S - m - 8 * S, h * S - m - 8 * S],
                  outline=ink, width=2 * S)
    elif shape == "circle":
        d.ellipse([m, m, w * S - m, h * S - m], outline=ink, width=4 * S)
        d.ellipse([m + 8 * S, m + 8 * S, w * S - m - 8 * S, h * S - m - 8 * S],
                  outline=ink, width=2 * S)
    else:
        d.rounded_rectangle([m, m, w * S - m, h * S - m], radius=10 * S,
                            outline=ink, width=4 * S)
        d.rounded_rectangle([m + 8 * S, m + 8 * S, w * S - m - 8 * S,
                             h * S - m - 8 * S], radius=8 * S,
                            outline=ink, width=2 * S)
    cx = w * S // 2
    y = m + 12 * S
    if title:
        f = font(SANSB, 15 * S)
        tw = d.textlength(title, font=f)
        d.text((cx - tw / 2, y), title, font=f, fill=ink)
        y += 24 * S
        d.line([cx - 60 * S, y, cx + 60 * S, y], fill=ink, width=2 * S)
        y += 8 * S
    else:
        y = m + 8 * S
    f = font(SANSB, 14 * S)
    f2 = font(SANS, 12 * S)
    for i, (txt, bold) in enumerate(lines):
        ff = f if bold else f2
        tw = d.textlength(txt, font=ff)
        d.text((cx - tw / 2, y), txt, font=ff, fill=ink)
        y += 20 * S
    return im.resize((w, h), Image.LANCZOS)


def paste_rotated(base, layer, cx, cy, angle):
    rot = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    base.alpha_composite(rot, (int(cx - rot.width / 2), int(cy - rot.height / 2)))


def signature(d, x, y):
    col = (28, 42, 88, 255)
    # flowing signature strokes for "Elena M. Voss"
    strokes = [
        [(0, 18), (6, 2), (12, 12), (18, 20), (24, 4), (30, 14), (38, 18)],
        [(44, 16), (50, 8), (56, 16), (62, 18)],
        [(70, 10), (76, 18), (82, 6), (88, 16)],
        [(96, 18), (104, 4), (112, 16), (120, 18), (128, 8), (136, 16)],
    ]
    for st in strokes:
        pts = [(x + px, y + py) for px, py in st]
        d.line(pts, fill=col, width=2, joint="curve")
    d.line([(x - 2, y + 26), (x + 150, y + 24)], fill=col, width=2)


def main():
    l1, l2 = build_mrz()
    assert verify_mrz(l1, l2), "MRZ failed verification"

    img = Image.new("RGBA", (W, H), PAPER + (255,))
    guilloche(img)
    d = ImageDraw.Draw(img)

    # outer frame + centre seam
    d.rectangle([6, 6, W - 7, H - 7], outline=INK, width=2)
    d.rectangle([12, 12, W - 13, H - 13], outline=GOLD, width=1)
    d.line([512, 14, 512, H - 14], fill=(60, 60, 50, 90), width=2)
    d.line([510, 14, 510, H - 14], fill=(255, 255, 255, 60), width=1)

    # ---------------------------------------------------------- LEFT PAGE
    coat_of_arms(d, 56, 52, 27)
    d.text((94, 26), "REPUBLIC OF MERIDIA", font=font(SERIFB, 25),
           fill=INK)
    d.text((94, 58), "P A S S P O R T   ·   P A S S E P O R T",
           font=font(SANS, 12), fill=GOLD)
    d.line([26, 88, 486, 88], fill=GOLD, width=2)
    d.line([26, 92, 486, 92], fill=INK, width=1)

    # portrait
    d.rectangle([24, 106, 168, 270], outline=INK, width=2)
    img.alpha_composite(portrait(), (26, 108))
    d.text((26, 274), "PHOTOGRAPH OF HOLDER", font=font(SANS, 8), fill=GREY)

    # data fields, right of portrait
    fx = 184
    field(d, fx, 106, "TYPE", "P", font(SANSB, 16))
    field(d, fx + 62, 106, "CODE", "MER", font(SANSB, 16))
    field(d, fx + 140, 106, "PASSPORT No.", "MD 4829137", font(SANSB, 16))
    field(d, fx, 150, "SURNAME", "VOSS", font(SANSB, 20))
    field(d, fx, 196, "GIVEN NAMES", "ELENA MARIS", font(SANSB, 17))
    field(d, fx, 238, "NATIONALITY", "MERIDIAN", font(SANSB, 15))
    field(d, fx + 150, 238, "SEX", "F", font(SANSB, 15))
    # full-width rows below photo
    field(d, 26, 300, "DATE OF BIRTH", "14 MAR 1988", font(SANSB, 15))
    field(d, 250, 300, "PLACE OF BIRTH", "PORT MERIDIA", font(SANSB, 15))
    field(d, 26, 344, "DATE OF ISSUE", "12 JUN 2023", font(SANSB, 15))
    field(d, 250, 344, "DATE OF EXPIRY", "11 JUN 2033", font(SANSB, 15))
    field(d, 26, 388, "AUTHORITY", "PORT MERIDIA PASSPORT OFFICE",
          font(SANSB, 15))
    # signature
    d.rectangle([26, 436, 486, 492], outline=INK, width=1)
    d.text((34, 442), "HOLDER'S SIGNATURE", font=font(SANS, 9), fill=GREY)
    signature(d, 200, 448)
    d.text((34, 500), "This passport remains the property of the Republic of "
           "Meridia and must be surrendered on demand.",
           font=font(SANSI, 10), fill=GREY)
    d.line([26, 524, 486, 524], fill=RULE, width=1)
    # MRZ
    mf = font(MONOB, 17)
    d.text((26, 538), l1, font=mf, fill=INK)
    d.text((26, 560), l2, font=mf, fill=INK)
    d.text((26, 592), "<<  MERIDIAN  ·  SOUTH ATLANTIC  ·  EST. 1962  >>",
           font=font(SANS, 9), fill=GREY)
    d.text((26, 692), "DATA PAGE", font=font(SANS, 9), fill=GREY)

    # ---------------------------------------------------------- RIGHT PAGE
    d.text((538, 22), "VISAS", font=font(SERIFB, 24), fill=INK)
    d.text((900, 34), "PAGE 14", font=font(SANS, 11), fill=GREY)
    d.line([538, 60, 998, 60], fill=GOLD, width=2)
    d.line([538, 64, 998, 64], fill=INK, width=1)

    # faint diagonal watermark
    wm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wm)
    wf = font(SERIFB, 92)
    wd.text((560, 250), "MERIDIA", font=wf, fill=(20, 96, 110, 16))
    wm = wm.rotate(-24, center=(780, 300), resample=Image.BICUBIC)
    img.alpha_composite(wm)
    d = ImageDraw.Draw(img)

    BLUE = (30, 80, 140, 215)
    PURPLE = (110, 60, 140, 215)
    GREEN = (30, 110, 70, 215)
    RUST = (150, 60, 40, 215)

    s1 = stamp_layer(216, 172, "oval", BLUE,
                     [("ARRIVAL", True), ("02 SEP 2023", False),
                      ("DEPARTURE", True), ("09 SEP 2023", False)],
                     title="PORTO AZZURRO")
    paste_rotated(img, s1, 650, 152, -8)
    s2 = stamp_layer(180, 180, "circle", PURPLE,
                     [("ARRIVAL", True), ("18 JAN 2024", False),
                      ("DEPARTURE", True), ("25 JAN 2024", False)],
                     title="CALDARA")
    paste_rotated(img, s2, 890, 158, 7)
    s3 = stamp_layer(224, 128, "rect", GREEN,
                     [("ENTRY  07 JUL 2024", True),
                      ("EXIT  21 JUL 2024", True)],
                     title="ISLE OF VEY")
    paste_rotated(img, s3, 652, 330, 5)
    s4 = stamp_layer(224, 128, "rect", RUST,
                     [("ENTRY  03 NOV 2025", True),
                      ("EXIT  10 NOV 2025", True)],
                     title="PORTO AZZURRO")
    paste_rotated(img, s4, 888, 332, -6)

    # visa condition box
    d.rectangle([538, 480, 998, 616], outline=INK, width=2)
    d.rectangle([544, 486, 992, 610], outline=GOLD, width=1)
    d.rectangle([538, 480, 998, 506], fill=INK)
    d.text((550, 486), "VISA CONDITION  —  CONDITION DE VISA",
           font=font(SANSB, 13), fill=(247, 242, 228))
    body = ("HOLDER IS EXEMPT FROM THE MERIDIAN HARBOUR LEVY WHILE IN "
            "TRANSIT. VALID FOR ALL COUNTRIES EXCEPT THE NORTHERN REACHES.")
    lines = wrap(d, body, font(SANS, 13), 430)
    y = 516
    for ln in lines:
        d.text((550, y), ln, font=font(SANS, 13), fill=INK)
        y += 19
    d.text((550, y + 6), "Issued at Port Meridia · 12 JUN 2023",
           font=font(SANSI, 11), fill=GREY)

    # fee stamp, sitting just above the visa-condition box
    fee = stamp_layer(210, 68, "rect", (176, 120, 30, 235),
                      [("HARBOUR LEVY PAID", True), ("40 CROWNS", True)])
    paste_rotated(img, fee, 880, 444, -5)

    d.text((538, 692), "REPUBLIC OF MERIDIA · SOUTH ATLANTIC",
           font=font(SANS, 9), fill=GREY)
    d.text((972, 692), "14", font=font(SANS, 9), fill=GREY)

    out = os.path.join(HERE, "entry.png")
    img.convert("RGB").save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
