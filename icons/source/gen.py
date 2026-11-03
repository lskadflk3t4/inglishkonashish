#!/usr/bin/env python3
"""Инглишко на шиш — app icon.
Clay-style scene: a cheerful suckling pig on a spit over fire, a glass of rakia
and a bowl of shopska salad, against a Union Jack backdrop.
Rendered from hand-built SVG so every form stays crisp at any size."""
import colorsys, os

S = 512  # design canvas


# ---------- colour helpers: clay shading is one hue, three values ----------
def hx(c):
    c = c.lstrip('#')
    return tuple(int(c[i:i + 2], 16) / 255 for i in (0, 2, 4))


def to_hex(r, g, b):
    return '#%02X%02X%02X' % tuple(max(0, min(255, round(v * 255))) for v in (r, g, b))


def shift(c, dl=0.0, ds=0.0, dh=0.0):
    h, l, s = colorsys.rgb_to_hls(*hx(c))
    h = (h + dh) % 1.0
    return to_hex(*colorsys.hls_to_rgb(h, max(0, min(1, l + dl)), max(0, min(1, s + ds))))


GRADS = {}


def clay(name, base, lift=.16, drop=.17, warm=.012):
    """A matte clay gradient: lit from the upper left, shadow drifting warm."""
    GRADS[name] = (shift(base, lift, .03, -warm), base, shift(base, -drop, .02, warm))
    return f'url(#{name})'


# ---------- palette ----------
C_NAVY, C_RED, C_WHITE = '#2E4475', '#C8453D', '#F2EADC'
C_PORK, C_CRACK = '#D99356', '#C0703C'      # roasted body, crisped edges
C_SNOUT, C_EAR = '#E7A98A', '#C9814E'
C_FLAME, C_EMBER, C_CORE = '#EE7B32', '#D8502A', '#F9CE55'
C_ROD = '#9AA3AE'
C_GLASS, C_RAKIA = '#E9E2D4', '#E0A94E'
C_BOWL, C_TOM, C_CUC, C_SIR = '#EFE6D7', '#CC4036', '#7CA757', '#FBF6EC'
C_WOOD = '#8A6243'


def svg(scene_scale=1.0, bleed=True):
    """scene_scale < 1 pulls the scene into the maskable safe zone; the flag always bleeds."""
    d, b = [], []

    # ----- defs -----
    for n, c in (('navy', C_NAVY), ('red', C_RED), ('white', C_WHITE), ('pork', C_PORK),
                 ('crack', C_CRACK), ('snout', C_SNOUT), ('ear', C_EAR), ('flame', C_FLAME),
                 ('ember', C_EMBER), ('core', C_CORE), ('rod', C_ROD), ('glass', C_GLASS),
                 ('rakia', C_RAKIA), ('bowl', C_BOWL), ('tom', C_TOM), ('cuc', C_CUC),
                 ('sir', C_SIR), ('wood', C_WOOD)):
        clay(n, c)
    for n, (lo, mid, hi) in GRADS.items():
        d.append(f'<radialGradient id="{n}" cx="34%" cy="26%" r="82%">'
                 f'<stop offset="0" stop-color="{lo}"/><stop offset=".55" stop-color="{mid}"/>'
                 f'<stop offset="1" stop-color="{hi}"/></radialGradient>')
    d.append('<filter id="sh" x="-30%" y="-30%" width="170%" height="180%">'
             '<feDropShadow dx="0" dy="7" stdDeviation="7" flood-color="#2A1A10" flood-opacity=".34"/></filter>')
    d.append('<filter id="shs" x="-40%" y="-40%" width="190%" height="200%">'
             '<feDropShadow dx="0" dy="4" stdDeviation="4" flood-color="#2A1A10" flood-opacity=".30"/></filter>')
    d.append('<filter id="soft" x="-60%" y="-60%" width="220%" height="220%">'
             '<feGaussianBlur stdDeviation="16"/></filter>')
    d.append('<filter id="soft2" x="-60%" y="-60%" width="220%" height="220%">'
             '<feGaussianBlur stdDeviation="7"/></filter>')
    # the flag is cloth, not plastic: a gentle centre light and darker corners
    d.append('<radialGradient id="vig" cx="42%" cy="34%" r="78%">'
             '<stop offset="0" stop-color="#FFFFFF" stop-opacity=".17"/>'
             '<stop offset=".58" stop-color="#FFFFFF" stop-opacity="0"/>'
             '<stop offset="1" stop-color="#15192E" stop-opacity=".40"/></radialGradient>')
    d.append('<linearGradient id="glassSheen" x1="0" y1="0" x2="1" y2="1">'
             '<stop offset="0" stop-color="#FFFFFF" stop-opacity=".85"/>'
             '<stop offset=".5" stop-color="#FFFFFF" stop-opacity=".12"/>'
             '<stop offset="1" stop-color="#FFFFFF" stop-opacity=".45"/></linearGradient>')

    # ----- Union Jack backdrop -----
    b.append(f'<rect width="{S}" height="{S}" fill="url(#navy)"/>')
    b.append(f'<g stroke-linecap="square"><path d="M0 0 L{S} {S} M{S} 0 L0 {S}" '
             f'stroke="url(#white)" stroke-width="104" fill="none"/>'
             f'<path d="M0 0 L{S} {S} M{S} 0 L0 {S}" stroke="url(#red)" stroke-width="42" fill="none"/></g>')
    b.append(f'<path d="M256 0 V{S} M0 256 H{S}" stroke="url(#white)" stroke-width="124" fill="none"/>')
    b.append(f'<path d="M256 0 V{S} M0 256 H{S}" stroke="url(#red)" stroke-width="64" fill="none"/>')
    b.append(f'<rect width="{S}" height="{S}" fill="url(#vig)"/>')

    # ----- scene -----
    s = []
    # warm glow of the fire washing over the flag
    s.append('<ellipse cx="256" cy="372" rx="190" ry="120" fill="#FF9A3C" opacity=".40" filter="url(#soft)"/>')
    # ground shadow
    s.append('<ellipse cx="256" cy="452" rx="196" ry="30" fill="#1B1020" opacity=".30" filter="url(#soft2)"/>')

    # spit supports: two crossed sticks at each end
    for cx in (72, 440):
        s.append(f'<g filter="url(#shs)" stroke="url(#wood)" stroke-width="17" stroke-linecap="round">'
                 f'<path d="M{cx-30} 455 L{cx+26} 252"/><path d="M{cx+30} 455 L{cx-26} 252"/></g>')

    # the spit rod — passes below the head, through the body
    s.append('<rect x="14" y="265" width="484" height="15" rx="7.5" fill="url(#rod)" filter="url(#shs)"/>')
    s.append('<circle cx="22" cy="272" r="12" fill="url(#rod)"/>')
    s.append('<path d="M498 272 l-22 -13 v26 z" fill="url(#rod)"/>')  # pointed tip

    # fire, behind the pig
    flames = [(196, 404, 30, 62), (256, 396, 38, 76), (318, 406, 29, 60),
              (226, 414, 24, 48), (288, 414, 24, 48)]
    for cx, cy, rx, ry in flames:
        s.append(f'<path d="M{cx} {cy-ry} C{cx+rx} {cy-ry*.35} {cx+rx} {cy+ry*.5} {cx} {cy+ry*.55} '
                 f'C{cx-rx} {cy+ry*.5} {cx-rx} {cy-ry*.35} {cx} {cy-ry} Z" fill="url(#flame)"/>')
    for cx, cy, rx, ry in flames[:3]:
        s.append(f'<path d="M{cx} {cy-ry*.55} C{cx+rx*.52} {cy-ry*.1} {cx+rx*.52} {cy+ry*.42} {cx} {cy+ry*.45} '
                 f'C{cx-rx*.52} {cy+ry*.42} {cx-rx*.52} {cy-ry*.1} {cx} {cy-ry*.55} Z" fill="url(#core)"/>')
    # glowing coals
    for cx, cy, rx in ((206, 444, 26), (248, 450, 30), (296, 445, 27), (334, 450, 21), (176, 450, 18)):
        s.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{rx*.52:.0f}" fill="url(#ember)"/>')

    # ----- the pig -----
    p = []
    # curly tail, kept clear of the body so it reads against the flag
    p.append('<path d="M392 206 c22 -12 31 4 22 15 c-8 9 -21 2 -16 -7" fill="none" '
             'stroke="url(#crack)" stroke-width="11" stroke-linecap="round"/>')
    p.append('<ellipse cx="282" cy="246" rx="126" ry="80" fill="url(#pork)"/>')
    # crisped back, softened into the body
    p.append('<path d="M176 222 C212 172 356 172 400 224 C352 194 224 194 176 222 Z" '
             'fill="url(#crack)" opacity=".55" filter="url(#soft2)"/>')
    # hind legs tucked under
    for lx, ly in ((352, 308), (236, 312)):
        p.append(f'<ellipse cx="{lx}" cy="{ly}" rx="30" ry="22" fill="url(#crack)" transform="rotate(14 {lx} {ly})"/>')
    # head
    p.append('<circle cx="170" cy="236" r="62" fill="url(#pork)"/>')
    # ear
    p.append('<path d="M148 182 c-10 -34 14 -46 36 -30 c-12 6 -24 16 -36 30 Z" fill="url(#ear)"/>')
    # snout
    p.append('<ellipse cx="118" cy="252" rx="34" ry="27" fill="url(#snout)"/>')
    p.append('<ellipse cx="109" cy="252" rx="6" ry="8" fill="#9A5B42"/>')
    p.append('<ellipse cx="128" cy="252" rx="6" ry="8" fill="#9A5B42"/>')
    # a contented closed eye
    p.append('<path d="M156 222 c9 -9 22 -9 31 0" fill="none" stroke="#6E3F28" '
             'stroke-width="8.5" stroke-linecap="round"/>')
    # cheek blush
    p.append('<ellipse cx="154" cy="256" rx="14" ry="9" fill="#D4705A" opacity=".45"/>')
    # specular sheen along the roasted back
    p.append('<ellipse cx="258" cy="208" rx="78" ry="19" fill="#FFF0D8" opacity=".30" filter="url(#soft2)"/>')
    s.append(f'<g filter="url(#sh)">{"".join(p)}</g>')

    # ----- glass of rakia (front left) -----
    # a small rakia tumbler with a golden measure in it
    g = []
    g.append('<path d="M100 352 h70 l-11 96 h-48 Z" fill="url(#glass)" opacity=".93"/>')
    g.append('<path d="M107 384 h56 l-8 64 h-40 Z" fill="url(#rakia)"/>')
    g.append('<path d="M109 358 h12 l-9 84 h-11 Z" fill="url(#glassSheen)" opacity=".8"/>')
    g.append('<ellipse cx="135" cy="352" rx="35" ry="9" fill="#FFFFFF" opacity=".5"/>')
    g.append('<ellipse cx="135" cy="384" rx="28" ry="7" fill="#FFFFFF" opacity=".30"/>')
    s.append(f'<g filter="url(#shs)">{"".join(g)}</g>')

    # ----- bowl of shopska salad (front right) -----
    sa = []
    # heaped tomato and cucumber first, so the rim of the bowl cuts across them
    veg = [(348, 366, 'tom'), (374, 354, 'cuc'), (400, 360, 'tom'),
           (424, 370, 'cuc'), (358, 384, 'cuc'), (414, 386, 'tom'), (386, 378, 'tom')]
    for vx, vy, nm in veg:
        sa.append(f'<rect x="{vx-12}" y="{vy-11}" width="24" height="22" rx="7" fill="url(#{nm})"/>')
    # a cap of grated sirene, small enough to leave the salad showing
    sa.append('<ellipse cx="388" cy="358" rx="32" ry="12" fill="url(#sir)"/>')
    sa.append('<ellipse cx="376" cy="355" rx="11" ry="5" fill="#FFFFFF" opacity=".8"/>')
    # the bowl in front
    sa.append('<path d="M320 382 h132 c-7 48 -29 72 -66 72 c-37 0 -59 -24 -66 -72 Z" fill="url(#bowl)"/>')
    sa.append('<path d="M320 382 h132" stroke="#FFFFFF" stroke-width="6" stroke-linecap="round" opacity=".6"/>')
    s.append(f'<g filter="url(#shs)">{"".join(sa)}</g>')

    k = scene_scale
    tr = '' if k == 1 else f' transform="translate({256*(1-k):.2f},{262*(1-k):.2f}) scale({k})"'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S} {S}" width="{S}" height="{S}">'
            f'<defs>{"".join(d)}</defs>{"".join(b)}<g{tr}>{"".join(s)}</g></svg>')


if __name__ == '__main__':
    out = os.path.dirname(os.path.abspath(__file__))
    open(out + '/icon.svg', 'w').write(svg(1.0))
    open(out + '/icon-maskable.svg', 'w').write(svg(0.78))
    print('wrote icon.svg, icon-maskable.svg')
