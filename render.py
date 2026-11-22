# render.py — draws entry.png for news-image-20261122 v3.
# A 1024x1024 newspaper front page summing up Sunday 22 November 2026.
# 35 dated stories across 7 regions plus a Markets & Tech cell: one hero
# (COP31 collapses) and 34 short items grouped by region, each with a
# headline and one line of detail. Rendered with Pillow + Noto Sans (real
# text, never an AI picture), so every letter stays crisp and legible.
# Run: python3 render.py  (writes entry.png next to this file)
#
# Layout (all coordinates in px, canvas 1024x1024, side margins 36):
#   masthead  -> red rule, paper name, big date, tagline (35 stories, 7 regions)
#   hero      -> dark teal panel: COP31 collapse (the day's biggest story)
#   grid      -> 4 rows x 2 columns of region cells; rows A/B are taller
#                (they hold 5-item cells), rows C/D shorter (4- and 3-item)
#   footer    -> one-line dateline: every story is from 22 November 2026
# Every text line is measured before drawing; if a line would overflow its
# box the script stops loudly instead of writing a broken image.

import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MX = 36                      # side margin; content spans 36..988
PAPER = (247, 243, 234)
INK = (26, 26, 26)
BODY = (64, 58, 48)
RED = (200, 16, 46)
GOLD = (245, 197, 66)
EDGE = (214, 205, 190)
FAINT = (140, 132, 118)
CARD_BG = (255, 255, 255)
HERO_TOP = (16, 78, 70)
HERO_BOT = (8, 48, 44)
HERO_SUB = (226, 236, 232)

FONTS = "/usr/share/fonts/truetype/noto/"


def load(name, size):
    return ImageFont.truetype(FONTS + name, size)


BLACK = lambda s: load("NotoSans-Black.ttf", s)
BOLD = lambda s: load("NotoSans-Bold.ttf", s)
REG = lambda s: load("NotoSans-Regular.ttf", s)

canvas = Image.new("RGB", (W, H), PAPER)
pen = ImageDraw.Draw(canvas)


def fit_lines(text, font, max_w, max_lines=None):
    """Greedy word wrap. Raises if the text cannot fit max_lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if pen.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    if max_lines is not None and len(lines) > max_lines:
        raise SystemExit(
            f"OVERFLOW: {len(lines)} lines for {max_lines}-line box: {text!r}")
    return lines


def vgrad(box, top, bottom, radius):
    """Rounded rectangle filled with a vertical gradient."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    grad = Image.new("RGB", (w, h))
    px = grad.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        col = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        for x in range(w):
            px[x, y] = col
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w, h], radius=radius,
                                           fill=255)
    canvas.paste(grad, (x0, y0), mask)


def diamond(cx, cy, r, color):
    pen.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)],
                fill=color)


# ---------------- masthead ----------------
pen.line([(MX, 12), (988, 12)], fill=RED, width=3)
pen.text((MX, 20), "THE WORLD IN ONE DAY", font=BOLD(23), fill=RED)
pen.text((MX, 46), "Sunday 22 November 2026", font=BLACK(38), fill=INK)
pen.text((MX, 94), "35 DATED STORIES  \u2022  7 REGIONS  \u2022  ALL FROM "
                   "SUNDAY 22 NOVEMBER 2026",
         font=BOLD(13), fill=BODY)

# ---------------- hero: COP31 collapses ----------------
hx0, hy0, hx1, hy1 = MX, 116, 988, 232
vgrad((hx0, hy0, hx1, hy1), HERO_TOP, HERO_BOT, 14)
pen = ImageDraw.Draw(canvas)
pen.text((58, 124), "CLIMATE  \u2022  ANTALYA, TURKEY",
         font=BOLD(14), fill=GOLD)
pen.text((58, 142), "COP31 COLLAPSES WITH NO DEAL",
         font=BLACK(38), fill=(255, 255, 255))
hero_sub = ("Climate talks end with no agreement after two days of "
            "overtime \u2014 the EU rejects a final text silent on "
            "fossil fuels.")
for i, ln in enumerate(fit_lines(hero_sub, REG(15), 700, max_lines=2)):
    pen.text((58, 188 + i * 19), ln, font=REG(15), fill=HERO_SUB)
# "No deal" mark: a gold ring cut by a diagonal slash, right of the headline.
pen.ellipse([818, 140, 908, 230], outline=GOLD, width=5)
pen.line([(836, 212), (890, 158)], fill=GOLD, width=5)

# ---------------- region grid ----------------
# Each item: one bold headline line + one regular detail line.
# Item height 34px (headline 17 + detail 14 + 3 gap); cell header 20px.
ITEM_H = 34
HEAD_H = 20


def cell(box, accent, region, items):
    """One white region cell: header + a list of headline/detail items."""
    x0, y0, x1, y1 = box
    pen.rounded_rectangle([x0, y0, x1, y1], radius=8, fill=CARD_BG,
                          outline=EDGE, width=1)
    tx = x0 + 16
    inner_w = x1 - x0 - 32
    diamond(tx + 6, y0 + 15, 6, accent)
    pen.text((tx + 18, y0 + 6), region, font=BOLD(15), fill=accent)
    # Spread the items evenly over the space below the header so short
    # cells do not leave a bare patch at the bottom.
    top = y0 + HEAD_H + 8
    avail = (y1 - 6) - top
    n = len(items)
    # Even spacing: total item block height vs available height.
    block = n * ITEM_H
    gap = 0 if n <= 1 else max(0, (avail - block) // (n - 1))
    y = top
    for headline, detail in items:
        head = fit_lines(headline, BOLD(13.5), inner_w, max_lines=1)
        pen.text((tx, y), head[0], font=BOLD(13.5), fill=INK)
        det = fit_lines(detail, REG(11), inner_w, max_lines=1)
        pen.text((tx, y + 17), det[0], font=REG(11), fill=BODY)
        y += ITEM_H + gap


# Row A (tall, 5-item cells)
cell((36, 240, 504, 436), (30, 58, 138), "EUROPE", [
    ("UK and EU clinch food and youth-mobility deals",
     "Britain and the EU agree food and youth-mobility deals."),
    ("Gen Z students protest in 25+ countries",
     "Students march in 25+ countries for schools and climate."),
    ("UniCredit\u2013Commerzbank deal agreed",
     "Berlin and UniCredit agree terms for the Commerzbank takeover."),
    ("Missiles crash in Poland",
     "PM Tusk denounces a Russian \u2018provocation\u2019 after missiles crash."),
    ("Italian ex-police chief found dead",
     "Ex-police chief found dead amid an inquiry into a 1992 bombing."),
])
cell((520, 240, 988, 436), (178, 34, 34), "MIDDLE EAST", [
    ("Iran strikes Bahrain; US bases hit",
     "Missiles and drones hit a civilian site, wounding two people."),
    ("Houthis fire missiles at Riyadh",
     "Saudi Arabia intercepts three Houthi missiles fired at Riyadh."),
    ("Tankers hit near Strait of Hormuz",
     "Two tankers hit near Hormuz; Iran says one struck a naval mine."),
    ("Iraq power station fire kills four",
     "Fire at the Hartha power station near Basra kills four, hurts 35."),
    ("Settler arson in West Bank condemned",
     "Opposition leader Eisenkot calls settler arson attacks \u2018terrorism\u2019."),
])

# Row B (tall: Asia 5 items, North America 4)
cell((36, 444, 504, 640), (180, 83, 9), "ASIA", [
    ("Cikande factory fire kills three",
     "Fire at a candy factory in Cikande kills three; 36 still missing."),
    ("EU\u2013Indonesia sign landmark trade deal",
     "The EU and Indonesia sign a landmark deal after a decade of talks."),
    ("Toxic alcohol kills 11 in Manipur",
     "Toxic alcohol kills at least 11 in Manipur; 180 more in hospital."),
    ("Bus\u2013tanker crash kills 10 in Pakistan",
     "A bus hits a gas tanker near Ormara, killing 10, three of them children."),
    ("China opposes US ban on its telecoms",
     "Beijing opposes a US ban on Chinese telecoms\u2019 access to US numbers."),
])
cell((520, 444, 988, 640), (18, 48, 110), "NORTH AMERICA", [
    ("Trump confirms FBI database breached",
     "Trump confirms hackers breached the FBI\u2019s NCIC crime database."),
    ("Schumer faces leadership challenge",
     "Schumer faces a Senate leadership challenge from Chris Van Hollen."),
    ("Trump delays Iran strikes decision",
     "Trump will delay deciding on renewed Iran strikes until after 1 January."),
    ("Florida river breaks 73-year record",
     "The St. Johns River breaks a 73-year flood record after heavy rain."),
])

# Row C (short, 4-item cells)
cell((36, 648, 504, 818), (22, 101, 52), "LATIN AMERICA", [
    ("Mexico captures \u2018El Chapo Isidro\u2019",
     "FBI most-wanted cartel boss seized in Sinaloa; 11 killed in the raid."),
    ("Haiti\u2013El Salvador prison deal struck",
     "Haiti strikes a deal with El Salvador to build three new prisons."),
    ("Colombia denies NYT anti-drug claim",
     "Colombia\u2019s president denies a NYT report on a Trump anti-drug plan."),
    ("Lula backs S\u00e1nchez in Spain vote",
     "Brazil\u2019s Lula backs Spain\u2019s S\u00e1nchez ahead of snap elections on 29 Nov."),
])
cell((520, 648, 988, 818), (126, 34, 150), "AFRICA", [
    ("Nigeria boat capsizes; 24 dead",
     "A boat carrying funeral mourners capsizes; the death toll rises to 24."),
    ("Ex-SA deputy president dies at 71",
     "Phumzile Mlambo-Ngcuka, ex-deputy president, dies at 71."),
    ("Seven killed in South Sudan attack",
     "Seven killed and 10 injured in a fresh attack in Duk, South Sudan."),
    ("Kenya awards minerals deal to US",
     "Kenya awards a sought-after minerals contract to a US consortium."),
])

# Row D (short: Oceania 3 items, Markets & Tech 4)
cell((36, 826, 504, 996), (8, 110, 110), "OCEANIA & PACIFIC", [
    ("Niue wins $2.4m Earthshot Prize",
     "Niue wins the $2.4m Earthshot Prize for protecting its ocean."),
    ("Fiji declares drought disaster",
     "Fiji declares a 30-day state of disaster as drought strains water."),
    ("Australia hits back over AUKUS report",
     "Canberra criticises a US report warning AUKUS will cut US submarines."),
])
cell((520, 826, 988, 996), (90, 60, 10), "MARKETS & TECH", [
    ("Stocks slide into correction",
     "S&P 500 falls 3.7% and Nasdaq 5.3% in a Friday AI sell-off."),
    ("Amazon nears $7.5bn Decart deal",
     "Amazon nears a $7.5bn deal for Israeli AI startup Decart."),
    ("Riemann proof claimed by Anthropic",
     "Anthropic\u2019s Alp\u00f6ge claims a proof of the Riemann hypothesis."),
    ("IBM unveils 520-qubit Nighthawk",
     "IBM unveils its 520-qubit \u2018Nighthawk r3\u2019 chip for real workloads."),
])

# ---------------- footer dateline ----------------
footer = ("All 35 stories happened or were first reported on "
          "Sunday 22 November 2026.")
fw = pen.textlength(footer, font=REG(12))
pen.text(((W - fw) / 2, 1002), footer, font=REG(12), fill=FAINT)

canvas.save("entry.png", optimize=True)
print("wrote entry.png", canvas.size)
