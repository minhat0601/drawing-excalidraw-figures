#!/usr/bin/env python3
"""Draw REAL Excalidraw figures from a short JSON spec file.

    python3 scripts/ve.py <spec.json> [spec2.json ...] [--out DIR] [--col N] [--lib file.excalidrawlib]
    python3 scripts/ve.py --icons            list the available icons

Each spec produces four files with the same name:
    <name>.excalidraw   source scene; drop it on excalidraw.com to keep editing
    <name>.svg          static SVG: colors are var(--token), text is Patrick Hand
    <name>-light.png    preview in the 666px column (--col N for another width), light theme   <- you MUST open and look
    <name>-dark.png     same, dark theme                           <- you MUST open and look

Full spec syntax: references/spec.md. Uses the same @excalidraw/excalidraw library as the
site build (.cache/exca.bundle.js). Only READS engine/; changes nothing in the repo.
Exits 1 on a hard error (✗ lines), 0 when there are only reminders (• lines).
"""
import copy, json, math, pathlib, re, sys

SKILL = pathlib.Path(__file__).resolve().parents[1]
# Tìm thư mục gốc chứa engine/: đứng ở repo riêng (engine/ nằm cạnh SKILL.md)
# hay cài trong .claude/skills/ của một dự án lớn hơn (engine/ nằm ở gốc dự án).
ROOT = next((p for p in (SKILL, *SKILL.parents) if (p / 'engine' / 'excalidraw.py').exists()),
            SKILL.parents[2])
sys.path.insert(0, str(ROOT / 'engine'))
import excalidraw as X   # noqa: E402  only borrows serve(), PAGE, _fix_mask_luminance
import theme as T        # noqa: E402

COT = 666            # content column width at the viewport precheck.py measures
CHU_MIN = 8.0        # px on screen, same threshold as the precheck.py gate
CHU_NEN = 12.0       # below this: reminder, not an error
MAU = dict(T.LIGHT)
NEN = dict(T.FILL_LIGHT, **{'fill-soft': T.LIGHT['fill-soft']})
# Code block: dark background in BOTH themes. The hex of --pre-bg equals --ink in the light
# theme, so it cannot go through tokenize(); use two sentinel hexes and swap them by hand first.
CANH_NEN, CANH_CHU = '#0B1021', '#DDE7F7'
# Literal object colors (a dark moth, a soot-black trunk, white paper): same value in BOTH themes,
# because the figure's meaning is that brightness. Every other token flips in the dark theme.
# The hexes are the --lit-* values themselves; they must be swapped to var(--lit-*) BEFORE
# tokenize() - both sit within _nearest's 30-unit radius of ink/paper, so tokenize() alone
# would absorb them (see tests/test_theme.py::test_lit_hex_song_sot_*).
LIT = {'lit-dark': T.UI_TOKENS['lit-dark'][0], 'lit-light': T.UI_TOKENS['lit-light'][0]}
SHAPES = ('box', 'ellipse', 'diamond')
ACCENT = {'l3', 'l4', 'l6', 'l7', 'err', 'warn', 'node', 'heap', 'hot'}


class Loi(SystemExit):
    pass


def chet(msg):
    raise Loi(f'✗ {msg}')


# ───────────────────────── colors ─────────────────────────
def mau(v):
    if v == 'code-fg':
        return CANH_CHU
    if v in LIT:
        return LIT[v]
    if v not in MAU:
        chet(f"color '{v}' is not a token. Use: {' '.join(MAU)} {' '.join(LIT)}")
    return MAU[v]


def nen(v):
    if not v:
        return 'transparent'
    if v == 'code':
        return CANH_NEN
    if v == 'ink':
        return MAU['ink']
    if v in LIT:
        return LIT[v]
    k = 'fill-soft' if v == 'soft' else f'fill-{v}'
    if k not in NEN:
        chet(f"fill '{v}' does not exist. Use: soft {' '.join(x[5:] for x in T.FILL_LIGHT)} {' '.join(LIT)}")
    return NEN[k]


# ───────────────────────── geometry ─────────────────────────
def tam(b):
    return b['x'] + b['w'] / 2, b['y'] + b['h'] / 2


def mep(b, side, at=0.5):
    x, y, w, h = b['x'], b['y'], b['w'], b['h']
    return {'top': (x + w * at, y), 'bottom': (x + w * at, y + h),
            'left': (x, y + h * at), 'right': (x + w, y + h * at)}[side]


def cat(b, tx, ty):
    """Intersection of the ray center(b) -> (tx,ty) with the edge of shape b."""
    cx, cy = tam(b)
    dx, dy = tx - cx, ty - cy
    if not dx and not dy:
        return cx, cy
    hw, hh = b['w'] / 2, b['h'] / 2
    kind = b.get('shape', b.get('t'))
    if kind == 'ellipse':
        k = 1 / math.hypot(dx / hw, dy / hh)
    elif kind == 'diamond':
        k = 1 / (abs(dx) / hw + abs(dy) / hh)
    else:
        k = min(hw / abs(dx) if dx else 1e9, hh / abs(dy) if dy else 1e9)
    return cx + dx * k, cy + dy * k


def lui(p, q, d=6):
    L = math.hypot(q[0] - p[0], q[1] - p[1]) or 1
    return p[0] + (q[0] - p[0]) * d / L, p[1] + (q[1] - p[1]) * d / L


def rong_chu(s, size):
    """Estimate Nunito text width. Good enough for placement; Excalidraw does the real measuring."""
    return max((len(l) for l in str(s).split('\n')), default=0) * size * 0.52


def cao_chu(s, size):
    return (str(s).count('\n') + 1) * size * 1.25


# ───────────────────────── macros ─────────────────────────
# Each function takes one spec element and returns a list of BASE elements:
#   box ellipse diamond arrow line text  +  anchor (invisible area arrows attach to)  +  raw
def _khung(e, **kw):
    """Ghost box: transparent border, only there so text centers itself in an area."""
    return dict({'t': 'box', 'ghost': True, 'x': e['x'], 'y': e['y'], 'w': e['w'], 'h': e['h'],
                 'text': e.get('text'), 'size': e.get('size', 18), 'color': e.get('color', 'ink')}, **kw)


def m_frame(e):
    out = [dict(e, t='box', text=None, sharp=e.get('sharp', False))]
    if e.get('title'):
        s = e.get('size', 16)
        out.append({'t': 'text', 'x': e['x'] + 12, 'y': e['y'] + 8, 'text': e['title'], 'size': s,
                    'color': e.get('titleColor', e.get('color', 'muted'))})
    return out


def m_cells(e):
    col, ws, out, chay = e.get('dir') == 'col', e.get('widths'), [], 0
    labs = e['labels']
    if ws and len(ws) != len(labs):
        chet(f"cells '{e['id']}': widths has {len(ws)} items, labels has {len(labs)}")
    for i, lab in enumerate(labs):
        m = e.get('marks', {}).get(str(i), {})
        buoc = ws[i] if ws else (e['ch'] if col else e['cw'])
        b = {'t': 'box', 'id': f"{e['id']}.{i}", 'sharp': True,
             'x': e['x'] + (0 if col else chay), 'y': e['y'] + (chay if col else 0),
             'w': e['cw'] if col else buoc, 'h': buoc if col else e['ch'],
             'text': lab, 'size': e.get('size', 18)}
        for k in ('color', 'fill', 'fillStyle', 'weight', 'dashed'):
            v = m.get(k, e.get(k))
            if v is not None:
                b[k] = v
        out.append(b)
        if e.get('index'):
            ix = e['index'][i] if isinstance(e['index'], list) else str(i)
            if col:
                out.append({'t': 'text', 'x': b['x'] - 12 - rong_chu(ix, 15), 'y': b['y'] + b['h'] / 2 - 9,
                            'text': ix, 'size': 15, 'color': 'muted'})
            else:
                out.append({'t': 'text', 'x': b['x'] + b['w'] / 2 - rong_chu(ix, 15) / 2, 'y': b['y'] - 22,
                            'text': ix, 'size': 15, 'color': 'muted'})
        chay += buoc
    tot_w = e['cw'] if col else chay
    tot_h = chay if col else e['ch']
    out.append({'t': 'anchor', 'id': e['id'], 'x': e['x'], 'y': e['y'], 'w': tot_w, 'h': tot_h})
    if e.get('title'):
        out.append({'t': 'text', 'x': e['x'], 'y': e['y'] - (46 if e.get('index') and not col else 28),
                    'text': e['title'], 'size': 16, 'color': e.get('titleColor', 'muted')})
    return out


def m_grid(e):
    out = []
    for r, row in enumerate(e['rows']):
        for c, lab in enumerate(row):
            m = e.get('marks', {}).get(f'{r},{c}', {})
            b = {'t': 'box', 'id': f"{e['id']}.{r}.{c}", 'sharp': True, 'x': e['x'] + c * e['cw'],
                 'y': e['y'] + r * e['ch'], 'w': e['cw'], 'h': e['ch'], 'text': lab, 'size': e.get('size', 16)}
            for k in ('color', 'fill', 'fillStyle', 'weight'):
                v = m.get(k, e.get(k))
                if v is not None:
                    b[k] = v
            out.append(b)
    out.append({'t': 'anchor', 'id': e['id'], 'x': e['x'], 'y': e['y'],
                'w': e['cw'] * max(len(r) for r in e['rows']), 'h': e['ch'] * len(e['rows'])})
    return out


def m_table(e):
    cols, rh, out = e['cols'], e.get('rh', 38), []
    y = e['y']
    if e.get('title'):
        out.append({'t': 'text', 'x': e['x'], 'y': y - 28, 'text': e['title'], 'size': 16, 'color': 'muted'})
    rows = ([e['head']] if e.get('head') else []) + e['rows']
    for r, row in enumerate(rows):
        la_head = bool(e.get('head')) and r == 0
        ri = r - (1 if e.get('head') else 0)
        m = {} if la_head else e.get('marks', {}).get(str(ri), {})
        x = e['x']
        for c, lab in enumerate(row):
            mc = {} if la_head else e.get('marks', {}).get(f'{ri},{c}', {})
            b = {'t': 'box', 'id': f"{e['id']}.{'h' if la_head else ri}.{c}", 'sharp': True, 'x': x, 'y': y,
                 'w': cols[c], 'h': rh, 'text': str(lab), 'size': e.get('size', 16),
                 'color': mc.get('color', m.get('color', e.get('color', 'ink'))),
                 'fill': mc.get('fill', m.get('fill', 'soft' if la_head else e.get('fill')))}
            if mc.get('fillStyle') or m.get('fillStyle'):
                b['fillStyle'] = mc.get('fillStyle') or m.get('fillStyle')
            if mc.get('dashed', m.get('dashed')):
                b['dashed'] = True
            out.append(b)
            x += cols[c]
        if not la_head:
            out.append({'t': 'anchor', 'id': f"{e['id']}.{ri}", 'x': e['x'], 'y': y, 'w': sum(cols), 'h': rh})
        y += rh
    out.append({'t': 'anchor', 'id': e['id'], 'x': e['x'], 'y': e['y'], 'w': sum(cols), 'h': y - e['y']})
    return out


def m_entity(e):
    fs, lh = e.get('size', 16), 24
    hh, bh = 36, lh * len(e['fields']) + 14
    c = e.get('color', 'ink')
    return [
        {'t': 'box', 'x': e['x'], 'y': e['y'], 'w': e['w'], 'h': hh, 'sharp': True, 'text': e['name'],
         'size': 18, 'color': c, 'fill': e.get('fill', 'soft')},
        {'t': 'box', 'x': e['x'], 'y': e['y'] + hh, 'w': e['w'], 'h': bh, 'sharp': True, 'color': c,
         'text': '\n'.join(e['fields']), 'size': fs, 'align': 'left', 'valign': 'top'},
        {'t': 'anchor', 'id': e['id'], 'x': e['x'], 'y': e['y'], 'w': e['w'], 'h': hh + bh},
    ]


def m_code(e):
    fs = e.get('size', 15)
    lines = e['text'].split('\n')
    # The title never outgrows the code: a size-12 block under a size-15 title read as a heading
    # bigger than its own content (infra2 run).
    ts = min(15, fs)
    can = max([rong_chu(l, fs) * 1.17 for l in lines] + [rong_chu(e.get('title', ''), ts) * 1.17]) + 32
    # The text and title are free texts over the box, so no overflow check sees them leave it:
    # a 27-char title in a `w` 252 block ran past the right border with a silent ✓ (ds3 run).
    if e.get('w') and e['w'] < can - 8:
        chet(f"code '{e['id']}': w {e['w']} is narrower than its longest line or title needs (about {can:.0f}): "
             f"raise w or shorten that line")
    w = e.get('w') or can
    th = 26 if e.get('title') else 0
    h = len(lines) * fs * 1.3 + 24 + th
    # `color` marks the block itself as broken (err), correct (node) or under discussion (l4):
    # the text inside is always code-fg on the dark ground, so the border is the only place
    # an accent can go; without it, "run 2 fails / run 2 is silent" needed loose labels (infra2 run).
    out = [{'t': 'box', 'id': e['id'], 'x': e['x'], 'y': e['y'], 'w': w, 'h': h,
            'color': e.get('color', 'line'), 'fill': 'code', 'weight': 2 if e.get('color') else 1},
           {'t': 'text', 'x': e['x'] + 16, 'y': e['y'] + 12 + th, 'text': e['text'], 'size': fs,
            'color': 'code-fg', 'mono': True}]
    if e.get('title'):
        out.append({'t': 'text', 'x': e['x'] + 16, 'y': e['y'] + 8, 'text': e['title'], 'size': ts,
                    'color': 'code-fg', 'mono': True, 'opacity': 60})
    return out


def m_axis(e):
    x, y, L, c = e['x'], e['y'], e['length'], e.get('color', 'ink')
    doc = e.get('dir') == 'y'
    out = [{'t': 'arrow', 'points': [[x, y], [x, y - L] if doc else [x + L, y]], 'color': c}]
    ticks = e.get('ticks', [])
    for i, lab in enumerate(ticks):
        d = e['gap'] * i if e.get('gap') else (L - 40) * i / max(len(ticks) - 1, 1)
        s = e.get('size', 15)
        if doc:
            out.append({'t': 'line', 'points': [[x - 6, y - d], [x + 6, y - d]], 'color': c})
            out.append({'t': 'text', 'x': x - 14 - rong_chu(lab, s), 'y': y - d - s * 0.6, 'text': lab,
                        'size': s, 'color': 'muted'})
        else:
            out.append({'t': 'line', 'points': [[x + d, y - 6], [x + d, y + 6]], 'color': c})
            out.append({'t': 'text', 'x': x + d - rong_chu(lab, s) / 2, 'y': y + 12, 'text': lab,
                        'size': s, 'color': 'muted'})
    if e.get('label'):
        out.append({'t': 'text', 'x': x - rong_chu(e['label'], 17) / 2 if doc else x + L + 10,
                    'y': y - L - 30 if doc else y - 12, 'text': e['label'], 'size': 17, 'color': c})
    return out


def m_span(e):
    """Bracket measuring a span: |------|  with a label."""
    c, y = e.get('color', 'muted'), e['y']
    x1, x2 = e['x1'], e['x2']
    s = e.get('size', 16)
    duoi = e.get('side', 'below') == 'below'
    out = [{'t': 'line', 'points': [[x1, y], [x2, y]], 'color': c, 'weight': e.get('weight', 2)},
           {'t': 'line', 'points': [[x1, y - 8], [x1, y + 8]], 'color': c},
           {'t': 'line', 'points': [[x2, y - 8], [x2, y + 8]], 'color': c}]
    if e.get('text'):
        out.append({'t': 'text', 'x': (x1 + x2) / 2 - rong_chu(e['text'], s) / 2,
                    'y': y + 12 if duoi else y - 12 - cao_chu(e['text'], s), 'text': e['text'],
                    'size': s, 'color': c})
    return out


def m_plot(e):
    x, y, w, h = e['x'], e['y'], e['w'], e['h']       # (x,y) = BOTTOM-LEFT corner of the plot area
    out = [{'t': 'arrow', 'points': [[x, y], [x + w + 20, y]]}, {'t': 'arrow', 'points': [[x, y], [x, y - h - 20]]}]
    if e.get('xlabel'):
        out.append({'t': 'text', 'x': x + w + 28, 'y': y - 12, 'text': e['xlabel'], 'size': 16, 'color': 'muted'})
    if e.get('ylabel'):
        out.append({'t': 'text', 'x': x - 10, 'y': y - h - 50, 'text': e['ylabel'], 'size': 16, 'color': 'muted'})
    vmax = e.get('max') or max([b['value'] for b in e.get('bars', [])] +
                               [p[1] for s in e.get('lines', []) for p in s['points']] +
                               [t['value'] for t in e.get('thresholds', [])] + [1e-9])
    bars = e.get('bars', [])
    if bars:
        slot = w / len(bars)
        bw = min(slot * 0.62, 70)
        for i, b in enumerate(bars):
            bh = max(h * b['value'] / vmax, 2)
            bx = x + slot * i + (slot - bw) / 2
            out.append({'t': 'box', 'id': f"{e.get('id', 'plot')}.{i}", 'sharp': True, 'x': bx, 'y': y - bh,
                        'w': bw, 'h': bh, 'color': b.get('color', 'l4'), 'fill': b.get('fill', b.get('color', 'l4')),
                        'fillStyle': b.get('fillStyle', 'hachure')})
            if b.get('label'):
                out.append({'t': 'text', 'x': bx + bw / 2 - rong_chu(b['label'], 15) / 2, 'y': y + 10,
                            'text': b['label'], 'size': 15, 'color': 'muted'})
            if b.get('text'):
                out.append({'t': 'text', 'x': bx + bw / 2 - rong_chu(b['text'], 15) / 2, 'y': y - bh - 24,
                            'text': b['text'], 'size': 15, 'color': b.get('color', 'l4')})
    for s in e.get('lines', []):
        xm = e.get('xmax') or max(p[0] for p in s['points'])
        pts = [[x + w * p[0] / xm, y - h * p[1] / vmax] for p in s['points']]
        out.append({'t': 'line', 'points': pts, 'color': s.get('color', 'l4'), 'weight': 3, 'smooth': s.get('smooth', True)})
        if s.get('label'):
            out.append({'t': 'text', 'x': pts[-1][0] + 8, 'y': pts[-1][1] - 12, 'text': s['label'], 'size': 15,
                        'color': s.get('color', 'l4')})
    for t in e.get('thresholds', []):
        ty = y - h * t['value'] / vmax
        out.append({'t': 'line', 'points': [[x, ty], [x + w, ty]], 'color': t.get('color', 'err'), 'dashed': True})
        if t.get('label'):
            out.append({'t': 'text', 'x': x + w + 8, 'y': ty - 12, 'text': t['label'], 'size': 15,
                        'color': t.get('color', 'err')})
    for xv in e.get('xticks', []):
        tx = x + w * xv['at']
        out.append({'t': 'line', 'points': [[tx, y - 5], [tx, y + 5]]})
        out.append({'t': 'text', 'x': tx - rong_chu(xv['label'], 15) / 2, 'y': y + 10, 'text': xv['label'],
                    'size': 15, 'color': 'muted'})
    return out


FRAGS = ('alt', 'opt', 'loop', 'par', 'group', 'break', 'critical')


def m_sequence(e):
    acts, gap, step = e['actors'], e.get('gap', 190), e.get('step', 54)
    aw = max([e.get('aw', 130)] + [rong_chu(a['label'], 17) + 30 for a in acts])
    # A two-line actor label ("Role admin\naccount 123") keeps the column narrow; the box grows to hold it
    # (Excalidraw sets Nunito at 1.35 line height), so a fixed 44 no longer makes it grow (aws1 run).
    ah = max(44, round(max(a['label'].count('\n') + 1 for a in acts) * 17 * 1.35 + 11))
    gap = max(gap, aw + 30)
    pos = {a['id']: e['x'] + i * gap + aw / 2 for i, a in enumerate(acts)}
    xa, xb = min(pos.values()), max(pos.values())
    sid = e.get('id') or f"seq@{e['x']},{e['y']}"      # ids of labels and lifelines, read by the lifeline lint in soat()
    out, y = [], e['y'] + ah + 34
    stack = []

    def cham(x1, x2):
        for f in stack:
            f['x0'], f['x1'] = min(f['x0'], x1), max(f['x1'], x2)

    prev_kind = None
    for m in e['messages']:
        c = m.get('color', 'ink')
        kind = next((k for k in FRAGS if k in m), None)
        prev_kind, open_before = kind, prev_kind
        if kind and y - 34 < e['y'] + ah + 14:
            y += 14
        if kind:                                   # open an alt/opt/loop/par/group frame
            stack.append({'kind': kind, 'label': m[kind], 'top': y - 34, 'x0': 1e9, 'x1': -1e9, 'seps': [],
                          'color': m.get('color', 'muted'), 'over': m.get('over')})
            y += 30
            continue
        if 'else' in m:
            if not stack:
                chet("sequence: 'else' is outside an alt frame")
            stack[-1]['seps'].append((y - 30, m['else']))
            y += 28
            continue
        if m.get('end'):
            if not stack:
                chet("sequence: 'end' has no open frame")
            f = stack.pop()
            if f['over']:
                f['x0'], f['x1'] = min(pos[k] for k in f['over']), max(pos[k] for k in f['over'])
            else:                                   # default: span every lifeline, inset by nesting depth
                f['x0'], f['x1'] = xa - 6 + 12 * len(stack), max(xb + 6 - 12 * len(stack), f['x1'])
                for k, par in enumerate(reversed(stack)):      # parent narrowed with `over`: stay inside it
                    if par['over']:
                        f['x0'] = min(pos[i] for i in par['over']) + 12 * (k + 1)
                        f['x1'] = max(pos[i] for i in par['over']) - 12 * (k + 1)
                        break
            x0, x1, top, bot, fc = f['x0'] - 34, f['x1'] + 34, f['top'], y - 28, f['color']
            tw = rong_chu(f['kind'], 15) + 26
            out.append({'t': 'box', 'x': x0, 'y': top, 'w': x1 - x0, 'h': bot - top, 'sharp': True, 'color': fc,
                        'weight': 1, 'under': True})
            out.append({'t': 'box', 'x': x0, 'y': top, 'w': tw, 'h': 30, 'sharp': True, 'color': fc, 'fill': 'soft',
                        'weight': 1, 'text': f['kind'], 'size': 15})
            if f['label']:
                out.append({'t': 'text', 'x': x0 + tw + 8, 'y': top + 5, 'text': f"[{f['label']}]", 'size': 15, 'color': fc})
            for sy, lab in f['seps']:
                out.append({'t': 'line', 'points': [[x0, sy], [x1, sy]], 'color': fc, 'dashed': True, 'weight': 1})
                if lab:
                    out.append({'t': 'text', 'x': x0 + 10, 'y': sy + 4, 'text': f'[{lab}]', 'size': 15, 'color': fc})
            cham(f['x0'] - 12, f['x1'] + 12)       # outer frame encloses the inner one
            y += 14
            continue
        if ('divider' in m or 'delay' in m) and y - 34 < e['y'] + ah + 14:
            y += 14
        if 'divider' in m:
            w = rong_chu(m['divider'], 15) + 28
            out.append({'t': 'line', 'points': [[xa - aw / 2, y - 12], [xb + aw / 2, y - 12]], 'color': 'muted', 'weight': 1})
            out.append({'t': 'box', 'x': (xa + xb) / 2 - w / 2, 'y': y - 28, 'w': w, 'h': 32, 'text': m['divider'],
                        'size': 15, 'color': 'muted', 'fill': 'soft', 'weight': 1, 'sharp': True})
            y += 44
            continue
        if 'delay' in m:
            out.append({'t': 'text', 'x': (xa + xb) / 2, 'y': y - 22, 'text': m['delay'], 'size': 15, 'color': 'muted',
                        'align': 'center'})
            y += 40
            continue
        if m.get('note'):
            ids = m.get('over') or [acts[0]['id'], acts[-1]['id']]
            pad = 40 if m.get('over') or not stack else 28 - 12 * len(stack)
            x1, x2 = min(pos[k] for k in ids) - pad, max(pos[k] for k in ids) + pad
            nh = max(34, round((m['note'].count('\n') + 1) * 15 * 1.35 + 11))   # multi-line note grows (aws1 run)
            out.append({'t': 'box', 'x': x1, 'y': y - 16, 'w': x2 - x1, 'h': nh, 'text': m['note'], 'size': 15,
                        'color': m.get('color', 'muted'), 'fill': m.get('fill', 'soft'), 'dashed': True, 'weight': 1})
            cham(x1 + pad, x2 - pad)
            y += step * 1.5 + nh - 34
            continue
        nhan = (f"{m['n']}. " if m.get('n') else '') + m.get('text', '')
        if '\n' in nhan:
            chet(f"sequence: message text “{nhan[:30]}” must be one line. Put the detail in a note entry")
        if m.get('self') or m['from'] == m.get('to'):
            # A self-message has no label above its line, so right after a frame opens the 24 units kept for
            # that label stood empty under the frame header (ds3 queue 2: `break` + one self-message).
            if open_before in FRAGS:
                y -= 20
            x = pos[m['from']]
            out.append({'t': 'arrow', 'points': [[x, y], [x + 46, y], [x + 46, y + 26], [x + 4, y + 26]],
                        'color': c, 'dashed': m.get('dashed'), 'sharp': True})
            out.append({'t': 'text', 'id': f"{sid}~lab~{len(out)}", 'x': x + 56, 'y': y, 'text': nhan, 'size': 15, 'color': c})
            cham(x, x + 30 + rong_chu(nhan, 15))
            y += step + 12
            continue
        x1, x2 = pos[m['from']], pos[m['to']]
        d = 1 if x2 > x1 else -1
        if m.get('lost'):                          # request that never gets an answer: stops short, X at the tip
            x2 = x1 + (x2 - x1) * 0.72
            out.append({'t': 'cross', 'x': x2 + 2 * d - 8, 'y': y - 8, 'size': 16})
        out.append({'t': 'arrow', 'points': [[x1 + 3 * d, y], [x2 - 4 * d, y]], 'color': c, 'dashed': m.get('dashed'),
                    'weight': m.get('weight', 2), 'head': m.get('head', 'arrow')})
        # Centred label, anchored at its centre: Excalidraw measures Nunito and the SVG swaps in the narrower
        # Patrick Hand, so a left-anchored label placed with rong_chu drifted ~40 units toward the left lifeline
        # (hang-doi 0.1 run). A message that crosses lifelines gets its label over the first gap (lessons rule 17).
        giua = sorted((p for p in pos.values() if min(x1, x2) < p < max(x1, x2)), key=lambda p: abs(p - x1))
        cx = (x1 + giua[0]) / 2 if giua else (x1 + x2) / 2
        if nhan:
            out.append({'t': 'text', 'id': f"{sid}~lab~{len(out)}", 'x': cx, 'y': y - 24, 'text': nhan,
                        'size': 15, 'color': c, 'align': 'center'})
        if m.get('fail'):
            out.append({'t': 'cross', 'x': cx + rong_chu(nhan, 15) * 0.42 + 8, 'y': y - 26, 'size': 16})
        cham(min(x1, x2), max(x1, x2))
        y += step
    if stack:
        chet(f"sequence: frame '{stack[-1]['kind']}' is not closed with {{\"end\":true}}")
    for a in acts:
        out.append({'t': 'box', 'id': a['id'], 'x': pos[a['id']] - aw / 2, 'y': e['y'], 'w': aw, 'h': ah,
                    'text': a['label'], 'size': 17, 'color': a.get('color', 'ink'), 'fill': a.get('fill', 'soft')})
        out.append({'t': 'line', 'id': f"{sid}~life~{a['id']}", 'points': [[pos[a['id']], e['y'] + ah], [pos[a['id']], y - 10]],
                    'color': 'line', 'dashed': True, 'weight': 1, 'under': True})
    return out


def m_tree(e):
    nw, nh = e.get('nw', 110), e.get('nh', 44)
    dx, dy = e.get('dx', 26), e.get('dy', 64)
    ngang = e.get('dir') == 'right'
    out, dem = [], [0]

    def la(n):
        ch = n.get('children') or []
        return sum(la(c) for c in ch) if ch else 1

    def w_of(n):
        return n.get('w', nw)

    def dat(n, lvl, start):
        """start = start of the leaf strip reserved for n, along the perpendicular axis."""
        ch = n.get('children') or []
        ô = (nh if ngang else nw) + dx
        span = la(n) * ô
        ctr = start + span / 2
        nid = n.get('id') or f"{e.get('id', 'tree')}.{dem[0]}"
        dem[0] += 1
        w, h = w_of(n), n.get('h', nh)
        if ngang:
            x, y = e['x'] + lvl * (nw + dy), e['y'] + ctr - h / 2
        else:
            x, y = e['x'] + ctr - w / 2, e['y'] + lvl * (nh + dy)
        b = {'t': n.get('shape', 'box'), 'id': nid, 'x': x, 'y': y, 'w': w, 'h': h, 'text': n.get('text', ''),
             'size': n.get('size', e.get('size', 17))}
        for k in ('color', 'fill', 'fillStyle', 'dashed', 'sharp', 'weight'):
            v = n.get(k, e.get(k))
            if v is not None:
                b[k] = v
        out.append(b)
        s = start
        for c in ch:
            cid = dat(c, lvl + 1, s)
            s += la(c) * ô
            a = {'t': 'arrow', 'from': nid, 'to': cid, 'color': c.get('edgeColor', e.get('edgeColor', 'ink')),
                 'fromSide': 'right' if ngang else 'bottom', 'toSide': 'left' if ngang else 'top',
                 'head': 'none' if e.get('lines') else 'arrow', 'dashed': c.get('edgeDashed')}
            if c.get('edge'):
                a['text'] = c['edge']
            out.append(a)
        return nid

    dat(e['root'], 0, 0)
    return out


def m_ring(e):
    cx, cy, r = e['cx'], e['cy'], e['r']
    out = [{'t': 'ellipse', 'id': e.get('id', 'ring'), 'x': cx - r, 'y': cy - r, 'w': 2 * r, 'h': 2 * r,
            'color': e.get('color', 'l2')}]

    def pt(a, rr):   # angle 0 = top, clockwise
        t = math.radians(a - 90)
        return cx + rr * math.cos(t), cy + rr * math.sin(t)

    for a in e.get('arcs', []):
        t1, t2 = a['from'], a['to'] + (360 if a['to'] < a['from'] else 0)
        n = max(int((t2 - t1) / 6), 2)
        out.append({'t': 'line', 'points': [list(pt(t1 + (t2 - t1) * i / n, r)) for i in range(n + 1)],
                    'color': a.get('color', 'warn'), 'weight': a.get('weight', 8), 'smooth': True, 'opacity': 70})
        if a.get('label'):
            lx, ly = pt((t1 + t2) / 2, r - 34)
            out.append({'t': 'text', 'x': lx - rong_chu(a['label'], 15) / 2, 'y': ly - 10, 'text': a['label'],
                        'size': 15, 'color': a.get('color', 'warn')})
    for k in e.get('ticks', []):
        p, q = pt(k['angle'], r - 6), pt(k['angle'], r + 6)
        out.append({'t': 'line', 'points': [list(p), list(q)], 'color': 'muted'})
        # a tick at a node's angle (node "at position 25"): push the label inward past the node disc,
        # or it touches the node (sd09 run: "75" sat on the DB4 node)
        near = [n.get('d', 26) for n in e.get('nodes', [])
                if abs((n['angle'] - k['angle'] + 180) % 360 - 180) < 12]
        lx, ly = pt(k['angle'], r - 22 - (max(near) / 2 + 2 if near else 0))
        out.append({'t': 'text', 'x': lx - rong_chu(k['label'], 15) / 2, 'y': ly - 9, 'text': k['label'],
                    'size': 15, 'color': 'muted'})
    for n in e.get('nodes', []):
        d = n.get('d', 26)
        px, py = pt(n['angle'], r)
        c = n.get('color', 'l4')
        out.append({'t': 'ellipse', 'id': n['id'], 'x': px - d / 2, 'y': py - d / 2, 'w': d, 'h': d, 'color': c,
                    'fill': n.get('fill', c), 'dashed': n.get('dashed'), 'fillStyle': n.get('fillStyle', 'solid')})
        if n.get('label'):
            s = n.get('size', 16)
            lx, ly = pt(n['angle'], r + d / 2 + 14)
            ca, sa = math.cos(math.radians(n['angle'] - 90)), math.sin(math.radians(n['angle'] - 90))
            tw, th = rong_chu(n['label'], s), cao_chu(n['label'], s)
            out.append({'t': 'text', 'x': lx - tw / 2 + ca * tw / 2, 'y': ly - th / 2 + sa * th / 2,
                        'text': n['label'], 'size': s, 'color': c})
    return out


def m_lanes(e):
    out, y, lw = [], e['y'], e.get('labelW', 110)
    for ln in e['lanes']:
        h = ln.get('h', 90)
        out.append({'t': 'box', 'id': ln['id'], 'x': e['x'], 'y': y, 'w': e['w'], 'h': h, 'sharp': True,
                    'color': 'line', 'fill': ln.get('fill'), 'weight': 1, 'under': True})
        out.append(_khung({'x': e['x'], 'y': y, 'w': lw, 'h': h, 'text': ln['label'], 'size': 16,
                           'color': ln.get('color', 'muted')}))
        y += h
    out.append({'t': 'line', 'points': [[e['x'] + lw, e['y']], [e['x'] + lw, y]], 'color': 'line', 'weight': 1})
    return out


def m_start(e):
    d = e.get('d', 22)
    return [{'t': 'ellipse', 'id': e.get('id'), 'x': e['x'], 'y': e['y'], 'w': d, 'h': d,
             'color': e.get('color', 'ink'), 'fill': 'ink', 'rough': 0}]


def m_end(e):
    d = e.get('d', 26)
    return [{'t': 'ellipse', 'id': e.get('id'), 'x': e['x'], 'y': e['y'], 'w': d, 'h': d, 'color': e.get('color', 'ink')},
            {'t': 'ellipse', 'x': e['x'] + 6, 'y': e['y'] + 6, 'w': d - 12, 'h': d - 12, 'color': e.get('color', 'ink'),
             'fill': 'ink', 'rough': 0}]


def m_swimlane(e):
    """Business flow: one column per role, nodes placed by (lane, row), edges route orthogonally."""
    lanes, nodes = e['lanes'], e['nodes']
    rh, hh = e.get('rowH', 110), e.get('headH', 40)
    nw, nh, size = e.get('nw', 150), e.get('nh', 56), e.get('size', 16)
    out, x, cx, li = [], e['x'], {}, {}

    def co(n):                                     # node size: explicit w/h win, else fit the text
        k, sz, tx = n.get('kind', 'step'), n.get('size', size), n.get('text', '')
        if k in ('start', 'end', 'merge'):
            return 26, 26
        if k == 'decision':                        # a diamond holds text in its middle half, and wraps when too narrow
            w = n.get('w', max(nw * 1.1, rong_chu(tx, sz) * 2 + 44))
            dong = sum(max(1, math.ceil((rong_chu(l, sz) + 8) / max(w / 2 - 8, 1))) for l in str(tx).split('\n'))
            return w, n.get('h', max(nh * 1.5, dong * sz * 1.25 * 2 + 34))
        return n.get('w', max(nw, rong_chu(tx, sz) + 30)), n.get('h', max(nh, cao_chu(tx, sz) + 26))

    day = e['y'] + hh
    for n in nodes:                                # lanes end just below the lowest node
        h = co(n)[1]
        day = max(day, e['y'] + hh + 8 + n.get('row', 0) * rh + rh / 2 + n.get('dy', 0) + h / 2)
    H = day - e['y'] + 26
    for k, ln in enumerate(lanes):
        w = ln.get('w', e.get('laneW', 190))
        cx[ln['id']], li[ln['id']] = x + w / 2, k
        out.append(_khung({'x': x, 'y': e['y'], 'w': w, 'h': hh, 'text': ln['label'], 'size': 17,
                           'color': ln.get('color', 'ink')}))
        if ln.get('fill'):
            out.append({'t': 'box', 'x': x, 'y': e['y'], 'w': w, 'h': H, 'sharp': True, 'color': 'line',
                        'fill': ln['fill'], 'weight': 1, 'under': True})
        if k:
            out.append({'t': 'line', 'points': [[x, e['y']], [x, e['y'] + H]], 'color': 'line', 'weight': 1, 'under': True})
        x += w
    out.append({'t': 'box', 'x': e['x'], 'y': e['y'], 'w': x - e['x'], 'h': H, 'sharp': True, 'color': 'line',
                'weight': 1, 'under': True})
    out.append({'t': 'line', 'points': [[e['x'], e['y'] + hh], [x, e['y'] + hh]], 'color': 'line', 'weight': 1, 'under': True})
    info = {}
    for n in nodes:
        if n['lane'] not in cx:
            chet(f"swimlane: node '{n.get('id')}' uses lane '{n['lane']}', which does not exist. Lanes: {' '.join(cx)}")
        kind = n.get('kind', 'step')
        mx = cx[n['lane']] + n.get('dx', 0)
        my = e['y'] + hh + 8 + n.get('row', 0) * rh + rh / 2 + n.get('dy', 0)
        info[n['id']] = (li[n['lane']], n.get('row', 0), kind, mx, co(n)[0])
        if kind in ('start', 'end'):
            d = 22 if kind == 'start' else 26
            out.append({'t': kind, 'id': n['id'], 'x': mx - d / 2, 'y': my - d / 2, 'd': d})
            continue
        w, h = co(n)
        b = {'t': 'diamond' if kind in ('decision', 'merge') else 'box', 'id': n['id'], 'x': mx - w / 2, 'y': my - h / 2,
             'w': w, 'h': h, 'text': n.get('text'), 'size': n.get('size', size),
             'color': n.get('color', 'ink')}
        for k in ('fill', 'fillStyle', 'dashed', 'weight'):
            if k in n:
                b[k] = n[k]
        out.append(b)
    for g in e.get('edges', []):
        for k in ('from', 'to'):
            if g.get(k) not in info:
                chet(f"swimlane: edge has {k}='{g.get(k)}', which matches no node. Nodes: {' '.join(info)}")
        (la, ra, ka, xa_, wa_), (lb, rb, _, xb_, _w) = info[g['from']], info[g['to']]
        a = dict(g, t='arrow')
        a.setdefault('size', 15)
        if 'fromSide' not in g and 'toSide' not in g and 'route' not in g and 'bend' not in g and g['from'] != g['to']:
            if abs(xa_ - xb_) < 1:
                a['fromSide'], a['toSide'] = ('bottom', 'top') if rb >= ra else ('top', 'bottom')
            elif ra == rb:
                a['fromSide'], a['toSide'] = ('right', 'left') if xb_ > xa_ else ('left', 'right')
            elif ka in ('decision', 'merge') and abs(xb_ - xa_) >= wa_ / 2 + 12:
                a['fromSide'] = 'right' if xb_ > xa_ else 'left'
                a['toSide'] = 'top' if rb > ra else 'bottom'
                a['route'] = 'hv'
            else:
                a['fromSide'], a['toSide'] = ('bottom', 'top') if rb > ra else ('top', 'bottom')
                a['route'] = 'vhv'
        if g.get('text') and ka == 'decision' and not any(k in g for k in ('labelAt', 'labelDx', 'labelDy')):
            a['labelAt'] = 30
        out.append(a)
    return out


def m_stack(e):
    n, out = e.get('n', 3), []
    for k in range(n - 1, -1, -1):
        b = dict(e, t='box', x=e['x'] + k * 8, y=e['y'] - k * 8)
        b.setdefault('fill', 'soft')
        if k:
            b['id'] = f"{e['id']}~{k}"
            b.pop('text', None)
        out.append(b)
    return out


def m_cross(e):
    x, y, s = e['x'], e['y'], e.get('size', 22)
    return [{'t': 'line', 'points': p, 'color': e.get('color', 'err'), 'weight': 4}
            for p in ([[x, y], [x + s, y + s]], [[x + s, y], [x, y + s]])]


def m_check(e):
    x, y, s = e['x'], e['y'], e.get('size', 22)
    return [{'t': 'line', 'points': [[x, y + s * 0.55], [x + s * 0.38, y + s], [x + s, y]],
             'color': e.get('color', 'node'), 'weight': 4}]


def m_badge(e):
    d, c = e.get('d', 30), e.get('color', 'l4')
    # Text sits in a ghost box, not bound to the ellipse: an ellipse with bound text grows into an egg.
    return [{'t': 'ellipse', 'id': e.get('id'), 'x': e['x'], 'y': e['y'], 'w': d, 'h': d, 'color': c, 'fill': c},
            _khung({'x': e['x'] - 6, 'y': e['y'], 'w': d + 12, 'h': d, 'text': str(e['n']), 'size': e.get('size', 16),
                    'color': c})]


def m_note(e):
    s, c = e.get('size', 16), e.get('color', 'muted')
    w, h = rong_chu(e['text'], s) + 8, cao_chu(e['text'], s)
    nid = e.get('id') or f"note@{e['x']},{e['y']}"
    out = [{'t': 'text', 'x': e['x'], 'y': e['y'], 'text': e['text'], 'size': s, 'color': c},
           {'t': 'anchor', 'id': nid, 'x': e['x'] - 4, 'y': e['y'] - 2, 'w': w, 'h': h + 4}]
    if e.get('to'):
        out.append({'t': 'arrow', 'from': nid, 'to': e['to'], 'color': c, 'dashed': True, 'weight': 1,
                    'bend': e.get('bend', 0), 'toSide': e.get('toSide'), 'fromSide': e.get('fromSide')})
    return out


def m_legend(e):
    out, y = [], e['y']
    for it in e['items']:
        c = it.get('color', 'ink')
        if it.get('line'):      # `head: none` for a plain edge (tree line, ER line) so the key matches the figure
            out.append({'t': 'arrow', 'points': [[e['x'], y + 10], [e['x'] + 34, y + 10]], 'color': c,
                        'dashed': it.get('dashed'), 'head': it.get('head', 'arrow')})
        else:
            out.append({'t': it.get('shape', 'box'), 'x': e['x'] + 6, 'y': y, 'w': 22, 'h': 20, 'color': c,
                        'fill': it.get('fill'), 'fillStyle': it.get('fillStyle', 'solid'), 'dashed': it.get('dashed')})
        out.append({'t': 'text', 'x': e['x'] + 44, 'y': y - 1, 'text': it['text'], 'size': 15, 'color': 'muted'})
        y += 30
    return out


def m_db(e):
    """Cylinder: a data store."""
    x, y, w, h = e['x'], e['y'], e['w'], e['h']
    ry = min(h * 0.16, 16)
    c = e.get('color', 'ink')
    arc = [[x + w / 2 + (w / 2) * math.cos(math.radians(a)), y + h - ry + ry * math.sin(math.radians(a))]
           for a in range(0, 181, 15)]
    than = [[x + w, y + ry]] + arc + [[x, y + ry]]
    out = [{'t': 'line', 'points': than, 'closed': True, 'fill': e.get('fill', 'soft'), 'color': c,
            'fillStyle': e.get('fillStyle', 'solid'), 'weight': e.get('weight', 2), 'dashed': e.get('dashed'),
            'smooth': False},
           {'t': 'ellipse', 'x': x, 'y': y, 'w': w, 'h': ry * 2, 'color': c, 'fill': e.get('fill', 'soft'),
            'fillStyle': e.get('fillStyle', 'solid'), 'weight': e.get('weight', 2), 'dashed': e.get('dashed')},
           {'t': 'anchor', 'id': e['id'], 'x': x, 'y': y, 'w': w, 'h': h}]
    kind = e.get('kind')
    by0, bh = y + ry * 2, h - ry * 3          # free area of the body
    if kind == 'sql':                          # three stacked disks
        for k in (1, 2):
            yy = y + ry + (h - 2 * ry) * k / 3
            out.append({'t': 'line', 'color': c, 'weight': 1, 'smooth': True, 'points': [
                [x + w / 2 + (w / 2) * math.cos(math.radians(a)), yy + ry * math.sin(math.radians(a))]
                for a in range(0, 181, 20)]})
    elif kind == 'col':                        # vertical bars: columnar store
        for k in range(1, 5):
            xx = x + w * k / 5
            out.append({'t': 'line', 'color': c, 'weight': 1, 'points': [[xx, by0 + 4], [xx, by0 + bh - 2]]})
    elif kind == 'ts':                         # zigzag line: time-series
        P = [(.15, .7), (.32, .35), (.5, .6), (.68, .2), (.85, .5)]
        out.append({'t': 'line', 'color': c, 'weight': 2, 'smooth': False,
                    'points': [[x + w * px, by0 + bh * py] for px, py in P]})
    elif kind in ('doc', 'kv', 'blob', 'search', 'vector', 'graph'):
        g = {'doc': '{ }', 'kv': 'k → v', 'blob': '▲ ◆ ●', 'search': 'a-z ?', 'vector': '[.1 .7]', 'graph': 'o-o'}[kind]
        out.append(_khung({'x': x, 'y': by0, 'w': w, 'h': bh, 'text': g, 'size': 15, 'color': c}))
    if e.get('text'):
        s = e.get('size', 17)
        if kind or e.get('labelPos') == 'below':
            out.append({'t': 'text', 'x': x + w / 2 - rong_chu(e['text'], s) / 2, 'y': y + h + 6,
                        'text': e['text'], 'size': s, 'color': c})
        else:
            out.append(_khung({'x': x, 'y': by0, 'w': w, 'h': bh, 'text': e['text'], 'size': s, 'color': c}))
    return out


def m_pipe(e):
    """Horizontal pipe: stream, log, Kafka topic. segments = number of sections (partitions or batches)."""
    x, y, w, h, c = e['x'], e['y'], e['w'], e['h'], e.get('color', 'ink')
    rx = min(w * 0.08, 14)
    f = e.get('fill', 'soft')

    def cung(cx, a0, a1):
        return [[cx + rx * math.cos(math.radians(a)), y + h / 2 + (h / 2) * math.sin(math.radians(a))]
                for a in range(a0, a1 + 1, 15)]
    than = [[x + rx, y]] + [[x + w - rx, y]] + cung(x + w - rx, -90, 90) + [[x + rx, y + h]] + cung(x + rx, 90, 270)
    out = [{'t': 'line', 'points': than, 'closed': True, 'smooth': False, 'color': c, 'fill': f,
            'dashed': e.get('dashed')},
           {'t': 'ellipse', 'x': x, 'y': y, 'w': rx * 2, 'h': h, 'color': c, 'fill': f},
           {'t': 'anchor', 'id': e['id'], 'x': x, 'y': y, 'w': w, 'h': h}]
    n = e.get('segments', 0)
    for k in range(1, n):
        xx = x + rx + (w - 2 * rx) * k / n
        out.append({'t': 'line', 'color': c, 'weight': 1, 'smooth': True, 'points': cung(xx, -90, 90)})
    if e.get('text'):
        s = e.get('size', 16)
        if n or e.get('labelPos') == 'above':
            out.append({'t': 'text', 'x': x + 4, 'y': y - 26, 'text': e['text'], 'size': s, 'color': c})
        else:
            out.append(_khung({'x': x + rx * 2, 'y': y, 'w': w - rx * 3, 'h': h, 'text': e['text'], 'size': s, 'color': c}))
    return out


def m_steps(e):
    """Numbered step list, paired with the (1) (2) labels on the figure's arrows."""
    s, c, out, y = e.get('size', 16), e.get('color', 'ink'), [], e['y']
    if e.get('title'):
        out.append({'t': 'text', 'x': e['x'], 'y': y, 'text': e['title'], 'size': s, 'color': 'muted'})
        y += s * 1.7
    for i, it in enumerate(e['items']):
        txt = it if isinstance(it, str) else it['text']
        ic = c if isinstance(it, str) else it.get('color', c)
        out.append({'t': 'text', 'x': e['x'], 'y': y, 'text': f"{i + e.get('start', 1)}.", 'size': s, 'color': e.get('numColor', 'muted')})
        out.append({'t': 'text', 'x': e['x'] + s * 1.5, 'y': y, 'text': txt, 'size': s, 'color': ic})
        y += cao_chu(txt, s) + s * 0.45
    return out


def m_card(e):
    """Note card: underlined title + a few lines. For requirements, APIs, numbers placed beside the figure."""
    s, c = e.get('size', 15), e.get('color', 'l2')
    body = e.get('text', '')
    w = e.get('w') or max(rong_chu(e.get('title', ''), 17), rong_chu(body, s) * (1.17 if e.get('mono') else 1)) + 28
    h = e.get('h') or (34 if e.get('title') else 10) + cao_chu(body, s) + 14
    out = [{'t': 'box', 'id': e.get('id'), 'x': e['x'], 'y': e['y'], 'w': w, 'h': h, 'color': c,
            'fill': e.get('fill'), 'weight': 1, 'dashed': e.get('dashed')}]
    yy = e['y'] + 8
    if e.get('title'):
        out.append({'t': 'text', 'x': e['x'] + 14, 'y': yy, 'text': e['title'], 'size': 17, 'color': e.get('titleColor', c)})
        out.append({'t': 'line', 'points': [[e['x'] + 12, yy + 26], [e['x'] + w - 12, yy + 26]], 'color': c, 'weight': 1})
        yy += 34
    if body:
        out.append({'t': 'text', 'x': e['x'] + 14, 'y': yy, 'text': body, 'size': s, 'color': e.get('textColor', 'ink'),
                    'mono': e.get('mono')})
    return out


def m_queue(e):
    """Queue: horizontal tube with messages inside."""
    x, y, w, h = e['x'], e['y'], e['w'], e['h']
    c = e.get('color', 'ink')
    out = [{'t': 'box', 'id': e['id'], 'x': x, 'y': y, 'w': w, 'h': h, 'color': c, 'fill': e.get('fill', 'soft')}]
    items = e.get('items')
    if items is None:
        items = [{}] * e.get('n', 4)
    mw, pad = e.get('mw', 22), 8
    tot = len(items) * (mw + 6)
    sx = x + w - pad - tot
    for i, it in enumerate(items):
        if it is None:
            continue
        ic = it.get('color', c) if isinstance(it, dict) else it
        out.append({'t': 'box', 'x': sx + i * (mw + 6), 'y': y + 8, 'w': mw, 'h': h - 16, 'color': ic,
                    'fill': ic if ic in ACCENT else 'soft', 'fillStyle': 'hachure', 'sharp': True, 'weight': 1,
                    'text': it.get('text') if isinstance(it, dict) else None, 'size': 15})
    if e.get('text'):
        if e.get('labelPos') == 'above' or sx - x < rong_chu(e['text'], 16) + 14:
            out.append({'t': 'text', 'x': x + 4, 'y': y - 26, 'text': e['text'], 'size': 16, 'color': c})
        else:
            out.append(_khung({'x': x + 4, 'y': y, 'w': sx - x - 8, 'h': h, 'text': e['text'], 'size': 16, 'color': c}))
    return out


def m_person(e):
    x, y, h, c = e['x'], e['y'], e.get('h', 70), e.get('color', 'ink')
    w = h * 0.5
    r = h * 0.2
    cx = x + w / 2
    out = [{'t': 'ellipse', 'x': cx - r, 'y': y, 'w': 2 * r, 'h': 2 * r, 'color': c, 'fill': e.get('fill')},
           {'t': 'line', 'points': [[cx, y + 2 * r], [cx, y + h * 0.7]], 'color': c},
           {'t': 'line', 'points': [[x, y + h * 0.5], [x + w, y + h * 0.5]], 'color': c},
           {'t': 'line', 'points': [[x + 2, y + h], [cx, y + h * 0.7], [x + w - 2, y + h]], 'color': c},
           {'t': 'anchor', 'id': e['id'], 'x': x - 6, 'y': y, 'w': w + 12, 'h': h}]
    if e.get('text'):
        s = e.get('size', 16)
        out.append({'t': 'text', 'x': cx - rong_chu(e['text'], s) / 2, 'y': y + h + 6, 'text': e['text'],
                    'size': s, 'color': c})
    return out


def m_cloud(e):
    x, y, w, h, c = e['x'], e['y'], e['w'], e['h'], e.get('color', 'ink')
    P = [(.18, .82), (.05, .62), (.12, .38), (.28, .32), (.36, .12), (.56, .08), (.68, .26), (.86, .28),
         (.96, .5), (.88, .76), (.7, .84), (.5, .92), (.3, .88)]
    out = [{'t': 'line', 'points': [[x + px * w, y + py * h] for px, py in P], 'closed': True, 'smooth': True,
            'color': c, 'fill': e.get('fill', 'soft'), 'dashed': e.get('dashed')},
           {'t': 'anchor', 'id': e['id'], 'x': x + w * .05, 'y': y + h * .1, 'w': w * .9, 'h': h * .8, 'shape': 'ellipse'}]
    if e.get('text'):
        out.append(_khung({'x': x + w * .15, 'y': y + h * .3, 'w': w * .7, 'h': h * .5, 'text': e['text'],
                           'size': e.get('size', 17), 'color': c}))
    return out


def m_doc(e):
    x, y, w, h, c = e['x'], e['y'], e['w'], e['h'], e.get('color', 'ink')
    k = min(w, h) * 0.26
    out = [{'t': 'line', 'points': [[x, y], [x + w - k, y], [x + w, y + k], [x + w, y + h], [x, y + h]],
            'closed': True, 'color': c, 'fill': e.get('fill', 'soft')},
           {'t': 'line', 'points': [[x + w - k, y], [x + w - k, y + k], [x + w, y + k]], 'color': c},
           {'t': 'anchor', 'id': e['id'], 'x': x, 'y': y, 'w': w, 'h': h}]
    if e.get('text'):
        out.append(_khung({'x': x, 'y': y + k * 0.6, 'w': w, 'h': h - k * 0.6, 'text': e['text'],
                           'size': e.get('size', 16), 'color': c}))
    return out


def m_window(e):
    """Browser window or app screen: a client with a UI."""
    x, y, w, h, c = e['x'], e['y'], e['w'], e['h'], e.get('color', 'ink')
    out = [{'t': 'box', 'id': e['id'], 'x': x, 'y': y, 'w': w, 'h': h, 'color': c, 'fill': e.get('fill')},
           {'t': 'line', 'points': [[x, y + 24], [x + w, y + 24]], 'color': c, 'weight': 1}]
    for i in range(3):
        out.append({'t': 'ellipse', 'x': x + 10 + i * 14, 'y': y + 8, 'w': 8, 'h': 8, 'color': c, 'weight': 1})
    if e.get('title'):
        out.append({'t': 'text', 'id': f"{e['id']}.title", 'x': x + 60, 'y': y + 3, 'text': e['title'], 'size': 15,
                    'color': 'muted'})
    if e.get('text'):
        out.append(_khung({'x': x, 'y': y + 24, 'w': w, 'h': h - 24, 'text': e['text'], 'size': e.get('size', 16),
                           'color': c}))
    return out


def m_group(e):
    """Shift a whole cluster by (dx,dy); dim=true turns it muted so it backs the new parts."""
    out = []
    for c in bung(e['elements']):
        c = copy.deepcopy(c)
        dx, dy = e.get('dx', 0), e.get('dy', 0)
        for k in ('x', 'x1', 'x2', 'cx'):
            if k in c:
                c[k] += dx
        for k in ('y', 'cy'):
            if k in c:
                c[k] += dy
        if 'points' in c:
            c['points'] = [[p[0] + dx, p[1] + dy] for p in c['points']]
        if c.get('t') == 'raw':                    # icons: raw Excalidraw elements carry their own x/y and colours
            for r in c['elements']:
                r['x'], r['y'] = r.get('x', 0) + dx, r.get('y', 0) + dy
                if e.get('dim') and r.get('strokeColor') not in (None, 'transparent'):
                    r['strokeColor'] = MAU['muted']
        if e.get('dim'):
            c['color'] = 'muted'
            if c.get('fill') and c['fill'] != 'code':
                c['fill'] = 'soft'
        if e.get('prefix'):
            for k in ('id', 'from', 'to'):
                if c.get(k):
                    c[k] = e['prefix'] + c[k]
        out.append(c)
    return out


def m_row(e):
    """Lay child elements out in an evenly spaced row (or column): no hand-computed x,y."""
    col, gap = e['t'] == 'col', e.get('gap', 60)
    chay, out = (e['y'] if col else e['x']), []
    kids = e['elements']
    lon = max(k.get('w' if col else 'h', 0) for k in kids)
    for k in kids:
        k = dict(k)
        if col:
            k['y'] = chay
            k['x'] = e['x'] + (lon - k.get('w', 0)) / 2 if e.get('align', 'center') == 'center' else e['x']
            chay += k.get('h', 0) + gap
        else:
            k['x'] = chay
            k['y'] = e['y'] + (lon - k.get('h', 0)) / 2 if e.get('align', 'center') == 'center' else e['y']
            chay += k.get('w', 0) + gap
        out.append(k)
    return bung(out)


_ICONS = None
LIBS = []


def _nap_icon():
    global _ICONS
    if _ICONS is None:
        _ICONS = {}
        f = SKILL / 'assets' / 'icons.json'
        if f.exists():
            _ICONS.update(json.loads(f.read_text(encoding='utf-8')))
        for lib in LIBS:
            d = json.loads(pathlib.Path(lib).read_text(encoding='utf-8', errors='replace'))
            items = d.get('libraryItems') or [{'elements': x, 'name': ''} for x in d.get('library', [])]
            for i, it in enumerate(items):
                els = [x for x in it.get('elements', []) if not x.get('isDeleted')]
                if els:
                    _ICONS[(it.get('name') or f'#{i}').strip().lower()] = {'elements': els, 'src': str(lib)}
    return _ICONS


def m_icon(e):
    ic = _nap_icon().get(e['name'].strip().lower())
    if not ic:
        chet(f"icon '{e['name']}' does not exist. Run `ve.py --icons` to list icons.")
    els = [copy.deepcopy(x) for x in ic['elements'] if x.get('type') in ('rectangle', 'ellipse', 'diamond', 'line', 'arrow')
           or (e.get('keepText') and x.get('type') == 'text')]
    # A line's extent is its points, not x + width: library lines often run leftward or upward
    # (negative points), and x + width then overshoots, which shrank the icon and pushed its label off-centre.
    def _ext(x, i, wh):
        if x.get('points'):
            return [x['xy'[i]] + p[i] for p in x['points']]
        return [x['xy'[i]], x['xy'[i]] + abs(x.get(wh, 0))]
    x0 = min(min(_ext(x, 0, 'width')) for x in els)
    y0 = min(min(_ext(x, 1, 'height')) for x in els)
    x1 = max(max(_ext(x, 0, 'width')) for x in els)
    y1 = max(max(_ext(x, 1, 'height')) for x in els)
    w0, h0 = max(x1 - x0, 1), max(y1 - y0, 1)
    s = e['w'] / w0 if e.get('w') else e.get('h', 56) / h0
    w, h = w0 * s, h0 * s
    c = e.get('color', 'ink')
    raw = []
    for k, x in enumerate(els):
        x['x'] = e['x'] + (x['x'] - x0) * s
        x['y'] = e['y'] + (x['y'] - y0) * s
        x['width'] = x.get('width', 0) * s
        x['height'] = x.get('height', 0) * s
        if 'points' in x:
            x['points'] = [[p[0] * s, p[1] * s] for p in x['points']]
        if 'fontSize' in x:
            x['fontSize'] = max(x['fontSize'] * s, 10)
        if str(x.get('strokeColor')).lower() != 'transparent':
            x['strokeColor'] = mau(c)
        bg = str(x.get('backgroundColor', 'transparent')).lower()
        if bg != 'transparent':
            x['backgroundColor'] = nen(e.get('fill', 'soft'))
            x['fillStyle'] = x.get('fillStyle') if x.get('fillStyle') in ('solid', 'hachure', 'cross-hatch') else 'solid'
        x['strokeWidth'] = min(max(x.get('strokeWidth', 2) * (s ** 0.5), 1), 2)
        x['roughness'] = 1
        x['opacity'] = 100
        x.update(groupIds=[], frameId=None, boundElements=None, link=None, locked=False,
                 startBinding=None, endBinding=None)
        x['_k'] = k
        raw.append(x)
    out = [{'t': 'raw', 'elements': raw}, {'t': 'anchor', 'id': e.get('id') or f"icon@{e['x']},{e['y']}",
                                           'x': e['x'], 'y': e['y'], 'w': w, 'h': h}]
    if e.get('text'):
        sz = e.get('size', 16)
        # centred per line, so a two-line "service\nrole" label (the AWS icon rule) stays under the icon
        out.append({'t': 'text', 'x': e['x'] + w / 2, 'y': e['y'] + h + 6, 'align': 'center',
                    'text': e['text'], 'size': sz, 'color': c})
    return out


MACRO = {'frame': m_frame, 'cells': m_cells, 'grid': m_grid, 'table': m_table, 'entity': m_entity,
         'code': m_code, 'axis': m_axis, 'span': m_span, 'plot': m_plot, 'sequence': m_sequence,
         'tree': m_tree, 'ring': m_ring, 'lanes': m_lanes, 'swimlane': m_swimlane, 'start': m_start, 'end': m_end, 'stack': m_stack, 'cross': m_cross,
         'check': m_check, 'badge': m_badge, 'note': m_note, 'legend': m_legend, 'db': m_db,
         'queue': m_queue, 'pipe': m_pipe, 'steps': m_steps, 'card': m_card, 'person': m_person, 'cloud': m_cloud, 'doc': m_doc, 'window': m_window,
         'group': m_group, 'row': m_row, 'col': m_row, 'icon': m_icon}
GOC = SHAPES + ('arrow', 'line', 'text', 'anchor', 'raw')


def bung(els):
    out = []
    for i, e in enumerate(els):
        t = e.get('t')
        if t in MACRO:
            try:
                out.extend(bung(MACRO[t](e)))
            except KeyError as k:
                chet(f"element {i} (t='{t}'): missing property {k}. See references/spec.md")
        elif t in GOC:
            out.append(e)
        else:
            chet(f"element {i}: t='{t}' is not supported. Available: {' '.join(GOC[:6])} {' '.join(MACRO)}")
    return out


def nap(path, seen=()):
    """Read a spec and resolve `extends` (progressively built figures)."""
    path = pathlib.Path(path).resolve()
    if path in seen:
        chet(f'circular extends at {path.name}')
    spec = json.loads(path.read_text(encoding='utf-8'))
    els = spec.get('elements', [])
    if spec.get('extends'):
        goc = nap(path.parent / spec['extends'], seen + (path,))
        bo = set(spec.get('remove', []))
        base = [x for x in goc if x.get('id') not in bo]
        if spec.get('dimBase', True):
            base = [{'t': 'group', 'dim': True, 'elements': base}]
        els = base + els
    return els


# ───────────────────────── build skeleton ─────────────────────────
HEAD = {'arrow': 'arrow', 'triangle': 'triangle', 'dot': 'circle', 'bar': 'bar', 'none': None,
        'one': 'crowfoot_one', 'many': 'crowfoot_many', 'one-many': 'crowfoot_one_or_many',
        'zero-one': 'crowfoot_one', 'zero-many': 'crowfoot_many',
        'inherit': 'triangle_outline', 'compose': 'diamond', 'aggregate': 'diamond_outline', 'circle': 'circle_outline'}


HACH_HEP = 30        # a hachure shape whose short side is under this many units counts as narrow


def _hachure_ro(e, o):
    """Make a hachure fill visible where Excalidraw's own one is not.
    Excalidraw draws hachure lines in the backgroundColor (a pale `fill-*` tint), 1 unit thick, 8 apart
    (hachureGap = 4 × strokeWidth, not settable per element). `soft` is so close to the page that its lines vanish
    at any width, and a narrow empty cell (cw 13-24) gets two or three tint lines and reads as an empty cell
    (sd01 run: 27 cells at cw 13; hang-doi 2.1: cw 18 queue cells; hang-doi 3.3 run).
    Fix: `soft` hachure lines use the `line` token; a narrow shape with no text gets its lines from an under-layer
    (id `<id>~hach`, no stroke, strokeWidth 1.5 so the gap is 6) in the saturated token of its fill at 55% opacity, and the shape itself keeps only
    its outline, so the outline stays at full strength. Text-bearing cells keep the tint: their glyphs already fill
    them, and saturated lines behind them would cut into the letters.
    Returns the under-layer element to draw first, or None."""
    f = e['fill']
    if f == 'soft':
        o['backgroundColor'] = MAU['line']
        return None
    if min(e['w'], e['h']) < HACH_HEP and not e.get('text') and f in MAU:
        u = {k: v for k, v in o.items() if k != 'label'}
        u.update(id=f"{o['id']}~hach", strokeColor='transparent', backgroundColor=MAU[f], opacity=55,
                 strokeWidth=1.5)          # stroke is invisible here: 1.5 only sets the gap to 6 and the line to 0.75
        o['backgroundColor'] = 'transparent'
        return u
    return None


def dung(spec_els):
    els = bung(spec_els)
    hinh = {}
    for e in els:
        if e['t'] in SHAPES + ('anchor',) and e.get('id'):
            if e['id'] in hinh and e['t'] != 'anchor':
                chet(f"duplicate id '{e['id']}'")
            hinh.setdefault(e['id'], e)
    out, raw, lint_arrows = [], [], []
    duoi = [e for e in els if e.get('under')]
    for i, e in enumerate(duoi + [e for e in els if not e.get('under')]):
        t = e['t']
        if t == 'anchor':
            continue
        if t == 'raw':
            raw.extend(e['elements'])
            continue
        c = mau(e.get('color', 'ink'))
        chung = {'strokeColor': 'transparent' if e.get('ghost') else c, 'strokeWidth': e.get('weight', 2),
                 'roughness': e.get('rough', 1), 'opacity': e.get('opacity', 100),
                 'strokeStyle': 'dashed' if e.get('dashed') else ('dotted' if e.get('dotted') else 'solid')}
        if t in SHAPES:
            o = {'type': {'box': 'rectangle'}.get(t, t), 'id': e.get('id') or f'_s{i}', 'x': e['x'], 'y': e['y'],
                 'width': e['w'], 'height': e['h'], 'backgroundColor': nen(e.get('fill')),
                 'fillStyle': e.get('fillStyle', 'solid'), **chung}
            if t == 'box':
                o['roundness'] = None if e.get('sharp') else {'type': 3}
            if e.get('text'):
                o['label'] = {'text': str(e['text']), 'fontSize': e.get('size', 20), 'strokeColor': c,
                              'textAlign': e.get('align', 'center'), 'verticalAlign': e.get('valign', 'middle')}
            if o['fillStyle'] in ('hachure', 'cross-hatch') and e.get('fill') and not e.get('ghost'):
                u = _hachure_ro(e, o)
                if u:
                    out.append(u)
            out.append(o)
        elif t in ('arrow', 'line'):
            if 'points' in e:
                pts = [tuple(p) for p in e['points']]
                if t == 'arrow':                           # free-routed arrows get the same crossing check
                    lint_arrows.append((None, None, pts, _dau(e)))
            else:
                for k in ('from', 'to'):
                    if e.get(k) not in hinh:
                        if any(x['t'] == 'text' and x.get('id') == e.get(k) for x in els):   # dbi4 run
                            chet(f"arrow {i}: {k}='{e.get(k)}' is a free `text`, which is not an arrow target: "
                                 f"draw the arrow with `points` ending about 6 units short of the text, or make it a box")
                        chet(f"arrow {i}: {k}='{e.get(k)}' matches no id. Existing ids: {' '.join(sorted(hinh))[:300]}")
                a, b = hinh[e['from']], hinh[e['to']]
                if e['from'] == e['to']:                       # self-loop: loop at the top-right corner
                    x, y, w = a['x'], a['y'], a['w']
                    pts = [(x + w * .62, y - 4), (x + w * .7, y - 34), (x + w + 30, y - 30), (x + w + 34, y + 6),
                           (x + w + 6, y + a['h'] * .3)]
                else:
                    ca, cb = tam(a), tam(b)
                    # a pinned end (side + At) is what the free end aims at, not the other shape's centre:
                    # aiming at the centre turned a row-level arrow into a slope toward a tall target (td5 run)
                    p = mep(a, e['fromSide'], e.get('fromAt', .5)) if e.get('fromSide') else None
                    q = mep(b, e['toSide'], e.get('toAt', .5)) if e.get('toSide') else None
                    if p is None:
                        p = cat(a, *(q or cb))
                    if q is None:
                        q = cat(b, *p) if e.get('fromSide') else cat(b, *ca)
                    r = e.get('route')
                    if r in ('hv', 'vh', 'hvh', 'vhv'):
                        if r == 'hv':
                            mid = [(q[0], p[1])]
                        elif r == 'vh':
                            mid = [(p[0], q[1])]
                        elif r == 'hvh':
                            mx = (p[0] + q[0]) / 2 + e.get('shift', 0)
                            mid = [(mx, p[1]), (mx, q[1])]
                        else:
                            my = (p[1] + q[1]) / 2 + e.get('shift', 0)
                            mid = [(p[0], my), (q[0], my)]
                        p, q = lui(p, mid[0]), lui(q, mid[-1])
                        pts = [p] + mid + [q]
                        e = dict(e, sharp=True)
                    else:
                        p, q = lui(p, q), lui(q, p)
                        pts = [p, q]
                        if e.get('bend'):
                            L = math.hypot(q[0] - p[0], q[1] - p[1]) or 1
                            nx, ny = -(q[1] - p[1]) / L, (q[0] - p[0]) / L
                            pts = [p, ((p[0] + q[0]) / 2 + nx * e['bend'], (p[1] + q[1]) / 2 + ny * e['bend']), q]
                    lint_arrows.append((e.get('from'), e.get('to'), pts, _dau(e)))
            if e.get('id') and t == 'arrow':            # arrow with an id: a note can point at its middle
                mx, my = pts[len(pts) // 2] if len(pts) > 2 else ((pts[0][0] + pts[1][0]) / 2, (pts[0][1] + pts[1][1]) / 2)
                hinh[e['id']] = {'t': 'anchor', 'id': e['id'], 'x': mx - 8, 'y': my - 8, 'w': 16, 'h': 16}
            x0, y0 = pts[0]
            o = {'type': t, 'id': e.get('id') or f'_{t}{i}', 'x': x0, 'y': y0,
                 'points': [[px - x0, py - y0] for px, py in pts], **chung}
            cong = e.get('smooth', len(pts) > 2 and not e.get('sharp') and not e.get('closed'))
            o['roundness'] = {'type': 2} if cong else None
            if t == 'line' and e.get('closed'):
                o['points'].append([0, 0])
                o['backgroundColor'] = nen(e.get('fill'))
                o['fillStyle'] = e.get('fillStyle', 'solid')
            if t == 'arrow':
                for k in ('head', 'tail'):
                    if e.get(k) is not None and e[k] not in HEAD:
                        chet(f"arrow {i}: {k}='{e[k]}' is not a head name. Use: {' '.join(HEAD)}")
                o['endArrowhead'] = HEAD.get(e.get('head', 'arrow'), 'arrow')
                o['startArrowhead'] = HEAD.get(e.get('tail', 'arrow' if e.get('both') else 'none'))
                tu_do = any(k in e for k in ('labelAt', 'labelDx', 'labelDy'))
                if e.get('text') and not tu_do:
                    o['label'] = {'text': str(e['text']), 'fontSize': e.get('size', 16), 'strokeColor': c}
            out.append(o)
            # Excalidraw dashes the arrowheads of a dashed arrow too, which cuts an ER bar or crow into stubs
            # (`td5-quan-sat-hai-duong-ve-benh-nhan`, a FK-less column drawn dashed). Keep the line dashed but
            # draw each ER end on its own short solid segment laid over the last 40 units.
            ER_ENDS = ('one', 'many', 'one-many', 'zero-one', 'zero-many')
            ve_lien = t == 'arrow' and chung['strokeStyle'] != 'solid'
            for k, (tip, prev) in (('head', (pts[-1], pts[-2])), ('tail', (pts[0], pts[1]))):
                if ve_lien and e.get(k) in ER_ENDS:
                    L = math.hypot(tip[0] - prev[0], tip[1] - prev[1]) or 1
                    s = min(40, L)
                    p = (tip[0] + (prev[0] - tip[0]) / L * s, tip[1] + (prev[1] - tip[1]) / L * s)
                    a0, a1 = (p, tip) if k == 'head' else (tip, p)
                    o['endArrowhead' if k == 'head' else 'startArrowhead'] = None
                    out.append({'type': 'arrow', 'id': f'_erend{i}{k}', 'x': a0[0], 'y': a0[1],
                                'points': [[0, 0], [a1[0] - a0[0], a1[1] - a0[1]]], 'roundness': None,
                                'endArrowhead': HEAD[e[k]] if k == 'head' else None,
                                'startArrowhead': HEAD[e[k]] if k == 'tail' else None, **dict(chung, strokeStyle='solid')})
            # Excalidraw has no "zero" crow's foot end: draw the hollow ring of the minimum
            # (zero-one, zero-many) beyond the bar or the crow, filled with the page so the line stops at it.
            # The ring is always solid: a dashed ring reads as a broken "c".
            for k, (tip, prev) in (('head', (pts[-1], pts[-2])), ('tail', (pts[0], pts[1]))):
                if t == 'arrow' and e.get(k) in ('zero-one', 'zero-many'):
                    L = math.hypot(tip[0] - prev[0], tip[1] - prev[1]) or 1
                    d = min(20, L * .5) + (14 if e[k] == 'zero-one' else 10)
                    cx, cy = tip[0] + (prev[0] - tip[0]) / L * d, tip[1] + (prev[1] - tip[1]) / L * d
                    out.append({'type': 'ellipse', 'id': f'_zero{i}{k}', 'x': cx - 6, 'y': cy - 6, 'width': 12,
                                'height': 12, 'backgroundColor': MAU['paper'], 'fillStyle': 'solid',
                                **dict(chung, strokeStyle='solid')})
            if t == 'arrow' and e.get('text') and tu_do:      # detached label: placed by distance along the arrow
                segs = [(pts[k], pts[k + 1], math.hypot(pts[k + 1][0] - pts[k][0], pts[k + 1][1] - pts[k][1]))
                        for k in range(len(pts) - 1)]
                tong = sum(sg[2] for sg in segs) or 1
                at = e.get('labelAt', 0.5)
                con = at * tong if at <= 1 else min(at, tong)
                for p0, p1, L in segs:
                    if con <= L or (p0, p1, L) == segs[-1]:
                        f = con / (L or 1)
                        lx, ly = p0[0] + (p1[0] - p0[0]) * f, p0[1] + (p1[1] - p0[1]) * f
                        ngang = abs(p1[0] - p0[0]) >= abs(p1[1] - p0[1])
                        break
                    con -= L
                sz = e.get('size', 16)
                tw, th = rong_chu(e['text'], sz), cao_chu(e['text'], sz)
                dx = e.get('labelDx', 0 if ngang else tw / 2 + 8)
                dy = e.get('labelDy', -(th / 2 + 3) if ngang else 0)
                out.append({'type': 'text', 'id': f'_lab{i}', 'x': lx + dx, 'y': ly + dy - th / 2, 'text': str(e['text']),
                            'fontSize': sz, 'strokeColor': c, 'textAlign': 'center', 'opacity': e.get('opacity', 100)})
        elif t == 'text':
            o = {'type': 'text', 'id': e.get('id') or f'_text{i}', 'x': e['x'], 'y': e['y'], 'text': str(e['text']),
                 'fontSize': e.get('size', 20), 'strokeColor': c, 'textAlign': e.get('align', 'left'),
                 'opacity': e.get('opacity', 100)}
            if e.get('mono'):
                o['_mono'] = True
            out.append(o)
    # Amber text fails the site gate: --warn on --card is 2.44:1 in the light theme (threshold 3:1,
    # tools/contrast.py). Strokes and fills keep warn; only the glyphs drop to ink.
    for o in out + raw:
        lab = o.get('label') if isinstance(o.get('label'), dict) else None
        for t in ([o] if o.get('type') == 'text' else []) + ([lab] if lab else []):
            if str(t.get('strokeColor', '')).lower() == MAU['warn'].lower():
                t['strokeColor'] = MAU['ink']
    return out, raw, hinh, lint_arrows, els


# ───────────────────────── lint ─────────────────────────
def _cat_doan_hcn(p, q, r, co=6):
    """Whether segment p-q passes through rectangle r (shrunk inward by `co` units)."""
    x0, y0, x1, y1 = r['x'] + co, r['y'] + co, r['x'] + r['w'] - co, r['y'] + r['h'] - co
    if x1 <= x0 or y1 <= y0:
        return False
    dx, dy = q[0] - p[0], q[1] - p[1]
    t0, t1 = 0.0, 1.0
    for d, a, b in ((dx, x0 - p[0], x1 - p[0]), (dy, y0 - p[1], y1 - p[1])):
        if abs(d) < 1e-9:
            if a > 0 or b < 0:
                return False
        else:
            ta, tb = a / d, b / d
            if ta > tb:
                ta, tb = tb, ta
            t0, t1 = max(t0, ta), min(t1, tb)
            if t0 > t1:
                return False
    return t1 - t0 > 0.02


def _dau(e):
    """Number of drawn arrowheads (0-2) on an arrow spec."""
    return int(e.get('head', 'arrow') != 'none') + int(e.get('tail', 'arrow' if e.get('both') else 'none') != 'none')


def soat(conv, hinh, lint_arrows, goc, sk=()):
    cung, nhac = [], []
    by = {e['id']: e for e in conv}
    # 0 · Excalidraw silently GROWS a shape when its text does not fit: the layout shifts with no warning
    for s in sk:
        c = by.get(s.get('id'))
        if c and s.get('label') and s['type'] in ('rectangle', 'ellipse', 'diamond') and s.get('strokeColor') != 'transparent':
            if c['width'] > s['width'] + 2 or c['height'] > s['height'] + 2:
                # Same width, taller: the text WRAPPED, so a larger h (or `ch`) never helps (dbi2 run: 2-digit keys in cw 28)
                t, fs = s['label']['text'], s['label'].get('fontSize', 20)
                # Wrapped = Excalidraw's bound text has MORE lines than the spec text. The old test guessed it from
                # cao_chu (1.25 line height) while Excalidraw lays Nunito out at 1.35, so two lines at size 15 in h 48
                # were called "wrapped" and told to widen a box that only needed 3 more units of height (sd53 run).
                bt = next((e for e in conv if e['type'] == 'text' and e.get('containerId') == c['id']), None)
                quan = bt is not None and bt['text'].count('\n') > t.count('\n')
                if c['width'] <= s['width'] + 2 and quan:
                    fix = (f"the text wrapped, so widen it, not heighten it: `w` (`cw` in a cells strip) at least "
                           f"chars × size × 0.52 + 16 = {rong_chu(t, fs) + 16:.0f}")
                elif c['width'] <= s['width'] + 2:
                    fix = (f"the text did not wrap, the box is too short for its lines: `h` (`ch`) at least "
                           f"lines × size × 1.35 + 11 = {(t.count(chr(10)) + 1) * fs * 1.35 + 11:.0f}")
                else:
                    fix = "set a larger w/h (diamond and ellipse need twice the text width)"
                cung.append(f"shape '{s['id']}' grew from {s['width']:.0f}×{s['height']:.0f} to {c['width']:.0f}×{c['height']:.0f} "
                            f"because text “{s['label']['text'][:20]}” does not fit: {fix}")
    # 1 · text overflows the shape that contains it
    for e in conv:
        if e['type'] == 'text' and e.get('containerId') and e['containerId'] in by:
            c = by[e['containerId']]
            if c['type'] in ('rectangle', 'ellipse', 'diamond') and c.get('strokeColor') != 'transparent':
                he = {'rectangle': 1.0, 'ellipse': 0.72, 'diamond': 0.52}[c['type']]
                if e['width'] > c['width'] * he + 2 or e['height'] > c['height'] * he + 2:
                    cung.append(f"text “{e['text'][:28]}” overflows its shape: enlarge the shape's w/h, do not shrink the font")
    # 2 · arrow passes through a shape that is not one of its two ends
    than = [h for h in hinh.values() if h['t'] in SHAPES and not h.get('ghost') and not h.get('under')
            and '~' not in str(h.get('id'))]
    for a, b, pts, dau in lint_arrows:
        if a is None:                       # `points` arrow: its ends are the two points, not two shapes
            A = {'x': pts[0][0], 'y': pts[0][1], 'w': 0, 'h': 0}
            B = {'x': pts[-1][0], 'y': pts[-1][1], 'w': 0, 'h': 0}
            a, b = f"({pts[0][0]:.0f},{pts[0][1]:.0f})", f"({pts[-1][0]:.0f},{pts[-1][1]:.0f})"
        else:
            A, B = hinh[a], hinh[b]
        dai = sum(math.hypot(pts[k + 1][0] - pts[k][0], pts[k + 1][1] - pts[k][1]) for k in range(len(pts) - 1))
        if a != b and dai < (22 if dau < 2 else 64):     # two heads (`both`, a `tail`) need room for a visible shaft: 36- and 50-long `both` arrows read as a diamond (aws1)
            nhac.append(f"arrow {a} → {b} is only {dai:.0f} long for {dau} head(s), the heads hide the line: move the two shapes apart")
        for h in than:
            if h is A or h is B:
                continue
            chua = lambda o: (h['x'] - 4 <= o['x'] and h['y'] - 4 <= o['y'] and h['x'] + h['w'] + 4 >= o['x'] + o['w']
                              and h['y'] + h['h'] + 4 >= o['y'] + o['h'])
            if chua(A) or chua(B):          # enclosing frame, or the shape a `points` arrow starts or ends on
                continue
            if any(_cat_doan_hcn(pts[k], pts[k + 1], h) for k in range(len(pts) - 1)):
                nhac.append(f"arrow {a} → {b} crosses shape '{h.get('id')}': use bend, route, or move the shape")
                break
    # 2a · one arrow's head lands where another arrow starts: in and out share a spot and read as one line crossing
    #      the shape (A6 roadmap, `ba6-duong-mac-dinh-14-chang`). Axes sharing an origin and a pair a→b, b→a are fine.
    for i, (a1, b1, p1, _) in enumerate(lint_arrows):
        for j, (a2, b2, p2, _) in enumerate(lint_arrows):
            if i == j or len(p1) < 2 or len(p2) < 2 or (a1 is not None and a1 == b2 and b1 == a2):
                continue
            (hx, hy), (sx, sy) = p1[-1], p2[0]
            if math.hypot(hx - sx, hy - sy) < 6:
                nhac.append(f"an arrow ends where another starts ({hx:.0f},{hy:.0f}): give one of them fromAt/toAt "
                            f"or another side so each end has its own spot")
    # 2d · two arrows leave (or reach) the same spot in the same direction: their first (last) segments lie on one
    #      stroke, so a fork reads as one line that splits later, or not at all (DBI3 hero run: swimlane edges
    #      ② → ③ (vhv) and ② → T50 (straight down) both left the bottom centre of ② and shared 30 units).
    def _dir(p, q):
        L = math.hypot(q[0] - p[0], q[1] - p[1])
        return ((q[0] - p[0]) / L, (q[1] - p[1]) / L, L) if L else (0, 0, 0)
    for i, (a1, b1, p1, _) in enumerate(lint_arrows):
        for j in range(i + 1, len(lint_arrows)):
            a2, b2, p2, _ = lint_arrows[j]
            if len(p1) < 2 or len(p2) < 2:
                continue
            for k1, k2, n1, n2, ten in ((p1[0], p2[0], p1[1], p2[1], 'leave'), (p1[-1], p2[-1], p1[-2], p2[-2], 'reach')):
                ux, uy, l1 = _dir(k1, n1)
                vx, vy, l2 = _dir(k2, n2)
                if math.hypot(k1[0] - k2[0], k1[1] - k2[1]) < 6 and ux * vx + uy * vy > 0.985 and min(l1, l2) > 12:
                    nhac.append(f"arrows {a1} → {b1} and {a2} → {b2} {ten} ({k1[0]:.0f},{k1[1]:.0f}) in the same direction and "
                                f"share {min(l1, l2):.0f} units of stroke: give one fromAt/toAt or another side")
    # 2b · label longer than the arrow carrying it: the text will cover the shapes at both ends.
    #      Measured ALONG the arrow: on a vertical arrow the label's height eats the line, not its width
    #      (FE25 SPSC run: a 164-wide label on a 160-long vertical arrow left 140 units of line and was flagged).
    for e in conv:
        if e['type'] == 'text' and e.get('containerId') and by.get(e['containerId'], {}).get('type') == 'arrow':
            ar = by[e['containerId']]
            dai = math.hypot(ar['width'], ar['height'])
            doc = e['width'] * ar['width'] / dai + e['height'] * ar['height'] / dai if dai else e['width']
            if doc > dai - 14:
                nhac.append(f"label “{e['text'][:24]}” spans {doc:.0f} along an arrow only {dai:.0f} long, no room left for the line: "
                            f"move the two shapes apart, shorten the label, or make it a note")
    # 2c · an arrowhead straddles the border of a box it does not land on: the head ends a few units inside an
    #      enclosing frame, so the border cuts the head in two (DBI3 O2N/N2O run: roll_ptr head 14 units inside
    #      the undo-log frame). A head that ends ON a border is the target (or the strip holding it): skipped.
    for a, b, pts, dau in lint_arrows:
        ends = ([(pts[-1], pts[-2])] if dau >= 1 else []) + ([(pts[0], pts[1])] if dau >= 2 else [])
        for (px, py), (qx, qy) in ends:
            L = math.hypot(qx - px, qy - py) or 1
            # base of the drawn head: Excalidraw's arrow head is ~25 units plus the rough stroke, so a border 22
            # units behind the tip still cut it while a 20-unit probe stayed inside (infra2 hero run); a short
            # arrow's head never reaches past its own start
            d = min(26, L)
            hb = (px + (qx - px) * d / L, py + (qy - py) * d / L)
            for h in than:
                if h['t'] != 'box' or h.get('id') in (a, b):
                    continue
                x0, y0, x1, y1 = h['x'], h['y'], h['x'] + h['w'], h['y'] + h['h']
                trong = lambda x, y: x0 < x < x1 and y0 < y < y1
                bien = min(abs(px - x0), abs(px - x1), abs(py - y0), abs(py - y1))
                if bien > 2 and trong(px, py) != trong(*hb):
                    nhac.append(f"the arrowhead at ({px:.0f},{py:.0f}) is cut by the border of '{h.get('id')}' "
                                f"{bien:.0f} units away: move that border 30+ units clear of the tip, or move the head")
                    break
    # 3 · free text overlaps other text or cuts a shape border
    free =[e for e in conv if e['type'] == 'text' and not e.get('containerId')]
    alltext = [e for e in conv if e['type'] == 'text']

    def giao(p, q):
        w = min(p['x'] + p['width'], q['x'] + q['width']) - max(p['x'], q['x'])
        h = min(p['y'] + p['height'], q['y'] + q['height']) - max(p['y'], q['y'])
        return max(w, 0) * max(h, 0)

    seen = set()
    for f in free:
        for o in alltext:
            if o is f or (o['id'], f['id']) in seen:
                continue
            if giao(f, o) > 0.18 * min(f['width'] * f['height'], o['width'] * o['height']):
                seen.add((f['id'], o['id']))
                nhac.append(f"text “{f['text'][:22]}” overlaps text “{o['text'][:22]}”")
        for s in conv:
            if s['type'] != 'rectangle' or s.get('strokeColor') == 'transparent':   # ellipse/diamond: the bounding box is not the real border
                continue
            g, dt = giao(f, s), f['width'] * f['height']
            if 0.12 * dt < g < 0.88 * dt:
                # an auto id (`_s2`: swimlane or lanes background, frame of a macro) names nothing the author wrote,
                # so give its box: the DBI3 hero note sat under a swimlane whose bottom edge was not in the spec
                bx = (f" (box x {s['x']:.0f}-{s['x'] + s['width']:.0f}, y {s['y']:.0f}-{s['y'] + s['height']:.0f})"
                      if str(s['id']).startswith('_') else '')
                nhac.append(f"text “{f['text'][:22]}” straddles the border of shape '{s['id']}'{bx}")
            elif g >= 0.88 * dt and s['width'] >= 3 * f['width'] and s['height'] >= 3 * f['height'] \
                    and not str(f['id']).startswith(f"{s['id']}."):
                # inside a frame-sized shape but touching its edge: a two-line note ended 2.5 units above a frame's
                # bottom, so the rough stroke ran through its descenders and the straddle test stayed silent (sd03 run).
                # A shape's own parts (a window's title bar text, id `<window>.title`) and shapes under 3x the
                # text (a label in a small box) are placed by design.
                ke = min(f['x'] - s['x'], f['y'] - s['y'], s['x'] + s['width'] - f['x'] - f['width'],
                         s['y'] + s['height'] - f['y'] - f['height'])
                if -1 < ke < 4:
                    nhac.append(f"text “{f['text'][:22]}” touches the border of shape '{s['id']}' "
                                f"({ke:.0f} units inside): keep 6+ units clear")
    # 3a · a label touching the hollow ring of a `zero-one`/`zero-many` end: the ring sits 24-34 units inside the
    #      arrow, so a verb label centred on a short ER edge lands on it (`td4-variant-giu-gia-va-ton-kho`).
    #      3 units of clearance: a box that only touches the ring still reads as text sitting on it.
    for r in (e for e in conv if e['type'] == 'ellipse' and str(e.get('id', '')).startswith('_zero')):
        vong = {'x': r['x'] - 3, 'y': r['y'] - 3, 'width': r['width'] + 6, 'height': r['height'] + 6}
        for f in alltext:
            if giao(f, vong) > 0:
                nhac.append(f"label “{f['text'][:22]}” touches the ring of a zero-one/zero-many end: "
                            f"raise it with labelDy, slide it with labelAt, or lengthen the edge")
    # 3b · a free label touching the bar or crow of an ER end: on a 48-unit stub from the parent, a verb label at
    #      labelDy -16 sat on the `one` bar and the tool was silent (sd52 run, `nhắn` on users → dms).
    #      The bar or crow lies within ~24 units of the tip and ~8 units either side of the line (measured on the PNG).
    da_bao = set()
    for ar in (e for e in conv if e['type'] == 'arrow' and len(e.get('points', [])) >= 2):
        P = [(ar['x'] + p[0], ar['y'] + p[1]) for p in ar['points']]
        for kieu, tip, prev in ((ar.get('endArrowhead'), P[-1], P[-2]), (ar.get('startArrowhead'), P[0], P[1])):
            if not str(kieu or '').startswith('crowfoot'):
                continue
            L = math.hypot(prev[0] - tip[0], prev[1] - tip[1]) or 1
            ux, uy = (prev[0] - tip[0]) / L, (prev[1] - tip[1]) / L
            q = (tip[0] + ux * min(24, L), tip[1] + uy * min(24, L))
            xs = [tip[0] - uy * 8, tip[0] + uy * 8, q[0] - uy * 8, q[0] + uy * 8]
            ys = [tip[1] + ux * 8, tip[1] - ux * 8, q[1] + ux * 8, q[1] - ux * 8]
            vung = {'x': min(xs) - 1, 'y': min(ys) - 1, 'width': max(xs) - min(xs) + 2, 'height': max(ys) - min(ys) + 2}
            for f in free:
                if f['id'] not in da_bao and giao(f, vung) > 0:
                    da_bao.add(f['id'])
                    nhac.append(f"label “{f['text'][:22]}” touches the bar or crow of an ER end at ({tip[0]:.0f},{tip[1]:.0f}): "
                                f"slide it with labelAt toward the middle of the edge, or raise it with labelDy")
    # 3c · a sequence message label runs across a lifeline (lessons rule 16: the most common leftover flaw).
    #      Measured on Excalidraw's Nunito box, which is ~20% wider than the Patrick Hand glyphs the SVG shows,
    #      so the box itself is the clearance (hang-doi 0.1 run: two labels and a self-message label crossed
    #      the next lifeline and the tool was silent).
    song = [e for e in conv if e['type'] == 'line' and '~life~' in str(e.get('id'))]
    for t in conv:
        if t['type'] != 'text' or '~lab~' not in str(t.get('id')):
            continue
        for L in song:
            ys = [L['y'] + p[1] for p in L['points']]
            if t['x'] < L['x'] < t['x'] + t['width'] and min(ys) < t['y'] + t['height'] and t['y'] < max(ys):
                ai = str(L['id']).split('~life~')[1]
                nhac.append(f"sequence label “{t['text'][:26]}” runs across the lifeline of '{ai}': shorten it, "
                            f"or raise `gap` (this label needs about {t['width'] + 30:.0f})")
    # 3d · an arrow's stroke runs through free text: a `vh` arrow leaving the bottom of a cells strip ran straight
    #      down through the strip's caption under it ("PEL: chưa XACK") and the tool was silent (hang-doi 2.3 run).
    #      Measured on the Excalidraw text box shrunk by 2 units, so a label resting beside its own line is skipped.
    for ar in (e for e in conv if e['type'] == 'arrow' and len(e.get('points', [])) >= 2):
        P = [(ar['x'] + p[0], ar['y'] + p[1]) for p in ar['points']]
        for f in free:
            r = {'x': f['x'], 'y': f['y'], 'w': f['width'], 'h': f['height']}
            if any(_cat_doan_hcn(P[k], P[k + 1], r, co=2) for k in range(len(P) - 1)):
                nhac.append(f"an arrow's line runs through text “{f['text'][:22]}”: move the text, or the arrow's side/route")
    # 4 · too many accent colors
    dung_mau ={e.get('color') for e in goc if e.get('color') in ACCENT} | {e.get('fill') for e in goc if e.get('fill') in ACCENT}
    if len(dung_mau) > 3:
        nhac.append(f"{len(dung_mau)} accent colors used ({' '.join(sorted(dung_mau))}): above 3, none stands out")
    # 5 · only boxes joined by arrows
    #     A `code` block is a rectangle too, but it is evidence, not a component: a figure of
    #     seven code blocks and no arrow got this nudge (infra2 run). So code blocks do not count,
    #     and a figure needs at least one arrow to be "joined by arrows".
    loai = {e['type'] for e in conv}
    hop = [e for e in conv if e['type'] == 'rectangle' and e.get('backgroundColor') != CANH_NEN]
    if loai <= {'rectangle', 'arrow', 'text'} and len(hop) >= 4 and 'arrow' in loai \
            and not any(e.get('strokeStyle') == 'dashed' or (e['type'] == 'rectangle' and e.get('roundness') is None) for e in conv):
        nhac.append('figure is only rounded boxes joined by arrows: check references/figure-types.md for a figure type '
                    'that SHOWS the mechanism better')
    return cung, list(dict.fromkeys(nhac))


JS = """async ([sk, raw]) => {
  await document.fonts.load("400 16px Nunito", 'Ăâề đư 100'); await document.fonts.ready;
  const F = window.__FF.Nunito, M = window.__FF.Cascadia;
  for (const e of sk) {
    if (e.type === 'text') e.fontFamily = e._mono ? M : F;
    if (e.label) e.label.fontFamily = F;
    delete e._mono;
  }
  const els = window.__conv(sk, {regenerateIds: false});
  const base = {angle: 0, groupIds: [], frameId: null, boundElements: null, link: null, locked: false,
                isDeleted: false, version: 1, fillStyle: 'solid', strokeStyle: 'solid', opacity: 100,
                backgroundColor: 'transparent', roundness: null};
  raw.forEach((r, i) => { const k = r._k; delete r._k;
    const o = Object.assign({}, base, r, {id: 'ic' + i});
    if (o.type === 'line' || o.type === 'arrow') { o.lastCommittedPoint = null; o.startArrowhead = o.startArrowhead || null;
      o.endArrowhead = o.type === 'arrow' ? (o.endArrowhead || 'arrow') : null; }
    els.push(o); });
  els.forEach((e, i) => { e.seed = 1000 + i * 37; e.versionNonce = 1; e.updated = 1; });
  const svg = await window.__toSvg({elements: els, appState: {exportBackground: false, exportPadding: 16}, files: null});
  return {els, svg: svg.outerHTML};
}"""

XEM = """<!doctype html><html data-theme="light"><meta charset="utf-8">
<link rel="stylesheet" href="/dist/assets/tokens.css"><link rel="stylesheet" href="/assets/fonts/fonts.css">
<style>body{margin:0;background:var(--bg)}#k{width:%dpx;margin:16px;padding:16px;background:var(--paper);
border:1px solid var(--line);border-radius:12px}#k svg{display:block;width:100%%;height:auto;max-width:%dpx;margin:0 auto}</style>
<div id="k">%s</div></html>"""

DO = """() => {
  const s = document.querySelector('#k svg'), k = s.getBoundingClientRect(), bad = [];
  const ty = k.width / s.viewBox.baseVal.width; let nho = 99, nhoTxt = '';
  for (const t of s.querySelectorAll('text')) { const r = t.getBoundingClientRect();
    const fs = parseFloat(t.getAttribute('font-size') || 20) * ty;
    if (fs < nho) { nho = fs; nhoTxt = t.textContent.slice(0, 24); }
    if (r.left < k.left - 1 || r.right > k.right + 1) bad.push(t.textContent.slice(0, 30)); }
  return {nho: Math.round(nho * 10) / 10, nhoTxt, bad};
}"""


_MASK_RE = re.compile(r'<mask id="[^"]*">.*?</mask>', re.S)
_RECT_RE = re.compile(r'<rect\b([^>]*)>(?:</rect>)?')


def mask_rects_to_paths(svg):
    """An arrow label cuts its line with a <mask> of two <rect>s (full cover + label hole).

    precheck.py's contrast gate takes every <rect> in an svg.dg as a possible background and
    measures it with getBBox(), which also answers for unpainted mask content.
    In dark mode the full-cover rect is var(--pre-fg) (light), so every text it spans fails at ~1.2:1.
    The same geometry as a <path> paints identically and is outside that gate's shape list.
    """
    def rect_to_path(m):
        a = dict(re.findall(r'([\w-]+)="([^"]*)"', m.group(1)))
        x, y = float(a.get('x', 0)), float(a.get('y', 0))
        w, h = float(a.get('width', 0)), float(a.get('height', 0))
        extra = ''.join(f' {k}="{a[k]}"' for k in ('fill', 'opacity') if k in a)
        return f'<path d="M{x:g} {y:g}h{w:g}v{h:g}h{-w:g}Z"{extra}></path>'
    return _MASK_RE.sub(lambda m: _RECT_RE.sub(rect_to_path, m.group(0)), svg)


_TEXT_G_RE = re.compile(r'<g((?: [\w-]+="[^"]*")*?) transform="translate\(([-\d.e]+) ([-\d.e]+)\) rotate\(0 [^)]*\)"'
                        r'((?: [\w-]+="[^"]*")*)>((?:<text\b[^>]*>.*?</text>)+)</g>', re.S)
_CODE_G_RE = re.compile(r'<g stroke-linecap="round" transform="translate\(([-\d.e]+) ([-\d.e]+)\) rotate\(0 ([-\d.e]+) ([-\d.e]+)\)">'
                        r'(?=<path[^>]*fill="var\(--pre-bg\)")')


def code_bg_rects(svg):
    """Give precheck.py's contrast gate the dark background of each `code` block.

    That gate takes only <rect>/<circle>/<ellipse>/<polygon> as backgrounds and compares getBBox() boxes,
    which are in each element's LOCAL space. Excalidraw draws every shape as <path> and puts every text in a
    <g transform="translate(..)">, so all text was measured against the page: harmless for ink text, but the
    light text of a dark `code` block failed at 1.26:1 in the light theme (ds3 run).
    So: move each unrotated text group's translate into its x/y (same pixels, absolute coordinates), then put
    a <rect> in --pre-bg, inset 8 units so the rough rounded path hides it, under each code block.
    """
    def text_abs(m):
        tx, ty = float(m.group(2)), float(m.group(3))
        def move(t):
            t = re.sub(r'(<text\b[^>]*?\s)x="([-\d.e]+)"', lambda k: f'{k.group(1)}x="{float(k.group(2)) + tx:g}"', t, count=1)
            return re.sub(r'(<text\b[^>]*?\s)y="([-\d.e]+)"', lambda k: f'{k.group(1)}y="{float(k.group(2)) + ty:g}"', t, count=1)
        return f'<g{m.group(1)}{m.group(4)}>' + re.sub(r'<text\b[^>]*>', lambda k: move(k.group(0)), m.group(5)) + '</g>'

    def rect(m):
        x, y, w, h = float(m.group(1)), float(m.group(2)), 2 * float(m.group(3)), 2 * float(m.group(4))
        return (f'<rect x="{x + 8:g}" y="{y + 8:g}" width="{w - 16:g}" height="{h - 16:g}" rx="8" '
                f'fill="var(--pre-bg)"></rect>' + m.group(0))
    return _CODE_G_RE.sub(rect, _TEXT_G_RE.sub(text_abs, svg))


def ve(pg, base, src, ra):
    ten = src.stem
    sk, raw, hinh, lint_arrows, goc = dung(nap(src))
    sk0 = copy.deepcopy(sk)
    r = pg.evaluate(JS, [sk, raw])
    svg = re.sub(r'<style.*?</style>', '', r['svg'], flags=re.S)
    vb = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
    w, h = float(vb.group(1)), float(vb.group(2))
    svg = re.sub(r'<svg\b[^>]*>', f'<svg viewBox="0 0 {w:g} {h:g}" xmlns="http://www.w3.org/2000/svg" class="dg">', svg, count=1)
    svg = svg.replace('font-family="Nunito,', "font-family=\"'Patrick Hand', Nunito,")
    svg = re.sub(r'font-family="Cascadia[^"]*"', "font-family=\"'IBM Plex Mono', monospace\"", svg)
    svg = re.sub(re.escape(CANH_NEN), 'var(--pre-bg)', svg, flags=re.I)
    svg = re.sub(re.escape(CANH_CHU), 'var(--pre-fg)', svg, flags=re.I)
    for k, hx in LIT.items():
        svg = re.sub(re.escape(hx), f'var(--{k})', svg, flags=re.I)
    svg = X._fix_mask_luminance(T.tokenize(svg))      # same as the engine's PATCH 8 (VÁ 8): masks do not flip with the theme
    svg = code_bg_rects(mask_rects_to_paths(svg))
    sot = T.audit(svg)
    (ra / f'{ten}.excalidraw').write_text(json.dumps(
        {'type': 'excalidraw', 'version': 2, 'source': 'migrationKl', 'elements': r['els'],
         'appState': {'viewBackgroundColor': '#ffffff', 'gridSize': None}, 'files': {}},
        ensure_ascii=False, indent=1).replace(CANH_NEN, MAU['ink']).replace(CANH_CHU, '#DCE6F5'), encoding='utf-8')
    (ra / f'{ten}.svg').write_text(svg, encoding='utf-8')
    pg.route('**/__xem.html*', lambda rt: rt.fulfill(body=XEM % (COT, int(w), ''), content_type='text/html'))
    pg.set_viewport_size({'width': COT + 66, 'height': 400})
    pg.goto(f'{base}/__xem.html?{ten}')
    pg.evaluate("s => { document.getElementById('k').innerHTML = s }", svg)
    pg.evaluate('document.fonts.ready')
    do = None
    for th in ('light', 'dark'):
        pg.evaluate("v => { document.documentElement.dataset.theme = v }", th)   # same as tools/shot.py
        pg.wait_for_timeout(200)
        pg.locator('#k').screenshot(path=str(ra / f'{ten}-{th}.png'))
        if th == 'light':
            do = pg.evaluate(DO)
    pg.unroute('**/__xem.html*')
    cung, nhac = soat(r['els'], hinh, lint_arrows, goc, sk0)
    cung += [f'text “{b}” overflows the figure frame' for b in do['bad']]
    ty = min(COT / w, 1.0)
    if do['nho'] < CHU_MIN:
        cung.append(f"smallest text {do['nho']}px (“{do['nhoTxt']}”) is below the {CHU_MIN}px limit: figure is {w:.0f} wide, "
                    f"stack it vertically or split the figure, do not shrink the text")
    elif do['nho'] < CHU_NEN:
        nhac.append(f"smallest text {do['nho']}px (“{do['nhoTxt']}”): readable but tight. Figure is {w:.0f} wide, try to make it narrower")
    if sot:
        cung.append(f'non-token colors left: {sorted(sot)}')
    print(f"{'✗' if cung else '✓'} {ten}: {len(r['els'])} elements · {w:.0f}×{h:.0f} · scale {ty:.2f}× · smallest text {do['nho']}px")
    for c in cung:
        print('  ✗', c)
    for c in nhac:
        print('  •', c)
    print(f'  → LOOK: {ra / (ten + "-light.png")}')
    print(f'          {ra / (ten + "-dark.png")}')
    return not cung


def main():
    args = sys.argv[1:]
    if not args or '-h' in args or '--help' in args:
        print(__doc__)
        return 0
    ra = None
    if '--out' in args:
        i = args.index('--out')
        ra = pathlib.Path(args[i + 1]).resolve()
        del args[i:i + 2]
    if '--col' in args:
        global COT
        i = args.index('--col')
        COT = int(args[i + 1])
        del args[i:i + 2]
    while '--lib' in args:
        i = args.index('--lib')
        LIBS.append(args[i + 1])
        del args[i:i + 2]
    if '--icons' in args:
        ic = _nap_icon()
        print(f'{len(ic)} icons:\n' + '\n'.join(f"  {k:28} {v.get('src', '')}" for k, v in sorted(ic.items())))
        return 0
    from playwright.sync_api import sync_playwright
    X._ensure_bundle()
    ok = True
    with X.serve(ROOT) as base, sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        loi = []
        pg.on('pageerror', lambda e: loi.append(str(e)))
        pg.route('**/__ve.html', lambda r: r.fulfill(body=X.PAGE, content_type='text/html'))
        for a in args:
            src = pathlib.Path(a).resolve()
            out = ra or src.parent
            out.mkdir(parents=True, exist_ok=True)
            pg.goto(base + '/__ve.html')
            pg.wait_for_function('window.__ready === true', timeout=90000)
            try:
                ok = ve(pg, base, src, out) and ok
            except Loi as e:
                print(f'✗ {src.stem}: {str(e)[2:]}')
                ok = False
            except Exception as e:
                print(f'✗ {src.stem}: {type(e).__name__}: {str(e)[:300]}' + (f' | {loi[-1][:200]}' if loi else ''))
                ok = False
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
