#!/usr/bin/env python3
"""Render the news-image-20261124 v2 front page: one image of Tuesday 24 November 2026.

Flat editorial illustration, drawn entirely with PIL shapes. Deterministic output:
no randomness, no timestamps, no network.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

# ---------------------------------------------------------------- palette
PAPER   = (246, 241, 231)
INK     = (26, 26, 26)
NAVY    = (18, 40, 75)
NAVY2   = (31, 62, 110)
GOLD    = (232, 196, 104)
RED     = (192, 57, 43)
TEAL    = (14, 124, 107)
AMBER   = (217, 142, 0)
BLUE    = (31, 95, 168)
GREEN   = (30, 122, 52)
PINK    = (194, 24, 91)
ORANGE  = (230, 126, 34)
PURPLE  = (125, 60, 152)
BROWN   = (93, 64, 55)
GREY    = (120, 120, 116)
LIGHT   = (255, 255, 255)
SKY     = (214, 231, 240)
SAND    = (238, 226, 200)
BAND    = (232, 228, 216)

REGION_COLORS = {
    "N AMERICA": (192, 57, 43), "S AMERICA": (125, 60, 152),
    "EUROPE": (31, 95, 168), "MIDDLE EAST": (183, 121, 31),
    "AFRICA": (14, 124, 107), "E ASIA": (194, 24, 91),
    "S ASIA": (230, 126, 34), "SE ASIA": (46, 125, 50),
    "OCEANIA": (93, 64, 55), "GLOBAL": (120, 120, 116),
}
BADGE_COLORS = {"OFFICIAL": (30, 122, 52), "CONFIRMED": (31, 95, 168),
                "REPORTED": (183, 121, 31)}

# ---------------------------------------------------------------- fonts
FD = "/usr/share/fonts/truetype/dejavu"
SERIF = os.path.join(FD, "DejaVuSerif-Bold.ttf")
SERIF_R = os.path.join(FD, "DejaVuSerif.ttf")
SANS = os.path.join(FD, "DejaVuSans.ttf")
SANS_B = os.path.join(FD, "DejaVuSans-Bold.ttf")


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, font, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, font, fill, max_w, line_h, max_lines=None):
    lines = wrap(draw, text, font, max_w)
    if max_lines is not None:
        lines = lines[:max_lines]
    for i, ln in enumerate(lines):
        draw.text((x, y + i * line_h), ln, font=font, fill=fill)
    return y + len(lines) * line_h


def fit(draw, text, font_path, size, max_w, max_lines, min_size=8):
    """Shrink font until text fits max_w x max_lines; returns (font, lines)."""
    while size >= min_size:
        font = F(font_path, size)
        lines = wrap(draw, text, font, max_w)
        if len(lines) <= max_lines:
            return font, lines
        size -= 1
    font = F(font_path, min_size)
    return font, wrap(draw, text, font, max_w)[:max_lines]


def badge(draw, x, y, text, color, size=9):
    font = F(SANS_B, size)
    tw = draw.textlength(text, font=font)
    w = int(tw) + 12
    h = size + 7
    draw.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=color)
    draw.text((x + 6, y + 3), text, font=font, fill=LIGHT)
    return w


def label_tab(draw, x, y, text, color=RED, size=11):
    font = F(SANS_B, size)
    tw = draw.textlength(text, font=font)
    draw.rectangle([x, y, x + tw + 12, y + size + 8], fill=color)
    draw.text((x + 6, y + 4), text, font=font, fill=LIGHT)
    return tw + 12

# ---------------------------------------------------------------- data
LEADS = [
    dict(banner="50,018", color=NAVY, scene="markets",
         head="DOW TOPS 50,000 AS TECH SELLS OFF",
         body="The Dow closes above 50,000 for the first time, up 0.9%, while the "
              "Nasdaq falls 1.5% and Nvidia drops 5.9% a day after its 31% surge.",
         badge="OFFICIAL"),
    dict(banner="\u221245%", color=RED, scene="refinery",
         head="PUTIN VOWS RETALIATION AS REFINERY STRIKES BITE",
         body="Moscow says Ukraine keeps hitting its oil plants despite Trump's plea; "
              "Kyiv's drone campaign has cut Russian refining by 45% since late October.",
         badge="CONFIRMED"),
    dict(banner="7 KILLED", color=(90, 60, 30), scene="gaza",
         head="ISRAEL KILLS HAMAS SECURITY CHIEF IN GAZA",
         body="Airstrikes kill Naeem Abu Nahel, head of Hamas's internal security, and "
              "six others, including two police officers, medics say.",
         badge="CONFIRMED"),
]

TILES = [
    dict(num="79TH", color=ORANGE, scene="turkey",
         head="TRUMP PARDONS TURKEYS, RAGES AT MIDTERMS",
         body="Two birds spared; Giuliani gets the Medal of Freedom too.", badge="CONFIRMED"),
    dict(num="2009", color=TEAL, scene="climate",
         head="EU TO REWRITE COP RULES AFTER NO-DEAL",
         body="EU to push UN voting reform after the first no-deal since 2009.", badge="REPORTED"),
    dict(num="1ST", color=BLUE, scene="radar",
         head="GERMANY FIRST INTO UKRAINE'S DELTA SYSTEM",
         body="Berlin signs for Kyiv's battlefield software, plus more missiles.", badge="OFFICIAL"),
    dict(num="26", color=RED, scene="factory",
         head="INDONESIA FIRE TOLL RISES TO 26",
         body="Blaze in Serang leaves 28 missing; most died fleeing to the exit.", badge="OFFICIAL"),
    dict(num="$1.62BN", color=(183, 121, 31), scene="train",
         head="INDIA\u2013NEPAL SEAL $1.62BN PARTNERSHIP",
         body="Ten-pillar vision, aid and a new Ayodhya\u2013Janakpur rail link.", badge="OFFICIAL"),
    dict(num="$375K", color=PINK, scene="korea",
         head="SEOUL PUTS A BOUNTY ON AI CHEATS",
         body="Up to $375,000 for tips on AI cheating in the college entrance exam.", badge="CONFIRMED"),
    dict(num="5\u20131", color=(46, 125, 50), scene="soccer",
         head="REAL MADRID HIT FIVE IN PSV COMEBACK",
         body="Mbapp\u00e9 scores twice in the comeback; Arsenal and City held.", badge="OFFICIAL"),
    dict(num="USSF-266", color=NAVY, scene="rocket",
         head="SPACEX LOFTS SECRET SPACE FORCE PAYLOAD",
         body="Falcon 9 lifts off; its booster lands on a drone ship in the Pacific.", badge="OFFICIAL"),
    dict(num="5%", color=PURPLE, scene="shield",
         head="AUSTRALIA: SUE TECH GIANTS, FINES TO 5%",
         body="Canberra deal lets people sue platforms over harmful content.", badge="REPORTED"),
    dict(num="24H", color=TEAL, scene="congo",
         head="FIGHTING TRAPS EBOLA TEAMS IN CONGO",
         body="Fighting near a hospital forces Ebola teams to take cover, WHO says.", badge="OFFICIAL"),
]

UTC_EVENTS = [
    ("01:00", "Bulls beat the Cavaliers 122\u2013108 in Chicago"),
    ("06:55", "Space-medicine study published in Adelaide"),
    ("14:50", "Indonesia factory fire toll confirmed at 26"),
    ("15:55", "Falcon 9 launches classified USSF-266"),
    ("19:40", "Putin vows retaliation over refinery strikes"),
    ("19:53", "Trump pardons the Thanksgiving turkeys"),
    ("21:00", "Dow closes above 50,000 for the first time"),
]

NUMBERS = [
    ("50,018", "Dow's first close over 50,000"),
    ("\u22121.48%", "Nasdaq's Tuesday fall"),
    ("1,848", "Russian troops lost today"),
    ("26", "dead in the Indonesia fire"),
    ("103.3", "US consumer confidence"),
    ("$375K", "Korea's bounty on AI cheats"),
]

INDEX = [
    ("MOLDOVA", "7 Russian drones in airspace", "Airspace tightened near Chi\u0219in\u0103u", "EUROPE", "CONFIRMED"),
    ("NATO", "Chief vows space defence", "After reports of a Russian nuclear satellite", "EUROPE", "REPORTED"),
    ("IRAQ", "PM seizes Kurdish oilfields", "Ministry to run fields in 4 provinces", "MIDDLE EAST", "CONFIRMED"),
    ("LIBYA", "UN demands Benghazi probe", "Strikes hit the port and coast on Sunday", "AFRICA", "OFFICIAL"),
    ("SOMALIA", "Anti-Shabaab fight steps up", "As the AU withdrawal begins", "AFRICA", "REPORTED"),
    ("HUNGARY", "Zelensky meets PM Magyar", "Gas, diesel and new train links agreed", "EUROPE", "CONFIRMED"),
    ("PENTAGON", "Hegseth holds ~60 Patriots", "Allies paid; Kyiv waits for air defence", "N AMERICA", "REPORTED"),
    ("ECONOMY", "Confidence jumps to 103.3", "Best reading since January 2025", "N AMERICA", "OFFICIAL"),
    ("ASIA", "Kospi +6.3%, Nikkei +3.9%", "Kospi back above 5,000", "E ASIA", "CONFIRMED"),
    ("MARKETS", "Gold \u22122.7%, oil +1.8%", "WTI $81.63 \u00b7 Gold $3,552.80", "GLOBAL", "CONFIRMED"),
    ("ECUADOR", "90-day flood emergency", "El Ni\u00f1o rains flood Babahoyo parishes", "S AMERICA", "REPORTED"),
    ("CHESS", "Youngest final ever opens", "Game 1 opens in Geneva, both aged 20", "EUROPE", "CONFIRMED"),
    ("INDIA", "Keeps 3rd in Asia Power Index", "Score 40.5, Lowy Institute", "S ASIA", "OFFICIAL"),
    ("BANGLADESH", "Hasina to return 16 Dec", "After two years' exile in India", "S ASIA", "CONFIRMED"),
    ("PAPUA N.G.", "Bougainville vote", "Ratifying the 2019 independence vote", "OCEANIA", "REPORTED"),
    ("SCIENCE", "Space drugs pass orbit test", "Coating keeps drugs stable in orbit", "OCEANIA", "OFFICIAL"),
    ("CHINA", "Threatens EU with sanctions", "Beijing hits back over trade curbs", "E ASIA", "REPORTED"),
    ("POLLS", "Trump approval 45%, term low", "Morning Consult tracking", "N AMERICA", "CONFIRMED"),
    ("STARLINK", "Zelensky slams limits", "In a Bloomberg interview", "EUROPE", "REPORTED"),
    ("KERCH", "Ukraine hits the bridge again", "Road and rail spans damaged", "EUROPE", "REPORTED"),
    ("SANOFI", "$41bn deal lifts Insmed 14%", "Healthcare leads the Dow's day", "N AMERICA", "CONFIRMED"),
    ("RETAIL", "Dick's +14.6%, Dollar Tree +11%", "Strong earnings save the Dow", "N AMERICA", "CONFIRMED"),
    ("NATO SKIES", "25 airspace probes in 2026", "Four times the 2024 total", "EUROPE", "CONFIRMED"),
    ("HEALTH", "India passes 10m HPV doses", "One crore jabs given", "S ASIA", "OFFICIAL"),
]

# ---------------------------------------------------------------- scenes
def scene_markets(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(223, 233, 240))
    d.rectangle([x, y + h - 26, x + w, y + h], fill=(200, 214, 224))
    # gold 50,000 line
    ly = y + 52
    d.line([x + 6, ly, x + w - 6, ly], fill=GOLD, width=3)
    d.text((x + w - 52, ly - 16), "50,000", font=F(SANS_B, 10), fill=(150, 110, 20))
    # candlesticks
    bars = [(16, 30, 58, 26, GREEN), (44, 22, 44, 20, GREEN), (72, 34, 62, 28, RED),
            (100, 26, 70, 22, GREEN), (128, 18, 78, 18, GREEN), (156, 30, 88, 26, RED),
            (184, 14, 96, 16, GREEN), (212, 20, 104, 20, GREEN)]
    for bx, bt, bb, bw2, c in bars:
        d.rectangle([x + bx, y + bt, x + bx + 12, y + bb], fill=c)
        d.line([x + bx + 6, y + bt - 8, x + bx + 6, y + bb + 8], fill=c, width=2)
    # navy arrow: rise then dip
    pts = [(x + 10, y + h - 34), (x + 90, y + 44), (x + 170, y + 30), (x + w - 14, y + 62)]
    d.line(pts, fill=NAVY, width=4, joint="curve")
    d.polygon([(x + w - 14, y + 62), (x + w - 30, y + 56), (x + w - 28, y + 72)], fill=NAVY)


def scene_refinery(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(43, 48, 66))
    for sx, sy in [(30, 22), (90, 14), (160, 26), (220, 16), (270, 24)]:
        d.ellipse([x + sx, y + sy, x + sx + 4, y + sy + 4], fill=(200, 200, 200))
    gy = h - 34
    d.rectangle([x, y + gy, x + w, y + h], fill=(24, 26, 36))
    # towers
    for tx, th in [(20, 62), (70, 84), (150, 70), (210, 58)]:
        d.rectangle([x + tx, y + gy - th, x + tx + 34, y + gy], fill=(120, 128, 140))
        d.rectangle([x + tx + 6, y + gy - th - 12, x + tx + 28, y + gy - th], fill=(90, 98, 110))
    # flame
    fx, fy = x + w - 78, y + 26
    d.polygon([(fx, fy + 46), (fx + 14, fy + 10), (fx + 28, fy + 46)], fill=(230, 126, 34))
    d.polygon([(fx + 8, fy + 46), (fx + 14, fy + 24), (fx + 22, fy + 46)], fill=(240, 200, 60))
    # smoke
    for sx, sy, r in [(60, 18, 9), (80, 12, 11), (104, 18, 8)]:
        d.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r], fill=(150, 150, 150))


def scene_gaza(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SAND)
    d.rectangle([x, y, x + w, y + 34], fill=(245, 222, 179))
    gy = h - 30
    d.rectangle([x, y + gy, x + w, y + h], fill=(190, 170, 140))
    # buildings
    for bx, bw, bh in [(14, 44, 56), (66, 36, 74), (110, 48, 48), (166, 40, 66), (214, 46, 52),
                       (268, 36, 60)]:
        d.rectangle([x + bx, y + gy - bh, x + bx + bw, y + gy], fill=(150, 138, 122))
        for wy in range(3):
            for wx in range(2):
                d.rectangle([x + bx + 6 + wx * 16, y + gy - bh + 8 + wy * 16,
                             x + bx + 12 + wx * 16, y + gy - bh + 14 + wy * 16],
                            fill=(90, 80, 66))
    # blast + smoke
    d.polygon([(x + 235, y + 18), (x + 245, y + 34), (x + 262, y + 30), (x + 252, y + 46),
               (x + 262, y + 58), (x + 242, y + 56), (x + 238, y + 70), (x + 228, y + 54),
               (x + 212, y + 58), (x + 222, y + 44), (x + 210, y + 34), (x + 228, y + 32)],
              fill=(240, 160, 40))
    for sx, sy, r in [(150, 26, 12), (172, 16, 14), (196, 26, 10)]:
        d.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r], fill=(170, 165, 155))


def scene_turkey(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(198, 226, 190))
    d.rectangle([x, y + h - 22, x + w, y + h], fill=(140, 180, 120))
    cx, cy = x + w // 2 - 10, y + h // 2 + 8
    # tail feathers
    for a, c in [(-38, (150, 90, 40)), (-19, (180, 120, 50)), (0, (200, 140, 60)),
                 (19, (180, 120, 50)), (38, (150, 90, 40))]:
        import math
        rad = math.radians(a)
        ex, ey = cx + int(34 * math.sin(rad)), cy - 18 - int(30 * math.cos(rad))
        d.line([cx, cy - 8, ex, ey], fill=c, width=7)
    # body + head
    d.ellipse([cx - 26, cy - 22, cx + 26, cy + 22], fill=(120, 72, 30))
    d.ellipse([cx + 8, cy - 44, cx + 34, cy - 18], fill=(120, 72, 30))
    d.polygon([(cx + 30, cy - 36), (cx + 44, cy - 30), (cx + 30, cy - 28)], fill=(240, 180, 40))
    d.ellipse([cx + 26, cy - 30, cx + 30, cy - 26], fill=(240, 60, 40))
    d.ellipse([cx + 16, cy - 38, cx + 20, cy - 34], fill=INK)
    # medal
    mx, my = x + w - 34, y + h - 40
    d.ellipse([mx - 14, my - 14, mx + 14, my + 14], fill=GOLD, outline=(150, 110, 20), width=2)
    d.polygon([(mx, my - 8), (mx + 2, my - 2), (mx + 8, my - 2), (mx + 3, my + 2),
               (mx + 5, my + 8), (mx, my + 4), (mx - 5, my + 8), (mx - 3, my + 2),
               (mx - 8, my - 2), (mx - 2, my - 2)], fill=(150, 110, 20))


def scene_climate(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 231, 240))
    cx, cy, r = x + w // 2, y + h // 2 - 4, 44
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(60, 140, 200))
    d.ellipse([cx - 30, cy - 26, cx - 2, cy - 6], fill=(80, 170, 90))
    d.ellipse([cx + 4, cy + 4, cx + 30, cy + 24], fill=(80, 170, 90))
    d.ellipse([cx - 12, cy + 14, cx + 8, cy + 30], fill=(80, 170, 90))
    # crack
    d.line([(cx - 8, cy - r), (cx + 2, cy - 12), (cx - 6, cy + 6), (cx + 4, cy + r)],
           fill=(240, 240, 240), width=3)
    # NO DEAL band
    d.rectangle([x, y + h - 30, x + w, y + h - 8], fill=RED)
    d.text((x + w // 2 - 26, y + h - 28), "NO DEAL", font=F(SANS_B, 13), fill=LIGHT)


def scene_radar(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 60, 40))
    cx, cy, r = x + w // 2, y + h // 2 + 6, 46
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(80, 220, 150), width=2)
    d.ellipse([cx - r // 2, cy - r // 2, cx + r // 2, cy + r // 2], outline=(80, 220, 150), width=1)
    d.line([cx - r, cy, cx + r, cy], fill=(80, 220, 150), width=1)
    d.line([cx, cy - r, cx, cy + r], fill=(80, 220, 150), width=1)
    d.pieslice([cx - r, cy - r, cx + r, cy + r], start=300, end=345, fill=(40, 160, 110))
    for bx, by in [(cx - 22, cy - 18), (cx + 16, cy + 8), (cx + 4, cy - 26), (cx - 8, cy + 20)]:
        d.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill=(240, 220, 80))
    # German flag corner
    fx, fy = x + 8, y + h - 26
    for i, c in enumerate([(0, 0, 0), (221, 0, 0), (255, 206, 0)]):
        d.rectangle([fx, fy + i * 6, fx + 34, fy + i * 6 + 6], fill=c)


def scene_factory(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(228, 224, 214))
    gy = h - 24
    d.rectangle([x, y + gy, x + w, y + h], fill=(180, 172, 158))
    # sawtooth factory
    d.polygon([(x + 12, y + gy), (x + 12, y + 40), (x + 52, y + 18), (x + 92, y + 40),
               (x + 132, y + 18), (x + 172, y + 40), (x + 172, y + gy)], fill=(110, 110, 108))
    # windows with flames
    for wx in [30, 70, 110, 148]:
        d.rectangle([x + wx, y + 62, x + wx + 16, y + 78], fill=(240, 200, 60))
        d.polygon([(x + wx + 2, y + 78), (x + wx + 8, y + 60), (x + wx + 14, y + 78)],
                  fill=(230, 110, 30))
    # chimney + smoke
    d.rectangle([x + w - 30, y + 14, x + w - 18, y + 52], fill=(90, 90, 88))
    for sx, sy, r in [(x + w - 40, y + 8, 8), (x + w - 52, y + 2, 10)]:
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(160, 158, 150))
    # exit sign
    d.rectangle([x + 8, y + 8, x + 46, y + 22], fill=(30, 122, 52))
    d.text((x + 12, y + 10), "EXIT", font=F(SANS_B, 9), fill=LIGHT)


def scene_train(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 232, 240))
    # flags
    for fx, (c1, c2, c3) in [(x + 18, ((255, 153, 51), LIGHT, (19, 136, 8))),
                             (x + w - 58, ((220, 20, 60), (0, 56, 147), (220, 20, 60)))]:
        d.line([fx + 20, y + 6, fx + 20, y + 34], fill=(90, 90, 90), width=2)
        for i, c in enumerate([c1, c2, c3]):
            d.rectangle([fx + 20, y + 6 + i * 8, fx + 52, y + 14 + i * 8], fill=c)
    # train
    ty = y + h - 46
    d.rectangle([x + 14, ty, x + w - 14, ty + 30], fill=(31, 95, 168))
    d.rectangle([x + 14, ty, x + 52, ty + 30], fill=(18, 40, 75))
    for wx in range(60, w - 22, 26):
        d.rectangle([x + wx, ty + 7, x + wx + 16, ty + 19], fill=(200, 225, 245))
    d.ellipse([x + 34, ty + 22, x + 44, ty + 32], fill=INK)
    d.ellipse([x + w - 44, ty + 22, x + w - 34, ty + 32], fill=INK)
    d.line([x + 6, ty + 34, x + w - 6, ty + 34], fill=(90, 90, 90), width=3)


def scene_korea(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 231, 245))
    # jet
    jx, jy = x + 30, y + 18
    d.polygon([(jx, jy + 8), (jx + 46, jy), (jx + 58, jy + 8), (jx + 46, jy + 14),
               (jx + 30, jy + 22), (jx + 26, jy + 12)], fill=(60, 60, 70))
    d.line([jx - 6, jy + 10, jx + 40, jy + 10], fill=(200, 200, 200), width=2)
    # exam paper
    px, py = x + w - 74, y + 30
    d.rectangle([px, py, px + 56, py + 62], fill=LIGHT, outline=(120, 120, 120), width=1)
    for i in range(4):
        d.line([px + 8, py + 12 + i * 10, px + 48, py + 12 + i * 10], fill=(150, 150, 150), width=1)
    d.rectangle([px + 6, py + 48, px + 50, py + 58], fill=RED)
    d.text((px + 13, py + 49), "AI?", font=F(SANS_B, 8), fill=LIGHT)
    # taegeuk
    tx, ty = x + 16, y + h - 34
    d.ellipse([tx, ty, tx + 26, ty + 26], outline=(120, 120, 120), width=1)
    d.pieslice([tx, ty, tx + 26, ty + 26], start=90, end=270, fill=RED)
    d.pieslice([tx, ty, tx + 26, ty + 26], start=270, end=90, fill=BLUE)


def scene_soccer(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(90, 160, 90))
    d.line([x, y + h // 2, x + w, y + h // 2], fill=LIGHT, width=2)
    d.ellipse([x + w // 2 - 26, y + h // 2 - 26, x + w // 2 + 26, y + h // 2 + 26],
              outline=LIGHT, width=2)
    # goal
    d.rectangle([x + 8, y + 14, x + 44, y + 40], outline=LIGHT, width=2)
    # ball
    bx, by = x + w - 52, y + h - 40
    d.ellipse([bx - 15, by - 15, bx + 15, by + 15], fill=LIGHT, outline=(100, 100, 100), width=1)
    d.polygon([(bx, by - 7), (bx + 7, by - 2), (bx + 4, by + 6), (bx - 4, by + 6), (bx - 7, by - 2)],
              fill=INK)
    # scoreboard
    d.rectangle([x + w - 62, y + 8, x + w - 8, y + 26], fill=INK)
    d.text((x + w - 58, y + 10), "5\u20131", font=F(SANS_B, 12), fill=GOLD)


def scene_rocket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(18, 32, 64))
    for sx, sy in [(16, 14), (60, 30), (120, 10), (160, 26), (30, 50), (150, 48)]:
        d.ellipse([x + sx, y + sy, x + sx + 3, y + sy + 3], fill=LIGHT)
    cx = x + w // 2
    # flame
    d.polygon([(cx - 10, y + h - 26), (cx, y + h - 6), (cx + 10, y + h - 26)], fill=(240, 160, 40))
    d.polygon([(cx - 5, y + h - 26), (cx, y + h - 14), (cx + 5, y + h - 26)], fill=(250, 220, 80))
    # rocket body
    d.rectangle([cx - 11, y + 22, cx + 11, y + h - 26], fill=LIGHT)
    d.polygon([(cx - 11, y + 22), (cx, y + 6), (cx + 11, y + 22)], fill=RED)
    d.polygon([(cx - 11, y + h - 40), (cx - 24, y + h - 22), (cx - 11, y + h - 26)], fill=RED)
    d.polygon([(cx + 11, y + h - 40), (cx + 24, y + h - 22), (cx + 11, y + h - 26)], fill=RED)
    d.ellipse([cx - 6, y + 34, cx + 6, y + 46], fill=(120, 200, 240))
    # ground
    d.rectangle([x, y + h - 6, x + w, y + h], fill=(90, 90, 90))


def scene_shield(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 222, 200))
    cx, cy = x + w // 2, y + h // 2 - 2
    # shield
    d.polygon([(cx - 34, cy - 34), (cx + 34, cy - 34), (cx + 34, cy + 6),
               (cx, cy + 38), (cx - 34, cy + 6)], fill=(31, 95, 168))
    d.polygon([(cx - 26, cy - 26), (cx + 26, cy - 26), (cx + 26, cy + 4),
               (cx, cy + 28), (cx - 26, cy + 4)], fill=(255, 255, 255))
    d.text((cx - 13, cy - 14), "5%", font=F(SANS_B, 15), fill=NAVY)
    d.text((x + 10, y + h - 18), "SUE THE GIANTS", font=F(SANS_B, 9), fill=(120, 60, 20))


def scene_congo(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(170, 205, 150))
    gy = h - 22
    d.rectangle([x, y + gy, x + w, y + h], fill=(120, 160, 100))
    # trees
    for tx, th in [(12, 34), (150, 40), (170, 30)]:
        d.polygon([(x + tx, y + gy - th), (x + tx + 10, y + gy - th - 18),
                   (x + tx + 20, y + gy - th)], fill=(40, 110, 60))
    # tent
    tx, ty = x + 46, y + gy - 6
    d.polygon([(tx, ty - 34), (tx + 52, ty - 34), (tx + 26, ty)], fill=LIGHT)
    d.polygon([(tx + 20, ty - 34), (tx + 32, ty - 34), (tx + 26, ty)], fill=(200, 60, 50))
    # medical cross flag
    fx, fy = x + w - 52, y + 14
    d.line([fx + 12, fy, fx + 12, fy + 34], fill=(90, 90, 90), width=2)
    d.rectangle([fx + 12, fy + 2, fx + 44, fy + 20], fill=LIGHT, outline=(150, 150, 150), width=1)
    d.rectangle([fx + 24, fy + 6, fx + 30, fy + 16], fill=RED)
    d.rectangle([fx + 20, fy + 9, fx + 34, fy + 13], fill=RED)


SCENES = {"markets": scene_markets, "refinery": scene_refinery, "gaza": scene_gaza,
          "turkey": scene_turkey, "climate": scene_climate, "radar": scene_radar,
          "factory": scene_factory, "train": scene_train, "korea": scene_korea,
          "soccer": scene_soccer, "rocket": scene_rocket, "shield": scene_shield,
          "congo": scene_congo}

# ---------------------------------------------------------------- world map
# Coarse land grid, 60 cols (lon -170..190) x 26 rows (lat 75..-55), as land runs.
MAP_RUNS = [
    [(2, 12), (36, 58)], [(1, 14), (34, 59)], [(3, 16), (28, 30), (33, 59)],
    [(4, 18), (27, 28), (30, 34), (35, 58)], [(5, 19), (28, 35), (36, 57)],
    [(6, 20), (28, 36), (37, 56)], [(7, 21), (29, 34), (38, 55)],
    [(8, 22), (30, 33), (36, 54)], [(9, 23), (28, 34), (36, 40), (42, 53)],
    [(10, 20), (30, 38), (42, 46), (48, 52)], [(12, 19), (32, 36), (42, 45), (49, 52)],
    [(14, 18), (43, 45), (50, 53)], [(15, 19), (33, 36), (51, 54)],
    [(16, 20), (31, 35), (48, 53)], [(17, 21), (30, 35), (50, 55)],
    [(18, 22), (30, 34), (53, 55)], [(19, 23), (31, 33)], [(20, 24), (31, 33), (48, 52)],
    [(21, 24), (47, 53)], [(22, 24), (47, 54)], [(22, 24), (48, 53)],
    [(23, 24), (49, 52), (56, 57)], [(23, 24), (56, 57)], [(23, 24)],
    [(23, 24)], [(23, 24)],
]
MAP_PINS = [  # (col, row, color)
    (15, 7, (192, 57, 43)), (15, 15, (125, 60, 152)), (28, 5, (31, 95, 168)),
    (33, 5, (31, 95, 168)), (34, 9, (183, 121, 31)), (31, 16, (14, 124, 107)),
    (41, 9, (230, 126, 34)), (46, 16, (46, 125, 50)), (49, 8, (194, 24, 91)),
    (53, 22, (93, 64, 55)), (53, 17, (93, 64, 55)),
]


def draw_map(d, x, y, w, h):
    cw, ch = w / 60.0, h / 26.0
    for r, runs in enumerate(MAP_RUNS):
        for c0, c1 in runs:
            for c in range(c0, c1 + 1):
                cx, cy = x + c * cw + cw / 2, y + r * ch + ch / 2
                d.ellipse([cx - 1.8, cy - 1.8, cx + 1.8, cy + 1.8], fill=(120, 140, 160))
    for c, r, col in MAP_PINS:
        cx, cy = x + c * cw + cw / 2, y + r * ch + ch / 2
        d.ellipse([cx - 4.5, cy - 4.5, cx + 4.5, cy + 4.5], fill=col, outline=LIGHT, width=1)


# ---------------------------------------------------------------- layout
def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead
    d.rectangle([0, 0, W, 72], fill=NAVY)
    title = "TUESDAY 24 NOVEMBER 2026"
    tf = F(SERIF, 38)
    d.text(((W - d.textlength(title, font=tf)) / 2, 6), title, font=tf, fill=LIGHT)
    sf = F(SANS_B, 12)
    left = "ONE DAY OF WORLD NEWS, ONE PICTURE"
    right = "37 STORIES \u00b7 9 REGIONS \u00b7 11 FIELDS \u00b7 EVERY ONE FROM THIS TUESDAY"
    d.text((10, 50), left, font=sf, fill=GOLD)
    d.text((W - 10 - d.textlength(right, font=sf), 50), right, font=sf, fill=GOLD)

    # ---- UTC strip
    y = 72
    label_tab(d, 8, y + 8, "THE DAY IN UTC")
    col_w = (W - 16) / 7.0
    for i, (t, txt) in enumerate(UTC_EVENTS):
        cx = 8 + i * col_w
        d.text((cx + 6, y + 26), t, font=F(SANS_B, 13), fill=RED)
        draw_wrapped(d, cx + 6, y + 40, txt, F(SANS, 10), INK, col_w - 12, 11, max_lines=2)
    d.line([8, y + 62, W - 8, y + 62], fill=(200, 195, 180), width=1)

    # ---- numbers strip
    y = 136
    label_tab(d, 8, y + 6, "THE DAY IN NUMBERS", color=NAVY)
    col_w = (W - 16) / 6.0
    for i, (num, lab) in enumerate(NUMBERS):
        cx = 8 + i * col_w
        nf = F(SANS_B, 24)
        d.text((cx + (col_w - d.textlength(num, font=nf)) / 2, y + 26), num,
               font=nf, fill=NAVY)
        draw_wrapped(d, cx + 4, y + 52, lab, F(SANS, 10), INK, col_w - 8, 11, max_lines=1)
    d.line([8, y + 64, W - 8, y + 64], fill=(200, 195, 180), width=1)

    # ---- leads
    y = 204
    lw = int((W - 16 - 16) / 3.0)
    for i, lead in enumerate(LEADS):
        lx = 8 + i * (lw + 8)
        d.rectangle([lx, y, lx + lw, y + 24], fill=lead["color"])
        bf = F(SANS_B, 15)
        d.text((lx + (lw - d.textlength(lead["banner"], font=bf)) / 2, y + 4),
               lead["banner"], font=bf, fill=LIGHT)
        SCENES[lead["scene"]](d, lx, y + 24, lw, 116)
        hy = y + 24 + 116 + 6
        hf, hlines = fit(d, lead["head"], SERIF, 16, lw - 8, 2)
        for j, ln in enumerate(hlines):
            d.text((lx + 4, hy + j * 19), ln, font=hf, fill=INK)
        by = hy + len(hlines) * 19 + 2
        draw_wrapped(d, lx + 4, by, lead["body"], F(SANS, 11), INK, lw - 8, 13, max_lines=3)
        badge(d, lx + 4, y + 230, lead["badge"], BADGE_COLORS[lead["badge"]])
    d.line([8, y + 246, W - 8, y + 246], fill=(200, 195, 180), width=1)

    # ---- tiles: 2 rows x 5
    y = 454
    tw = int((W - 16 - 32) / 5.0)
    th = 150
    for i, tile in enumerate(TILES):
        row, col = divmod(i, 5)
        tx = 8 + col * (tw + 8)
        ty = y + row * (th + 8)
        d.rectangle([tx, ty, tx + tw, ty + 20], fill=tile["color"])
        bf = F(SANS_B, 12)
        d.text((tx + (tw - d.textlength(tile["num"], font=bf)) / 2, ty + 3),
               tile["num"], font=bf, fill=LIGHT)
        SCENES[tile["scene"]](d, tx, ty + 20, tw, 60)
        hy = ty + 20 + 62 + 4
        hf, hlines = fit(d, tile["head"], SANS_B, 11, tw - 8, 2)
        for j, ln in enumerate(hlines):
            d.text((tx + 4, hy + j * 13), ln, font=hf, fill=INK)
        by = hy + len(hlines) * 13 + 2
        draw_wrapped(d, tx + 4, by, tile["body"], F(SANS, 10), INK, tw - 8, 11, max_lines=2)
        badge(d, tx + 4, ty + th - 14, tile["badge"], BADGE_COLORS[tile["badge"]], size=8)
    d.line([8, y + 2 * th + 8, W - 8, y + 2 * th + 8], fill=(200, 195, 180), width=1)

    # ---- bottom band: map + index
    y = 766
    d.text((8, y), "WHERE IT HAPPENED", font=F(SANS_B, 11), fill=NAVY)
    d.text((346, y), "THE REST OF THE DAY \u2014 IN BRIEF", font=F(SANS_B, 11), fill=NAVY)
    draw_map(d, 8, y + 18, 328, 130)
    # date check box under the map
    dy = y + 156
    d.rectangle([8, dy, 336, 1014], outline=RED, width=2)
    d.rectangle([8, dy, 336, dy + 20], fill=RED)
    d.text((14, dy + 4), "DATE CHECK", font=F(SANS_B, 11), fill=LIGHT)
    draw_wrapped(d, 14, dy + 26,
                 "NOT THIS DAY: COP31 collapse (22 Nov) \u00b7 Merkury sunk (23 Nov) \u00b7 "
                 "Grok suits filed (23 Nov) \u00b7 Nvidia CEO back (23 Nov) \u00b7 Monday's "
                 "record rally (23 Nov).",
                 F(SANS, 9), INK, 316, 12, max_lines=4)
    draw_wrapped(d, 14, dy + 52,
                 "NOT YET: US Thanksgiving (27 Nov) \u00b7 PCE + GDP data (25 Nov) \u00b7 "
                 "Hasina's return (16 Dec) \u00b7 COP32 in Addis Ababa (2027).",
                 F(SANS, 9), INK, 316, 12, max_lines=3)

    # index: 3 cols x 8 rows
    col_w = (1016 - 346) / 3.0
    for i, (tag, head, fact, region, badge_name) in enumerate(INDEX):
        col, row = divmod(i, 8)
        ix = 346 + col * col_w
        iy = y + 18 + row * 28
        d.ellipse([ix, iy + 3, ix + 7, iy + 10], fill=REGION_COLORS[region])
        draw_wrapped(d, ix + 11, iy, tag + ": " + head, F(SANS_B, 10), INK,
                     col_w - 12, 11, max_lines=1)
        draw_wrapped(d, ix + 11, iy + 13, fact, F(SANS, 9), GREY, col_w - 12, 11,
                     max_lines=1)

    # ---- footer
    d.text((8, 1016), "Every story verified against at least two independent outlets dated "
                      "24 November 2026. Sources: AP \u00b7 Reuters \u00b7 BBC \u00b7 CNN \u00b7 "
                      "Investopedia \u00b7 Just Security \u00b7 Kyiv Independent.",
           font=F(SANS, 8), fill=GREY)
    img.save(OUT, optimize=True)
    return OUT


if __name__ == "__main__":
    path = render()
    import hashlib
    data = open(path, "rb").read()
    im = Image.open(path)
    print(path, len(data), "bytes,", im.size, "sha256",
          hashlib.sha256(data).hexdigest()[:16])
