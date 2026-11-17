"""Icon tech cho sơ đồ, lấy từ gói Iconify cục bộ.

Nhúng thẳng dạng dataURL: verify.py chặn mọi request ra ngoài origin, nên trỏ
tới CDN của Iconify là hỏng offline ngay. Gói @iconify-json/logos nặng 7,3MB
nhưng nằm ở devDependencies - chỉ build đọc, không lên site.

Màu bên trong mỗi icon KHÔNG đi qua token hệ theme (`var(--l4)`...) - đó là
chủ đích, không phải sót. Icon là logo thương hiệu (PostgreSQL `#336791`,
Redis đỏ...), nhúng dạng base64 bên trong `data:image/svg+xml;base64,...`.
`theme.audit()` không thấy các hex đó vì bảng chữ base64 không chứa `#`/`(`/
`)` nên không khớp `_COLOR_RE` - nhưng dù có thấy được, logo thương hiệu vẫn
phải giữ đúng màu gốc của nó, không đổi theo dark/light mode như hình vẽ tay.
Xem chú thích tương ứng ở assertion "audit sạch kể cả có icon" trong
scripts/test-excalidraw.py.
"""
import re, json, base64, difflib, functools, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PACKS = {'logos': ROOT / 'node_modules' / '@iconify-json' / 'logos' / 'icons.json'}


@functools.lru_cache(maxsize=None)
def _pack(name):
    p = PACKS.get(name)
    if not p or not p.exists():
        return None
    return json.loads(p.read_text(encoding='utf-8'))


def parse(spec):
    """`"A:logos:redis, D:logos:postgresql"` -> `{'A': 'logos:redis', ...}`.

    Phần không đúng dạng "id:pack:icon" (thiếu dấu `:`, thiếu id, hoặc thiếu
    tên icon) bị BỎ QUA ở đây - hàm này chỉ dựng bảng dùng được, không báo
    lỗi. Muốn biết phần nào bị bỏ qua và vì sao, gọi `malformed()` - tách
    riêng để `parse()` luôn an toàn gọi ở đường render (không được phép crash
    hay cần biết ngữ cảnh báo lỗi), còn `malformed()` phục vụ đúng một nơi cần
    báo lỗi cho tác giả: cổng `precheck.py`.
    """
    out = {}
    for part in (spec or '').split(','):
        part = part.strip()
        if not part:
            continue
        node, _, icon = part.partition(':')
        if node and icon:
            out[node.strip()] = icon.strip()
    return out


def malformed(spec):
    """Các phần trong `spec` KHÔNG đúng dạng "id:pack:icon", nguyên văn.

    `"A:logos:redis, nocolonhere"` -> `['nocolonhere']`. Trước bản vá này,
    một phần sai cú pháp bị `parse()` lặng lẽ bỏ qua - tác giả gõ nhầm không
    hề biết icon của mình vừa biến mất, không phải vì icon sai tên (đã có gate
    riêng) mà vì cả cặp node:icon không được nhận diện.
    """
    bad = []
    for part in (spec or '').split(','):
        raw = part.strip()
        if not raw:
            continue
        node, sep, icon = raw.partition(':')
        if not sep or not node.strip() or not icon.strip():
            bad.append(raw)
    return bad


def data_url(name):
    """`"logos:redis"` -> dataURL, hoặc None nếu không có."""
    pack_name, _, key = (name or '').partition(':')
    d = _pack(pack_name)
    if not d or key not in d.get('icons', {}):
        return None
    ic = d['icons'][key]
    w = ic.get('width', d.get('width', 24))
    h = ic.get('height', d.get('height', 24))
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">'
           f'{ic["body"]}</svg>')
    return 'data:image/svg+xml;base64,' + base64.b64encode(svg.encode('utf-8')).decode()


def closest(name, pool, n=3):
    """Tên gần đúng nhất với `name` trong `pool` - dùng chung cho gợi ý tên
    icon (`suggest()`) lẫn gợi ý node id ở cổng precheck.py."""
    if not name:
        return []
    return difflib.get_close_matches(name, pool, n=n, cutoff=0.5)


def suggest(name, n=3):
    """Gợi ý tên gần đúng khi icon không tồn tại, vd `docker` -> `docker-icon`.

    Tên icon không phải lúc nào cũng trùng tên sản phẩm - precheck.py dùng hàm
    này để báo lỗi kèm gợi ý thay vì chỉ nói "không có", để tác giả sửa ngay
    lúc viết chứ không phải mò trong icons.json 7MB.
    """
    pack_name, _, key = (name or '').partition(':')
    d = _pack(pack_name)
    if not d or not key:
        return []
    return closest(key, d.get('icons', {}).keys(), n=n)


# ── id node trong nguồn mermaid thô ─────────────────────────────
# Heuristic bằng regex, KHÔNG phải parser mermaid đầy đủ - chỉ cần đủ tốt để
# cổng icons= biết "id này CÓ xuất hiện trong sơ đồ hay không". subgraph/
# stateDiagram/erDiagram đằng nào cũng rơi về fallback ở excalidraw.py (bộ
# chuyển mermaid-to-excalidraw không đỡ những loại này), nên icons= trên
# chúng vô nghĩa và heuristic không cần đúng cho các loại đó.
_QUOTED_RE = re.compile(r'"(?:[^"\\]|\\.)*"')
# Chuỗi mũi tên mermaid: `-->`, `---`, `-.->`, `==>`, `--x`, `--o`... KHÔNG
# gồm `|` - `|` là dấu mở nhãn cạnh (`-->|nhãn| B`), lỡ gồm vào thì token
# arrow nuốt luôn dấu `|` và nhãn phía sau bị đọc nhầm thành id.
_ARROW = r'[.\-=]{2,}[xo>]{0,2}'
_SHAPE_OPEN_RE = re.compile(r'\b([A-Za-z_]\w*)\s*(?=[\[({])')      # A[...] B(...) C{...}
_ARROW_HEAD_RE = re.compile(r'\b([A-Za-z_]\w*)\s*(?=' + _ARROW + r')')   # A -->
_ARROW_TAIL_RE = re.compile(r'(?:' + _ARROW + r')\s*(?:\|[^|\n]*\|\s*)?([A-Za-z_]\w*)\b')  # --> B, -->|nhãn| B
_DECL_RE = re.compile(r'\b(?:participant|actor)\s+([A-Za-z_]\w*)')  # sequenceDiagram


def mermaid_node_ids(src):
    """Tập id node xuất hiện trong nguồn mermaid `src` - dùng để cổng
    precheck.py biết một `icons="Z:..."` có trỏ tới node THẬT SỰ có trong sơ
    đồ hay không.

    Bỏ nội dung trong chuỗi `"..."` trước khi quét (giữ nguyên độ dài để không
    lệch vị trí), tránh chữ trong nhãn ("Request GET /user/:id"...) bị đọc
    nhầm thành id hay mũi tên.
    """
    clean = _QUOTED_RE.sub(lambda m: '"' + ' ' * (len(m.group(0)) - 2) + '"', src or '')
    ids = set()
    ids.update(_SHAPE_OPEN_RE.findall(clean))
    ids.update(_ARROW_HEAD_RE.findall(clean))
    ids.update(_ARROW_TAIL_RE.findall(clean))
    ids.update(_DECL_RE.findall(clean))
    return ids
