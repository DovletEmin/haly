# -*- coding: utf-8 -*-
"""The five great Turkmen weaving groups, as palettes and knotted motifs.

Each style gives the field guls for four levels of activity (two colourings
each, alternated across the field as neighbouring guls swap dyes on a real
rug), a main border, an elem motif, and the dyes for everything else.

Motifs are drawn on the knot lattice, centred on knot (0, 0), and must fit in
a 9 x 9 day cell. At that size a gul is a sign of the real one rather than a
copy, so each keeps what tells the groups apart at a glance: the quartered
Tekke gul, the clawed Yomut dyrnak, the turreted Salor gul, the Saryk gul
with its pale diamond heart, and the lobed Ersari gulli gul with trefoils.
"""
from dataclasses import dataclass
from typing import Callable, Dict, Optional, Tuple

Knots = Dict[Tuple[int, int], str]


@dataclass
class Palette:
    ground: str          # field and elem
    border: str          # main border ground
    dark: str            # outlines, usually indigo
    light: str           # undyed wool or cotton
    gold: str
    red: str
    dim: str             # the quietest days
    accent: str
    cord: str            # selvedge wrap
    warp: str            # fringe
    lattice: Optional[str] = None


@dataclass
class Style:
    name: str
    title: str           # for the alt text
    p: Palette
    day: Dict[int, Tuple[Knots, Knots]]
    elem: Tuple[Knots, Knots]
    border_symbols: Optional[Tuple[Tuple[Knots, Knots], Knots]] = None
    border_band: Optional[Callable[[int, int], str]] = None
    light_border: bool = False
    notes: str = ''


# --- shapes on the knot lattice ---------------------------------------------
def octagon(r, trim=0):
    lim = r + r // 2 - trim
    return {(x, y) for x in range(-r, r + 1) for y in range(-r, r + 1)
            if abs(x) + abs(y) <= lim}


def inner_octagon(r):
    return {p for p in octagon(r, 1) if abs(p[0]) < r and abs(p[1]) < r}


def diamond(r):
    return {(x, y) for x in range(-r, r + 1) for y in range(-r, r + 1) if abs(x) + abs(y) <= r}


def corners():
    return ((1, 1), (1, -1), (-1, 1), (-1, -1))


def small(r, fill, line, eye):
    k = {p: (line if abs(p[0]) + abs(p[1]) == r else fill) for p in diamond(r)}
    k[(0, 0)] = eye
    return k


def plus(r, arm, eye, tips=None):
    k = {}
    for i in range(-r, r + 1):
        k[(i, 0)] = arm
        k[(0, i)] = arm
    for sx, sy in corners():
        k[(sx, sy)] = arm
    if tips:
        for i in (-r, r):
            k[(i, 0)] = tips
            k[(0, i)] = tips
    k[(0, 0)] = eye
    return k


def ashik(c, inner):
    """Hooked diamond, the commonest elem motif."""
    k = {p: c for p in diamond(4) if abs(p[0]) + abs(p[1]) == 4}
    k.update({p: inner for p in diamond(1)})
    k[(0, 0)] = c
    for sx, sy in corners():
        k[(2 * sx, 2 * sy)] = c
    return k


# Tekke: the quartered octagon, opposite quarters sharing a dye
def tekke_gul(r, a, b, eye, line, dot=None, hooks=None):
    inner = inner_octagon(r)
    k = {}
    for p in octagon(r):
        x, y = p
        if p not in inner or x == 0 or y == 0:
            k[p] = line
        else:
            k[p] = a if x * y > 0 else b
    if dot and r >= 4:
        for sx, sy in corners():
            k[(2 * sx, 2 * sy)] = dot
    k[(0, 0)] = eye
    if hooks:
        for sx, sy in corners():
            k[(r * sx, r * sy)] = hooks
    return k


# Yomut: the dyrnak, a striped diamond with claws along its edges
def dyrnak(r, a, b, line, claws, eye):
    k = {}
    for x, y in diamond(r):
        k[(x, y)] = line if abs(x) + abs(y) == r else (a if y % 2 == 0 else b)
    for x in range(-r, r + 1):
        for y in range(-r, r + 1):
            if abs(x) + abs(y) == r + 1 and abs(x) % 2 == 1:
                k[(x, y)] = claws
    k[(0, 0)] = eye
    return k


# Salor: an octagon with a turret on each axis, quartered on the diagonals
def turreted(r, a, b, line, eye, heart):
    k = {}
    inner = inner_octagon(r)
    for p in octagon(r):
        x, y = p
        if p not in inner:
            k[p] = line
        elif abs(x) == abs(y):
            k[p] = heart                      # the diagonals, picked out
        else:
            k[p] = a if abs(x) > abs(y) else b
    for s in (-1, 1):                         # turrets: a pale step, capped dark
        for i in (-1, 0, 1):
            k[(i, s * (r + 1))] = line
            k[(s * (r + 1), i)] = line
        k[(0, s * r)] = a
        k[(s * r, 0)] = a
    k[(0, 0)] = eye
    return k


# Saryk: a plain octagon round a pale diamond heart
def saryk_gul(r, fill, ring, line, eye, axis):
    k = {}
    inner = inner_octagon(r)
    for p in octagon(r):
        k[p] = fill if p in inner else line
    hr = max(1, r - 2)
    for x, y in diamond(hr):
        k[(x, y)] = ring if abs(x) + abs(y) == hr else line
    if r >= 4:
        for s in (-1, 1):
            k[(0, s * (r - 1))] = axis
            k[(s * (r - 1), 0)] = axis
    k[(0, 0)] = eye
    return k


# Ersari: the gulli gul, lobed at the axes, a trefoil in every quarter
def gulli(r, fill, leaf, line, heart, eye):
    k = {}
    inner = inner_octagon(r)
    for p in octagon(r):
        k[p] = fill if p in inner else line
    for s in (-1, 1):                         # the lobes: tips pulled in
        del k[(0, s * r)]
        del k[(s * r, 0)]
        k[(0, s * (r - 1))] = line
        k[(s * (r - 1), 0)] = line
    a, b = (2, 1) if r >= 4 else (1, 1)
    for sx, sy in corners():
        for dx, dy in ((a, b), (b, a), (a, a)):
            if (dx * sx, dy * sy) in inner:
                k[(dx * sx, dy * sy)] = leaf
    for p in diamond(1):
        k[p] = heart
    k[(0, 0)] = eye
    return k


# --- the styles -------------------------------------------------------------
def tekke():
    p = Palette(ground='#7B2521', border='#4B1918', dark='#1C2231', light='#E3D5B8',
                gold='#C58C3D', red='#B4432B', dim='#93392B', accent='#B4432B',
                cord='#2A1716', warp='#E4DAC6', lattice='#4F181B')
    return Style(
        'tekke', 'Tekke', p,
        day={1: (small(1, p.dim, p.dim, p.dark),) * 2,
             2: (small(2, p.red, p.dark, p.gold), small(2, p.red, p.dark, p.light)),
             3: (tekke_gul(3, p.gold, p.red, p.light, p.dark), tekke_gul(3, p.red, p.gold, p.light, p.dark)),
             4: (tekke_gul(4, p.light, p.gold, p.red, p.dark, dot=p.red, hooks=p.gold),
                 tekke_gul(4, p.gold, p.light, p.red, p.dark, dot=p.dark, hooks=p.light))},
        elem=(ashik(p.light, p.dark), ashik(p.gold, p.dark)),
        border_symbols=((tekke_gul(4, p.light, p.red, p.dark, p.dark, dot=p.dark),
                         tekke_gul(4, p.red, p.light, p.dark, p.dark, dot=p.light)),
                        small(2, p.gold, p.dark, p.border)),
        notes='Madder field, quartered guls linked by a dark lattice.')


def yomut():
    p = Palette(ground='#62262C', border='#D6C7A8', dark='#1D2838', light='#E7DDC7',
                gold='#C99E48', red='#A5392F', dim='#86383A', accent='#4C6B55',
                cord='#2B1A1C', warp='#E2D8C3')

    def running_dog(along, across):
        """The Yomut 'running dog': a stepped zigzag with diamonds in its bays."""
        t = along % 16
        y = 2 + abs(t - 8)
        if across in (y, y + 1):
            return p.dark
        for ct, ca, ring in ((8, 8, p.red), (0, 4, p.accent)):
            dt = min(abs(t - ct), 16 - abs(t - ct))
            d = dt + abs(across - ca)
            if d == 0:
                return p.gold
            if d <= 2:
                return ring
        return p.border

    return Style(
        'yomut', 'Yomut', p,
        day={1: (small(1, p.dim, p.dim, p.dark),) * 2,
             2: (small(2, p.accent, p.dark, p.light), small(2, p.red, p.dark, p.light)),
             3: (dyrnak(3, p.red, p.gold, p.dark, p.light, p.light),
                 dyrnak(3, p.gold, p.red, p.dark, p.light, p.dark)),
             4: (dyrnak(4, p.light, p.red, p.dark, p.gold, p.accent),
                 dyrnak(4, p.red, p.light, p.dark, p.gold, p.dark))},
        elem=(dyrnak(3, p.light, p.gold, p.dark, p.red, p.red),
              dyrnak(3, p.gold, p.light, p.dark, p.accent, p.accent)),
        border_band=running_dog, light_border=True,
        notes='Aubergine-brown field, clawed dyrnak guls, a running-dog border on ivory.')


def salor():
    p = Palette(ground='#8A1F2B', border='#5C1521', dark='#1A2137', light='#E8DCC5',
                gold='#C79343', red='#B83A3A', dim='#9C3446', accent='#D07587',
                cord='#2C1218', warp='#E6DCC8')
    return Style(
        'salor', 'Salor', p,
        day={1: (small(1, p.dim, p.dim, p.dark),) * 2,
             2: (small(2, p.accent, p.dark, p.light), small(2, p.red, p.dark, p.light)),
             3: (turreted(2, p.accent, p.red, p.dark, p.light, p.gold),
                 turreted(2, p.red, p.accent, p.dark, p.light, p.gold)),
             4: (turreted(3, p.light, p.accent, p.dark, p.red, p.gold),
                 turreted(3, p.accent, p.light, p.dark, p.red, p.dark))},
        elem=(ashik(p.light, p.dark), ashik(p.accent, p.dark)),
        border_symbols=((turreted(3, p.light, p.red, p.dark, p.accent, p.gold),
                         turreted(3, p.red, p.light, p.dark, p.accent, p.dark)),
                        plus(2, p.gold, p.light, tips=p.dark)),
        notes='Crimson field from lac and cochineal, turreted guls, pink silk highlights.')


def saryk():
    p = Palette(ground='#4B1F2B', border='#33161F', dark='#131925', light='#F2EEE6',
                gold='#B88A3E', red='#A12E2E', dim='#6E2C3A', accent='#7C3A5C',
                cord='#22121A', warp='#EEE9DF')
    return Style(
        'saryk', 'Saryk', p,
        day={1: (small(1, p.dim, p.dim, p.dark),) * 2,
             2: (small(2, p.accent, p.dark, p.light), small(2, p.red, p.dark, p.light)),
             3: (saryk_gul(3, p.red, p.light, p.dark, p.gold, p.gold),
                 saryk_gul(3, p.accent, p.light, p.dark, p.gold, p.gold)),
             4: (saryk_gul(4, p.red, p.light, p.dark, p.gold, p.gold),
                 saryk_gul(4, p.accent, p.light, p.dark, p.gold, p.light))},
        elem=(ashik(p.light, p.dark), ashik(p.red, p.dark)),
        border_symbols=((saryk_gul(4, p.red, p.light, p.dark, p.gold, p.light),
                         saryk_gul(4, p.accent, p.light, p.dark, p.gold, p.light)),
                        plus(2, p.light, p.gold)),
        notes='Deep aubergine field, sober guls with hearts of bright white cotton.')


def ersari():
    p = Palette(ground='#9C3E2A', border='#6A281E', dark='#1E2B3E', light='#EADBB8',
                gold='#DCA93A', red='#C2502F', dim='#82352A', accent='#55703F',
                cord='#2E1A14', warp='#D9CCB2')

    def lozenges(along, across):
        """A chain of lozenges, each ringed in gold."""
        t = along % 12
        if t == 0:
            return p.gold if abs(across - 6) <= 1 else p.border
        d = abs(t - 6) + abs(across - 6)
        if d == 5:
            return p.dark
        if d == 3:
            return p.gold
        if d <= 1:
            return p.light
        if d < 5:
            return p.red
        return p.border

    return Style(
        'ersari', 'Ersari', p,
        day={1: (small(1, p.dim, p.dim, p.dark),) * 2,
             2: (small(2, p.gold, p.dark, p.red), small(2, p.gold, p.dark, p.light)),
             3: (gulli(3, p.red, p.gold, p.dark, p.accent, p.light),
                 gulli(3, p.red, p.light, p.dark, p.gold, p.dark)),
             4: (gulli(4, p.red, p.gold, p.dark, p.accent, p.light),
                 gulli(4, p.dark, p.light, p.gold, p.gold, p.red))},
        elem=(plus(3, p.gold, p.light, tips=p.dark), plus(3, p.light, p.gold, tips=p.dark)),
        border_band=lozenges,
        notes='Brick-red field, big lobed gulli guls with trefoils, strong yellow and green.')


STYLES = {s.name: s for s in (tekke(), yomut(), salor(), saryk(), ersari())}


def get(name):
    key = (name or 'tekke').strip().lower()
    if key not in STYLES:
        raise SystemExit('Unknown style %r. Choose one of: %s.' % (name, ', '.join(STYLES)))
    return STYLES[key]
