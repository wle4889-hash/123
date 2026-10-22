"""Generate a 9:16 (1080x1920) SVG illustration: a person relaxing on a grassland.

Usage: python3 src/scene.py out/scene.html
"""
import math
import random
import sys

W, H = 1080, 1920
HORIZON = 1085
GROUND = 1500  # where the person lies
rng = random.Random(20261022)


def lerp(a, b, t):
    return a + (b - a) * t


def mix(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(round(lerp(x, y, t)) for x, y in zip(a, b))


def blade(x, y, h, w, lean, color, opacity=1.0):
    tx, ty = x + lean, y - h
    return (
        f'<path d="M{x - w / 2:.1f},{y:.1f} Q{x - w / 4 + lean * 0.35:.1f},{y - h * 0.55:.1f} {tx:.1f},{ty:.1f} '
        f'Q{x + w / 4 + lean * 0.35:.1f},{y - h * 0.55:.1f} {x + w / 2:.1f},{y:.1f}Z" '
        f'fill="{color}"' + (f' opacity="{opacity:.2f}"' if opacity < 1 else "") + "/>"
    )


def ridge(y_base, amp, rough, n, seed_shift, color, opacity=1.0, extra=""):
    pts = [rng.uniform(-1, 1) for _ in range(n + 1)]
    # midpoint-ish smoothing
    for _ in range(2):
        pts = [pts[0]] + [(pts[i - 1] + 2 * pts[i] + pts[i + 1]) / 4 for i in range(1, n)] + [pts[-1]]
    d = f"M0,{H}"
    for i, p in enumerate(pts):
        x = W * i / n
        y = y_base - amp * (0.5 + 0.5 * math.sin(i * 0.9 + seed_shift)) - rough * p
        d += f" L{x:.1f},{y:.1f}"
    d += f" L{W},{H} Z"
    return f'<path d="{d}" fill="{color}" opacity="{opacity}" {extra}/>'


def cloud(cx, cy, s, opacity=0.95):
    puffs = []
    n = rng.randint(6, 9)
    for i in range(n):
        t = i / (n - 1)
        x = cx + lerp(-170, 170, t) * s + rng.uniform(-15, 15) * s
        r = (60 + 55 * math.sin(math.pi * t) + rng.uniform(-10, 15)) * s
        y = cy - (r * 0.35) + rng.uniform(-8, 8) * s
        puffs.append((x, y, r))
    base = f'<ellipse cx="{cx:.1f}" cy="{cy + 6 * s:.1f}" rx="{190 * s:.1f}" ry="{34 * s:.1f}" fill="#efd9cf"/>'
    shade = "".join(f'<circle cx="{x:.1f}" cy="{y + 10 * s:.1f}" r="{r * 0.9:.1f}" fill="#f1dcd2"/>' for x, y, r in puffs)
    light = "".join(f'<circle cx="{x - 4 * s:.1f}" cy="{y - 8 * s:.1f}" r="{r * 0.96:.1f}" fill="#fffcf7"/>' for x, y, r in puffs)
    return f'<g filter="url(#soft)" opacity="{opacity}">{base}{shade}{light}</g>'


def daisy(x, y, r, petals=8, color="#ffffff", center="#f4b81c", rot=0.0, squash=0.55):
    out = [f'<g transform="translate({x:.1f},{y:.1f}) scale(1,{squash:.2f})">']
    for i in range(petals):
        a = rot + 360 * i / petals
        out.append(
            f'<ellipse cx="{r * 0.55:.1f}" cy="0" rx="{r * 0.55:.1f}" ry="{r * 0.2:.1f}" fill="{color}" '
            f'transform="rotate({a:.1f})"/>'
        )
    out.append(f'<circle r="{r * 0.28:.1f}" fill="{center}"/></g>')
    return "".join(out)


def stem_flower(x, y, h, r, kind):
    s = f'<path d="M{x:.1f},{y:.1f} q{rng.uniform(-6, 6):.1f},{-h / 2:.1f} {rng.uniform(-8, 8):.1f},{-h:.1f}" stroke="#4f8a2c" stroke-width="{max(1.2, r * 0.12):.1f}" fill="none"/>'
    fx = x + 0
    fy = y - h
    if kind == "daisy":
        return s + daisy(fx, fy, r, petals=rng.choice([8, 9, 10]), rot=rng.uniform(0, 40), squash=rng.uniform(0.45, 0.8))
    if kind == "yellow":
        return s + daisy(fx, fy, r * 0.8, petals=5, color="#ffd23f", center="#e8901a", rot=rng.uniform(0, 70), squash=0.7)
    # purple cluster (lavender-like)
    dots = "".join(
        f'<ellipse cx="{fx + rng.uniform(-r * 0.25, r * 0.25):.1f}" cy="{fy - k * r * 0.28:.1f}" rx="{r * 0.22:.1f}" ry="{r * 0.18:.1f}" fill="{rng.choice(["#9b6fd1", "#b08be0", "#7d55b8"])}"/>'
        for k in range(6)
    )
    return s + dots


parts = []
add = parts.append

# ---------------------------------------------------------------- defs
add(f"""
<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#2f6fc4"/>
    <stop offset="0.28" stop-color="#5a9be0"/>
    <stop offset="0.48" stop-color="#9cc9ef"/>
    <stop offset="0.53" stop-color="#d8e4e6"/>
    <stop offset="0.58" stop-color="#ffe2b8"/>
    <stop offset="0.62" stop-color="#ffd59a"/>
  </linearGradient>
  <radialGradient id="sunGlow" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="#fffef6" stop-opacity="1"/>
    <stop offset="0.07" stop-color="#fff6d8" stop-opacity="1"/>
    <stop offset="0.16" stop-color="#ffe6a8" stop-opacity="0.75"/>
    <stop offset="0.4" stop-color="#ffd08a" stop-opacity="0.28"/>
    <stop offset="1" stop-color="#ffc47a" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="meadow" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#b9cf6a"/>
    <stop offset="0.18" stop-color="#93bd4c"/>
    <stop offset="0.5" stop-color="#5f9a32"/>
    <stop offset="1" stop-color="#2c5e1b"/>
  </linearGradient>
  <linearGradient id="haze" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ffe6c2" stop-opacity="0"/>
    <stop offset="0.6" stop-color="#ffe6c2" stop-opacity="0.55"/>
    <stop offset="1" stop-color="#ffe6c2" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="shirt" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fffaf0"/>
    <stop offset="1" stop-color="#d9d3c6"/>
  </linearGradient>
  <linearGradient id="jeans" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#5b7fb0"/>
    <stop offset="1" stop-color="#34507a"/>
  </linearGradient>
  <linearGradient id="skin" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#f6d0ad"/>
    <stop offset="1" stop-color="#dba57f"/>
  </linearGradient>
  <radialGradient id="vignette" cx="0.5" cy="0.48" r="0.75">
    <stop offset="0.66" stop-color="#000" stop-opacity="0"/>
    <stop offset="1" stop-color="#1a1206" stop-opacity="0.4"/>
  </radialGradient>
  <radialGradient id="warm" cx="0.74" cy="0.36" r="0.9">
    <stop offset="0" stop-color="#ffd9a0" stop-opacity="0.38"/>
    <stop offset="0.5" stop-color="#ffcf90" stop-opacity="0.12"/>
    <stop offset="1" stop-color="#ffcf90" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="flare" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="#fff2cf" stop-opacity="0.35"/>
    <stop offset="0.7" stop-color="#ffd59a" stop-opacity="0.12"/>
    <stop offset="1" stop-color="#ffd59a" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="shadow" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="#1f3d10" stop-opacity="0.55"/>
    <stop offset="1" stop-color="#1f3d10" stop-opacity="0"/>
  </radialGradient>
  <pattern id="plaid" width="56" height="56" patternUnits="userSpaceOnUse">
    <rect width="56" height="56" fill="#c8453a"/>
    <rect width="56" height="18" y="19" fill="#e8d9bf" opacity="0.55"/>
    <rect width="18" height="56" x="19" fill="#e8d9bf" opacity="0.55"/>
    <rect width="56" height="4" y="26" fill="#7a221c" opacity="0.6"/>
    <rect width="4" height="56" x="26" fill="#7a221c" opacity="0.6"/>
  </pattern>
  <filter id="soft" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="7"/></filter>
  <filter id="blur2" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="2"/></filter>
  <filter id="blur1"><feGaussianBlur stdDeviation="0.8"/></filter>
  <filter id="dof" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="7"/></filter>
  <filter id="dof2" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="3"/></filter>
  <filter id="rays" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="22"/></filter>
  <filter id="grain" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7" result="n"/>
    <feColorMatrix type="saturate" values="0"/>
    <feComponentTransfer><feFuncA type="table" tableValues="0 0.09"/></feComponentTransfer>
  </filter>
</defs>
""")

# ---------------------------------------------------------------- sky
add(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')
SUN = (790, 760)
add(f'<circle cx="{SUN[0]}" cy="{SUN[1]}" r="950" fill="url(#sunGlow)"/>')

# god rays
rays = []
for i in range(9):
    a = math.radians(rng.uniform(105, 175))
    spread = math.radians(rng.uniform(2, 5))
    L = 1600
    x1, y1 = SUN[0] + L * math.cos(a - spread), SUN[1] + L * math.sin(a - spread)
    x2, y2 = SUN[0] + L * math.cos(a + spread), SUN[1] + L * math.sin(a + spread)
    rays.append(f'<path d="M{SUN[0]},{SUN[1]} L{x1:.0f},{y1:.0f} L{x2:.0f},{y2:.0f}Z" fill="#fff3d6" opacity="{rng.uniform(0.04, 0.08):.2f}"/>')
add(f'<g filter="url(#rays)">{"".join(rays)}</g>')

# clouds
for cx, cy, s, o in [(230, 330, 1.05, 0.95), (720, 210, 0.75, 0.85), (930, 520, 0.6, 0.8),
                     (130, 690, 0.55, 0.75), (520, 600, 0.45, 0.7), (380, 900, 0.5, 0.55), (980, 940, 0.42, 0.5)]:
    add(cloud(cx, cy, s, o))

# birds
for bx, by, bs in [(560, 440, 1.0), (610, 470, 0.8), (520, 490, 0.7), (660, 420, 0.6)]:
    add(f'<path d="M{bx - 14 * bs:.1f},{by:.1f} q{7 * bs:.1f},{-8 * bs:.1f} {14 * bs:.1f},0 q{7 * bs:.1f},{-8 * bs:.1f} {14 * bs:.1f},0" '
        f'stroke="#3a3f4a" stroke-width="{2.4 * bs:.1f}" fill="none" stroke-linecap="round" opacity="0.7"/>')

# ---------------------------------------------------------------- land: mountains & hills
add(ridge(HORIZON - 30, 70, 45, 26, 0.3, "#9fb5cf", 0.85, 'filter="url(#blur1)"'))
add(ridge(HORIZON + 5, 45, 30, 32, 2.1, "#87a2b8", 0.9, 'filter="url(#blur1)"'))
add(f'<rect x="0" y="{HORIZON - 160}" width="{W}" height="260" fill="url(#haze)"/>')


def hill(y0, amp, freq, phase, color):
    d = f"M0,{H} L0,{y0:.1f}"
    for i in range(0, W + 21, 20):
        y = y0 - amp * math.sin(i / W * math.pi * freq + phase) - amp * 0.35 * math.sin(i / W * math.pi * freq * 2.3 + phase * 1.7)
        d += f" L{i},{y:.1f}"
    d += f" L{W},{H}Z"
    return f'<path d="{d}" fill="{color}"/>'


add(hill(HORIZON + 20, 22, 2.2, 0.6, "#a7c48b"))
add(hill(HORIZON + 48, 26, 1.6, 2.4, "#94bb6a"))

# lone tree on the far hill
tx, ty = 880, HORIZON + 20
add(f'<g opacity="0.85"><rect x="{tx - 3}" y="{ty - 38}" width="6" height="40" fill="#4a3a28"/>'
    + "".join(f'<circle cx="{tx + dx}" cy="{ty - 46 + dy}" r="{r}" fill="#466f33"/>' for dx, dy, r in
              [(-14, 4, 16), (12, 4, 16), (0, -8, 20), (-6, 8, 14), (8, 10, 14)])
    + "</g>")

add(hill(HORIZON + 80, 18, 1.1, 1.0, "url(#meadow)"))

# distant meadow texture (perspective: tiny far away, bigger near)
far = []
y_top = HORIZON + 80
for _ in range(5200):
    y = y_top + (GROUND + 120 - y_top) * (rng.random() ** 1.35)
    t = (y - y_top) / (GROUND + 120 - y_top)
    x = rng.uniform(-10, W + 10)
    h = lerp(3, 34, t) * rng.uniform(0.6, 1.3)
    w = lerp(1.2, 5, t)
    col = mix(rng.choice(["#c9dc7a", "#a8cc5a", "#7fb043", "#93c255", "#d8d47a"]), "#3f7a25", t * 0.55)
    far.append(blade(x, y, h, w, rng.uniform(-0.5, 0.5) * h, col, 0.9))
add("".join(far))

# little far flowers
specks = []
for _ in range(420):
    y = y_top + 20 + (GROUND + 60 - y_top) * (rng.random() ** 1.1)
    t = (y - y_top) / (GROUND + 60 - y_top)
    x = rng.uniform(0, W)
    r = lerp(1.2, 4.5, t)
    c = rng.choice(["#ffffff", "#fff3a8", "#ffd23f", "#c7a7ee", "#ffffff"])
    specks.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r:.1f}" ry="{r * 0.7:.1f}" fill="{c}" opacity="0.92"/>')
add("".join(specks))

# ---------------------------------------------------------------- picnic blanket & person
PX, PY = 150, GROUND  # person local origin

add(f'<ellipse cx="{PX + 440}" cy="{PY + 6}" rx="430" ry="34" fill="url(#shadow)"/>')
add(f'<path d="M{PX + 10},{PY - 30} L{PX + 860},{PY - 34} L{PX + 900},{PY + 38} L{PX - 40},{PY + 42}Z" '
    f'fill="url(#plaid)" transform="" opacity="0.97"/>')
add(f'<path d="M{PX - 40},{PY + 42} L{PX + 900},{PY + 38} L{PX + 900},{PY + 46} L{PX - 40},{PY + 50}Z" fill="#8f2a22"/>')

add(f'<ellipse cx="{PX + 420}" cy="{PY - 2}" rx="360" ry="16" fill="#3a0f0a" opacity="0.28" filter="url(#dof2)"/>')

person = f"""
<g transform="translate({PX},{PY})">
  <!-- far arm (behind head) -->
  <path d="M215,-58 L158,-150 L102,-70" stroke="#d29b74" stroke-width="22" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M215,-58 L170,-128" stroke="#cfc8b9" stroke-width="30" stroke-linecap="round"/>

  <!-- far leg (straight) -->
  <path d="M470,-30 L735,-24" stroke="#2f4a72" stroke-width="44" stroke-linecap="round"/>
  <path d="M738,-6 C736,-40 744,-62 760,-66 C776,-68 782,-52 778,-30 L772,-4 Z" fill="#efe9de"/>
  <path d="M738,-6 L772,-4 L774,4 L736,2 Z" fill="#b8ab98"/>

  <!-- near forearm (goes behind head) -->
  <path d="M168,-160 L96,-78" stroke="url(#skin)" stroke-width="22" stroke-linecap="round"/>

  <!-- hair back + head -->
  <path d="M92,-36 C70,-60 72,-104 102,-118 C120,-126 140,-122 150,-112 L132,-60 L150,-22 C130,-6 104,-14 92,-36Z" fill="#3a271c"/>
  <path d="M120,-100 C132,-120 168,-126 186,-108 C196,-104 202,-112 208,-106 C206,-98 202,-94 200,-90
           C210,-86 214,-80 210,-76 C214,-70 212,-64 206,-62 C210,-54 204,-44 196,-40
           C180,-26 150,-20 132,-34 C116,-48 112,-80 120,-100Z" fill="url(#skin)"/>
  <!-- hair top / fringe -->
  <path d="M112,-96 C116,-120 146,-132 172,-122 C160,-116 150,-108 146,-98 C138,-104 126,-104 112,-96Z" fill="#3a271c"/>
  <!-- ear -->
  <ellipse cx="142" cy="-62" rx="11" ry="14" fill="#e3ad86"/>
  <path d="M138,-66 q6,4 2,10" stroke="#c98d68" stroke-width="2" fill="none"/>
  <!-- closed eye & smile -->
  <path d="M176,-98 q8,6 16,0" stroke="#3a271c" stroke-width="2.6" fill="none" stroke-linecap="round"/>
  <path d="M176,-100 l-3,-4 M182,-98 l-1,-5 M188,-98 l1,-5" stroke="#3a271c" stroke-width="1.4" stroke-linecap="round"/>
  <path d="M194,-62 q6,2 10,-4" stroke="#a65a44" stroke-width="2.4" fill="none" stroke-linecap="round"/>
  <ellipse cx="184" cy="-74" rx="9" ry="6" fill="#f2a08a" opacity="0.35"/>

  <!-- neck -->
  <path d="M188,-44 C196,-40 206,-44 214,-48 L222,-10 L186,-10Z" fill="#d8a07a"/>

  <!-- torso / shirt -->
  <path d="M205,-62 C236,-84 300,-94 350,-84 C390,-76 440,-80 476,-70 L486,-6 C430,0 300,2 214,-2 C196,-4 188,-20 196,-40 Z" fill="url(#shirt)"/>
  <path d="M232,-30 C300,-26 380,-28 470,-36" stroke="#cfc6b6" stroke-width="2" fill="none" opacity="0.8"/>
  <path d="M300,-76 C320,-60 360,-56 400,-62" stroke="#d6cfc0" stroke-width="2" fill="none" opacity="0.7"/>
  <!-- collar -->
  <path d="M205,-62 C214,-56 222,-50 228,-44 L214,-38 C206,-44 200,-52 205,-62Z" fill="#e9e3d6"/>

  <!-- belt + hips -->
  <path d="M470,-70 C500,-72 530,-64 548,-50 L552,-6 L480,-4 Z" fill="url(#jeans)"/>
  <rect x="468" y="-72" width="12" height="68" rx="3" fill="#5a3a22"/>

  <!-- near leg (bent knee) -->
  <path d="M520,-40 L620,-158" stroke="url(#jeans)" stroke-width="54" stroke-linecap="round"/>
  <path d="M620,-158 L684,-30" stroke="#4a6c9c" stroke-width="44" stroke-linecap="round"/>
  <path d="M606,-176 q22,-4 34,14" stroke="#7f9fca" stroke-width="5" fill="none" stroke-linecap="round" opacity="0.8"/>
  <!-- shoe -->
  <path d="M664,-30 C664,-46 684,-50 700,-44 C720,-38 744,-28 750,-16 C752,-8 746,-2 736,-2 L668,-2 C662,-10 662,-20 664,-30Z" fill="#f4efe6"/>
  <path d="M664,-6 L748,-6 L748,0 L664,0Z" fill="#b8ab98"/>
  <path d="M684,-44 l8,10 M696,-42 l6,10" stroke="#c9bfae" stroke-width="2.5"/>

  <!-- near upper arm (sleeve) over shoulder -->
  <path d="M240,-58 L176,-150" stroke="url(#skin)" stroke-width="24" stroke-linecap="round"/>
  <path d="M248,-54 L206,-112" stroke="#f6f1e6" stroke-width="34" stroke-linecap="round"/>
  <path d="M232,-90 L196,-112" stroke="#ddd6c8" stroke-width="2" opacity="0.8"/>

  <!-- rim light from the sun (upper right) -->
  <path d="M290,-90 C330,-92 360,-80 400,-78 C430,-77 455,-76 470,-72" stroke="#fff6dc" stroke-width="3" fill="none" opacity="0.8"/>
  <path d="M528,-68 L612,-172" stroke="#c9d8ef" stroke-width="3" fill="none" opacity="0.55" stroke-linecap="round"/>
</g>
"""
add(person)

# straw hat resting on the blanket near the head
hx, hy = PX - 20, PY - 4
add(f"""
<g transform="translate({hx},{hy}) rotate(-8)">
  <ellipse cx="0" cy="0" rx="70" ry="20" fill="#d9b46a"/>
  <ellipse cx="0" cy="-4" rx="66" ry="16" fill="#e8c983"/>
  <path d="M-36,-6 C-36,-44 36,-44 36,-6 Z" fill="#e2c07a"/>
  <path d="M-36,-10 C-20,-4 20,-4 36,-10 L36,-18 C20,-12 -20,-12 -36,-18Z" fill="#6b3b2a"/>
  <path d="M-30,-26 C-10,-34 14,-34 30,-26" stroke="#c9a15a" stroke-width="2" fill="none"/>
</g>
""")

# a small open book beside the hip
bx, by = PX + 800, PY + 14
add(f"""
<g transform="translate({bx},{by}) rotate(4)">
  <path d="M-46,0 L0,-8 L46,0 L46,6 L0,0 L-46,6Z" fill="#2f4d6e"/>
  <path d="M-44,-2 C-30,-10 -12,-12 0,-8 C12,-12 30,-10 44,-2 L0,-4Z" fill="#fbf7ec"/>
  <path d="M0,-8 L0,-3" stroke="#c9c0ac" stroke-width="1.5"/>
</g>
""")

# butterflies
for (x, y, s, c) in [(760, 1330, 1.0, "#ff9f1c"), (840, 1260, 0.7, "#ffffff")]:
    add(f'<g transform="translate({x},{y}) scale({s}) rotate(-12)">'
        f'<path d="M0,0 C-18,-26 -34,-10 -24,4 C-34,14 -16,24 0,4Z" fill="{c}" stroke="#4a2c12" stroke-width="1.2"/>'
        f'<path d="M0,0 C14,-22 28,-10 20,2 C28,10 14,20 0,4Z" fill="{c}" opacity="0.85" stroke="#4a2c12" stroke-width="1.2"/>'
        f'<path d="M0,-4 L1,10" stroke="#2b1a0b" stroke-width="2.5" stroke-linecap="round"/>'
        f'<path d="M0,-4 q-4,-10 -8,-12 M0,-4 q2,-10 6,-12" stroke="#2b1a0b" stroke-width="1" fill="none"/></g>')

# ---------------------------------------------------------------- near grass (overlapping the scene)
near = []
for _ in range(1400):
    y = rng.uniform(GROUND - 10, GROUND + 140)
    t = (y - (GROUND - 10)) / 150
    x = rng.uniform(-10, W + 10)
    h = lerp(18, 60, t) * rng.uniform(0.6, 1.4)
    w = lerp(4, 7, t)
    col = mix(rng.choice(["#9cc95a", "#7db343", "#b6d66a", "#6aa33a", "#cfdc7c"]), "#2f6a1f", t * 0.45)
    near.append(blade(x, y, h, w, rng.uniform(-0.45, 0.45) * h, col))
# taller tufts that poke in front of the blanket edge / person
for _ in range(260):
    x = rng.uniform(80, 1000)
    y = GROUND + rng.uniform(30, 60)
    h = rng.uniform(30, 85)
    col = rng.choice(["#8ec04f", "#a9d05e", "#6fa83d", "#c3dc72"])
    near.append(blade(x, y, h, rng.uniform(3, 6), rng.uniform(-0.5, 0.5) * h, col))
add("".join(near))

fl = []
for _ in range(70):
    y = rng.uniform(GROUND + 40, GROUND + 260)
    t = (y - GROUND) / 260
    x = rng.uniform(10, W - 10)
    fl.append(stem_flower(x, y, lerp(20, 55, t) * rng.uniform(0.7, 1.2), lerp(7, 14, t),
                          rng.choices(["daisy", "yellow", "purple"], [5, 3, 2])[0]))
add("".join(fl))

# foreground grass, lower frame
fg = []
for _ in range(1700):
    y = rng.uniform(GROUND + 120, H + 40)
    t = (y - GROUND - 120) / (H + 40 - GROUND - 120)
    x = rng.uniform(-20, W + 20)
    h = lerp(60, 200, t) * rng.uniform(0.6, 1.3)
    w = lerp(6, 14, t)
    col = mix(rng.choice(["#6faa3a", "#5c9a30", "#88bd4a", "#4d8a2a", "#a5c95a"]), "#183f10", t * 0.6)
    fg.append(blade(x, y, h, w, rng.uniform(-0.5, 0.5) * h, col))
add("".join(fg))

fl2 = []
for _ in range(34):
    y = rng.uniform(GROUND + 260, H - 120)
    t = (y - GROUND - 260) / (H - 380 - GROUND)
    x = rng.uniform(20, W - 20)
    fl2.append(stem_flower(x, y, lerp(50, 110, t), lerp(14, 26, t), rng.choices(["daisy", "yellow", "purple"], [5, 3, 2])[0]))
add("".join(fl2))

# out-of-focus giant blades at the very bottom (depth of field)
dof = []
for _ in range(60):
    x = rng.uniform(-40, W + 40)
    y = H + 40
    h = rng.uniform(260, 520)
    dof.append(blade(x, y, h, rng.uniform(16, 30), rng.uniform(-0.45, 0.45) * h,
                     rng.choice(["#2f6a1d", "#3c7a24", "#24561a", "#4a8a2a"])))
add(f'<g filter="url(#dof)">{"".join(dof)}</g>')
dofl = "".join(daisy(x, y, r, rot=rng.uniform(0, 40), squash=0.6) for x, y, r in [(120, 1740, 44), (930, 1810, 52)])
add(f'<g filter="url(#dof2)" opacity="0.95">{dofl}</g>')

# ---------------------------------------------------------------- light & finishing
add(f'<rect width="{W}" height="{H}" fill="url(#warm)" style="mix-blend-mode:screen"/>')
for (t, r, o) in [(0.35, 60, 0.5), (0.55, 26, 0.6), (0.8, 90, 0.35), (1.05, 40, 0.5)]:
    fx = lerp(SUN[0], 300, t)
    fy = lerp(SUN[1], 1500, t)
    add(f'<circle cx="{fx:.0f}" cy="{fy:.0f}" r="{r}" fill="url(#flare)" opacity="{o}" style="mix-blend-mode:screen"/>')
add(f'<rect width="{W}" height="{H}" fill="url(#vignette)"/>')
add(f'<rect width="{W}" height="{H}" filter="url(#grain)" style="mix-blend-mode:overlay"/>')

svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{"".join(parts)}</svg>'
html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Grassland Relax</title>
<style>html,body{{margin:0;padding:0;background:#000}}svg{{display:block}}</style></head><body>{svg}</body></html>"""

out = sys.argv[1] if len(sys.argv) > 1 else "scene.html"
with open(out, "w") as f:
    f.write(html)
print("wrote", out, len(html) // 1024, "KB")
