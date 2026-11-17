"""Nướng sơ đồ mermaid thành hình Excalidraw nét vẽ tay, lúc build.

Khung giống engine/mermaid.py (Chromium thật + server cục bộ + tokenize). Khác
ở CHÍN phép vá, mỗi cái chữa một lỗi đã đo trên corpus thật:

  1 · <br/> -> dấu ngăn PHÙ HỢP VỚI LOẠI SƠ ĐỒ. Bộ chuyển không xử lý <br/>,
      nên 543/786 hình (69%) sẽ hiện "<br>" nguyên văn giữa nhãn nếu bỏ qua vá
      này - nhưng thay bằng xuống dòng thật CHỈ đúng cho flowchart (nhãn nằm
      trong `["..."]`, chấp nhận xuống dòng). sequenceDiagram là cú pháp MỘT
      DÒNG MỘT LỆNH - `B->>S: msg<br/>tiếp` mà thay `<br/>` bằng `\n` thật thì
      dòng bị cắt làm đôi, phần dư "tiếp" không còn là cú pháp mermaid hợp lệ
      -> hỏng cả build (đo THẬT: content/backend/02-mang-va-runtime.md, "Parse
      error on line 6" - phát hiện sau khi chạy toàn bộ 786 sơ đồ thật qua
      renderer, không phải chỉ vài mẫu tay). 40/180 sequenceDiagram trong
      corpus có `<br/>`, dùng `" · "` (dấu ngăn dày đặc đã có sẵn trong CLAUDE.md
      của kho) thay vì xuống dòng. stateDiagram-v2/erDiagram đã kiểm THẬT
      (không đoán): cả hai không lỗi cú pháp dù nhận `\n`, vì chúng rơi về
      fallback bất kể nội dung bên trong (xem VÁ dưới) - nhưng vẫn dùng `" · "`
      cho đồng nhất, để không có loại sơ đồ nào (kể cả loại tương lai chưa
      gặp) mặc định rơi vào nhánh nguy hiểm.
  2 · font Nunito, KHÔNG phải Excalifont. Excalifont gộp cả 7 file subset chỉ
      có 561 glyph và thiếu 35/43 ký tự tiếng Việt - 778/786 hình (98%) mất
      dấu, "Kết nối" hiện thành "Kêt nôi". Đây là SAI CHỮ, không phải xấu chữ.
  3 · màu đặt ĐÚNG BẰNG hex token của theme.LIGHT (hoặc palette truyền vào qua
      `theme=`), để tokenize() ánh xạ chính xác qua _BY_HEX thay vì rơi vào
      _nearest() đoán mò. Mặc định Excalidraw là #1e1e1e đen tuyền - vô hình
      ở dark mode. Đây cũng là lý do người gọi KHÔNG được truyền màu tuỳ ý qua
      `theme` - nó phải là một bảng có hex khớp đúng bảng của theme.py (thực
      tế luôn là T.LIGHT), nếu không audit() sẽ không sạch. Áp dụng cho
      `rectangle`/`diamond`/`ellipse` (màu theo `color=` của fence - mang
      thông tin tầng OSI) VÀ cho `line` (màu ĐÚNG BẰNG `--line` cố định,
      không theo `color=` - đây là nét kẻ cấu trúc của sequenceDiagram, khung
      loop/alt/opt và thanh activation, không phải nội dung theo tầng). Đo
      trên toàn corpus 786 sơ đồ thật: `line` là type DUY NHẤT còn sót màu
      cứng (#adb5bd, 34 phần tử/7 sơ đồ) sau khi rectangle/diamond/ellipse đã
      được vá - không type nào khác lộ ra khi kiểm hết.
  4 · bóc @font-face base64 khỏi SVG. Nó chiếm 31-45% dung lượng mỗi hình và
      lặp lại 786 lần; khai Nunito một lần ở assets/fonts/ thì mỗi hình còn
      16-23KB, tức NHỎ HƠN bản mermaid hiện tại.
  5 · id/seed/versionNonce/updated ép TẤT ĐỊNH SAU khi `convertToExcalidrawElements`
      chạy - suy từ id sơ đồ (ổn định giữa các lần build) cộng vị trí phần tử
      trong mảng (ổn định trong cùng sơ đồ), không đụng random seed toàn cục
      nên thêm một sơ đồ mới không làm lệch id/seed của sơ đồ khác. `.cache/
      figs` (thực chất là `figs/`, xem .gitignore) cam kết 1806 SVG vào repo
      để CI khỏi cần Chromium; không tất định thì mỗi lần build lại đều đổi
      bytes vô nghĩa. Đủ cho MỌI hình học suy ra từ `seed` ở bước `exportToSvg`
      (rough.js đọc `seed` lúc đó, tức SAU ghi đè này) - NHƯNG KHÔNG đủ cho vị
      trí của text buộc vào một container NHIỀU ĐIỂM/CONG (mũi tên): thư viện
      tính vị trí đó qua một phép TÌM TRUNG ĐIỂM ĐƯỜNG CONG ngay TRONG
      `convertToExcalidrawElements` (`redrawTextBoundingBox`), và đo THẬT xác
      nhận phép tìm đó nhạy với nhiễu dấu phẩy động của Chromium giữa các lần
      khởi động process ĐỘC LẬP VỚI SEED - patch tạm `Math.random` sang một
      PRNG tất định trước khi convert (thử trước, giữ lại để so sánh) KHÔNG
      đổi kết quả: container (x/y/width/height/points/seed cuối) byte-identical
      giữa hai lần khởi động, chỉ MỘT MÌNH vị trí text lệch 1-2 đơn vị. Vì
      `exportToSvg` không đọc lại toạ độ này lúc xuất (tự tính vị trí hiển thị
      từ hình học container hiện tại - đã kiểm: SVG không đổi dù đổi x/y text
      này) nên bản SVG tĩnh không sao, nhưng scene ta lưu (Task 4 viewer đọc
      THẲNG, không gọi lại thư viện) thì có - đo trên toàn corpus: nướng lại
      hai process độc lập, 104/719 scene khác byte, luôn ở đúng phần tử `text`
      buộc vào container có `roundness`. Khoá bằng cách GHI ĐÈ x/y của những
      phần tử này (VÁ 5b, sau vòng gán seed/id ở trên) bằng công thức CANH
      GIỮA chuẩn - đúng ý nghĩa `textAlign: CENTER, verticalAlign: MIDDLE` mà
      thư viện đặt mặc định cho MỌI container - tất định tuyệt đối vì chỉ phụ
      thuộc hình học container và width/height của chính text (cả hai đã xác
      nhận ổn định; chỉ phép TÌM TRUNG ĐIỂM ĐƯỜNG CONG mới nhạy nhiễu).
  6 · nền ĐẶC (fillStyle='solid') + viền/chữ ĐỔI VAI TRÒ với color=. Bản
      trước tô `color=` lên VIỀN và CHỮ, hình khối rỗng ruột - đọc mỏng, và
      chữ theo màu tầng đo được chỉ 3,87-5,99:1 trên `--card` (tools/contrast.py),
      trong khi mermaid cũ nó thay thế dùng `--ink` và được 17,41:1 - một hồi
      quy về độ đọc, không chỉ thẩm mỹ. Bản này đảo lại: `color=` giờ chọn
      NỀN (tint nhạt của theme.FILL_TOKENS, vd `l4` -> `--fill-l4`), còn viền
      VÀ chữ luôn `--ink` (gần đen ở theme sáng, gần trắng ở theme tối vì
      `--ink` tự đảo) - phục hồi đúng 17,41:1 vì chữ lại dùng chính `--ink`
      như mermaid cũ. `ink`/`perf` không có tint riêng: `ink` (mặc định,
      không phải màu tầng) dùng lại `--fill-soft` đã có sẵn; `perf` là bí
      danh của `warn` (đúng tiền lệ `.c-perf{background:var(--warn)}` ở
      base.css) - trước bản vá này `pal['perf']` undefined nên rơi về `ink`
      trong im lặng, vô hại lúc còn là viền mảnh nhưng RÕ MẮT khi color= giờ
      quyết định cả một mảng nền. Thêm bo góc (`roundness` ADAPTIVE_RADIUS)
      cho riêng `rectangle`, và tăng `roughness` 1 -> 2 (ROUGHNESS.artist ->
      .cartoonist) cho `rectangle`/`diamond`/`ellipse`/`line` để nét lệch tay
      rõ hơn. Theo đúng yêu cầu thẩm mỹ chủ dự án đưa ra khi duyệt bản xem
      trước, kèm hai ảnh mẫu tham khảo.
  7 · font-family VIẾT LẠI thành Patrick Hand SAU KHI đã đo/dàn trang bằng
      Nunito (VÁ 2). Nunito đúng độ rộng cho tiếng Việt nhưng KHÔNG phải font
      viết tay; Patrick Hand là font viết tay VÀ phủ đủ tiếng Việt, nhưng đo
      riêng: hẹp hơn Nunito ~9% ở cùng chuỗi tiếng Việt, nên không dùng để đo
      (hộp sẽ hẹp hơn chữ thật, tràn ra ngoài). Cách xử lý: giữ nguyên VÁ 2
      (đo bằng Nunito), rồi sau khi `exportToSvg` đã chạy xong - hộp đã cố
      định kích thước - tráng chuỗi `font-family="Nunito,...` thành
      `font-family="'Patrick Hand', Nunito,..."`. Hộp đo rộng cho Nunito nên
      Patrick Hand (hẹp hơn) không bao giờ tràn, chỉ lỏng hơn một chút.
  8 · mask luminance của chính exportToSvg (không phải code ta viết) khoét
      khoảng trống trên đường kẻ dưới nhãn (message sequenceDiagram, nhãn
      cạnh mũi tên) bằng hai `<rect>` trong một `<mask>`: một "nền sáng" (mọi
      chỗ mặc định HIỆN trên phần tử tham chiếu mask), một "vùng tối" đúng vị
      trí nhãn (HIỆN trong mask nghĩa là bị CHE trên phần tử tham chiếu -
      luminance mask chuẩn SVG). Excalidraw tự đặt hai màu này ĐÚNG BẰNG màu
      nền (var(--card) sau tokenize) và màu viền mũi tên (var(--ink)) - hợp
      lý cho một bản xuất TĨNH một theme, nhưng CẢ HAI token đều đảo giá trị
      theo theme (VÁ 6 làm cho mọi màu khác) nên ở dark mode card hoá TỐI và
      ink hoá SÁNG - quan hệ sáng/tối mask cần bị LẬT NGƯỢC. Đo THẬT: chụp
      màn hình dark mode bất kỳ sequenceDiagram nào, đường kẻ hiện xuyên qua
      chữ như gạch ngang dù light mode vẫn đúng. Mask không phải màu người
      đọc thấy - khoá cứng về `var(--pre-fg)`/`var(--pre-bg)`, hai token DUY
      NHẤT trong theme.py KHÔNG đảo theo theme (`--pre-bg` luôn tối, `--pre-fg`
      luôn sáng - dùng cho khối code, xem CLAUDE.md), nên quan hệ sáng/tối
      mask cần giữ đúng ở CẢ HAI theme mà không cần token mới: cả hai vẫn qua
      audit() vì vẫn là token hợp lệ, chỉ đổi Ý NGHĨA sử dụng.

      (Một hướng khác đã thử và bỏ: tự chèn thêm một `<rect>` nền đặc phía
      sau nhãn, giống `MERMAID_THEME.edgeLabelBackground` của đường mermaid
      cũ. Bỏ vì lý do kỹ thuật, không phải thẩm mỹ: rect mới phải qua một
      lần `convertToExcalidrawElements()` RIÊNG (đã có scene, chỉ thêm phần
      tử), lần gọi riêng đó tự sinh `index` - vị trí vẽ theo fractional
      indexing - từ đầu, ĐỤNG ĐỘ với index đã dùng trong scene chính; rect
      mới vẽ SAU CÙNG bất kể nó được nối vào mảng ở đâu, đè kín cả chữ nhãn.
      Sửa mask có sẵn của thư viện không gặp vấn đề này vì không thêm phần
      tử nào.)
  9 · làm tròn HÌNH HỌC của phần tử (x/y/width/height/angle/points) về 3 chữ
      số sau dấu phẩy NGAY TRONG TRANG (trước khi gọi `exportToSvg`), KHÔNG
      phải regex trên chuỗi SVG đã xuất ra. Khử NHIỄU DẤU PHẨY ĐỘNG giữa các
      lần build (đo THẬT: `python3 build.py --no-cache` hai lần độc lập cho
      ra 90-101/719 sơ đồ khác byte, luôn ở chữ số thập phân thứ 11-13 của
      MỘT toạ độ tính - đặc tính đã biết của Chromium/V8, phép đo chữ/căn giữa
      phức tạp không đảm bảo CÙNG BYTE giữa các lần khởi động process độc lập
      dù công thức và input giống hệt nhau). BẢN VÁ TRƯỚC làm điều này bằng
      regex khớp số thập phân trên TOÀN BỘ chuỗi SVG sau khi xuất - vỡ THẬT trên
      corpus: nhãn tác giả gõ `"MIT 6.5840 Lab 2"` bị chính regex đó khớp như
      một số thập phân, `round(6.584, 3)` rồi bỏ số 0 đuôi ra `"6.584"` - MỘT
      CHỮ SỐ TRONG TÊN MỘT MÔN HỌC THẬT bị đổi âm thầm. Regex trên chuỗi
      xuất ra không phân biệt được toạ độ hình học với chữ tác giả gõ; làm
      tròn hình học TRƯỚC khi gọi `exportToSvg` thì KHÔNG BAO GIỜ chạm tới nội
      dung `<text>` (thư viện tự escape/ghi text nguyên văn, ta không đụng
      chuỗi SVG output nữa) mà vẫn khử đúng nguồn nhiễu (input của phép đo chữ
      và roughjs bên trong `exportToSvg` giờ đã là số đã ghim, nên đầu ra của
      chính nó cũng ổn định theo). `scripts/test-excalidraw.py` có cổng riêng
      xác nhận MỌI nhãn nguồn mermaid sống sót nguyên văn trong SVG xuất ra.

Hình nào bộ chuyển không đỡ (subgraph, stateDiagram-v2, erDiagram) thì nó trả
về một phần tử `image` bọc ảnh. Ta KHÔNG dùng thứ đó - báo lên để người gọi
quay về đường mermaid cũ.

Font Nunito bản thân KHÔNG nạp qua CSS: @excalidraw/excalidraw fetch nó lúc
chạy bằng `new FontFace()`, tính URL từ `window.EXCALIDRAW_ASSET_PATH` - bỏ
qua thì nó rơi về mặc định `https://esm.sh/...`, tức mỗi lần build đều gọi
mạng thật. Ta trỏ biến đó về `node_modules/@excalidraw/excalidraw/dist/prod/`
qua HTTP server cục bộ (đã phục vụ sẵn ROOT) để build luôn chạy offline.

`items[].icons` (Task 2) là spec dạng `"A:logos:redis, D:logos:postgresql"` -
chuyển ra dataURL cục bộ qua `icons.data_url()` rồi chèn thành phần tử `image`
neo TRÊN ĐƯỜNG VIỀN THẬT của hộp mang node id đó (góc dưới-phải cho
rectangle, điểm giữa cạnh dưới cho diamond/ellipse - xem giải thích đầy đủ
tại chỗ tính toạ độ trong `render()`, đoạn "Icon neo DƯỚI-PHẢI"), kèm một
phần tử `text` chú thích tên dịch vụ ngay dưới icon (bản trước đặt icon nổi
phía TRÊN, không nhãn - đổi theo đúng yêu cầu thẩm mỹ khi duyệt bản xem
trước). Tên chú thích SUY thẳng từ chính icon spec (`"logos:redis"` ->
`"Redis"`), không bắt tác giả gõ tên dịch vụ thêm lần hai. Cả hai phần tử
chèn này xảy ra SAU khi `__conv()` (convertToExcalidrawElements) đã chạy lần
đầu cho scene chính - cần geometry ĐÃ ỔN ĐỊNH (container tự giãn kích thước
để chữ Nunito vừa khít) mới tính đúng điểm neo - rồi được chuyển bằng một
lần `__conv()` RIÊNG trước khi nối vào scene. Cả hai vẫn đi qua VÁ 5 phía
dưới - id/seed/versionNonce/updated của chính chúng cũng suy tất định từ
diagId + vị trí trong mảng cuối cùng, không cần logic riêng. Chỉ `fileId`
của icon là tự đặt trực tiếp bằng `'ic-' + nodeId` (đã tất định sẵn vì
nodeId lấy thẳng từ spec trong markdown).
"""
import os, re, pathlib, threading, functools, http.server, socketserver, contextlib, subprocess
from playwright.sync_api import sync_playwright

import theme as T
import icons as I

ROOT = pathlib.Path(__file__).resolve().parent.parent
BUNDLE = ROOT / '.cache' / 'exca.bundle.js'

BR_RE = re.compile(r'<br\s*/?>', re.I)
FONTFACE_RE = re.compile(r'@font-face\s*\{[^}]*\}', re.S)
# VÁ 7 · font ĐO (Nunito) -> font HIỂN THỊ (Patrick Hand). Chỉ khớp phần MỞ
# đầu `font-family="Nunito,` (dấu phẩy phân cách với fallback emoji do chính
# thư viện Excalidraw nối thêm, vd "Nunito, Segoe UI Emoji") để không đụng gì
# khác trong SVG - giữ nguyên phần đuôi, chỉ chêm 'Patrick Hand' lên đầu danh
# sách font với Nunito làm dự phòng (nếu Patrick Hand lỡ không nạp được).
_FONT_DISPLAY_RE = re.compile(r'(font-family=")Nunito,')
# VÁ 8 · mask luminance của exportToSvg dùng var(--card)/var(--ink) (đảo theo
# theme) - khoá cứng về var(--pre-fg)/var(--pre-bg) (không đảo). Rationale đầy
# đủ ở docstring module, mục 8 - không chép lại ở đây để khỏi hai bản trôi
# nhau.
_MASK_BLOCK_RE = re.compile(r'<mask id="[^"]*">.*?</mask>', re.S)
_FILL_ATTR_RE = re.compile(r'fill="[^"]*"')


def _fix_mask_luminance(svg):
    def fix_block(m):
        block = m.group(0)
        fills = ['var(--pre-fg)', 'var(--pre-bg)']
        i = [0]

        def sub_fill(fm):
            v = fills[i[0]] if i[0] < len(fills) else fm.group(0)
            i[0] += 1
            return f'fill="{v}"'
        return _FILL_ATTR_RE.sub(sub_fill, block)
    return _MASK_BLOCK_RE.sub(fix_block, svg)


# VÁ 9 · làm tròn HÌNH HỌC phần tử (không phải chuỗi SVG) - xem docstring
# module mục 9. KHÔNG có regex nào ở tầng Python cho việc này nữa: bản trước
# regex hoá cả nội dung `<text>` và đã đổi âm thầm một chữ số trong nhãn tác
# giả gõ ("MIT 6.5840 Lab 2" -> "MIT 6.584 Lab 2") - phép làm tròn giờ chạy
# TRONG `pg.evaluate` (xem "VÁ 9" trong khối JS của `render()`), trên các
# trường x/y/width/height/angle/points của từng phần tử, TRƯỚC khi gọi
# `__toSvg`, nên không bao giờ chạm vào chuỗi text tác giả viết.

_COMMENT_RE = re.compile(r'^\s*%%.*$')
# Loại sơ đồ nào chấp nhận CHỮ THẬT xuống dòng trong nhãn - chỉ flowchart
# (nhãn nằm trong `["..."]`, một khối văn bản độc lập). Mọi loại còn lại
# (sequenceDiagram, stateDiagram-v2, erDiagram, và bất kỳ loại nào chưa gặp)
# là cú pháp MỘT DÒNG MỘT LỆNH - một `\n` thật chèn giữa dòng làm gãy câu,
# phần còn lại không còn là cú pháp hợp lệ (xem VÁ 1 bên dưới).
_MULTILINE_LABEL_KINDS = {'flowchart', 'graph'}


def _diagram_kind(src):
    """Từ đầu tiên của dòng khai báo loại sơ đồ - "flowchart", "sequenceDiagram",
    "stateDiagram-v2", "erDiagram"... Bỏ qua dòng trống và dòng comment `%%`."""
    for line in (src or '').split('\n'):
        s = line.strip()
        if not s or _COMMENT_RE.match(s):
            continue
        return s.split()[0] if s.split() else ''
    return ''


# color= (thuộc tính fence) -> hex tint nền. 'perf' là bí danh của 'warn' -
# đúng tiền lệ `.c-perf{background:var(--warn)}` ở base.css (chip HTML dùng
# 'perf' thay 'warn' theo quy ước đặt tên trong CLAUDE.md) - áp lại quy ước đó
# cho nền hình khối, nếu không color="perf" (10 sơ đồ trong corpus) rơi về
# mặc định trong im lặng. 'default' dùng cho 'ink' (mặc định/không xác định -
# không phải màu tầng nên không có 'fill-ink' riêng, dùng lại --fill-soft đã
# có sẵn cho mọi nền trung tính khác trên site).
_FILL_ALIAS = {'perf': 'warn'}


def _fill_pal():
    out = {k[len('fill-'):]: v for k, v in T.FILL_LIGHT.items()}
    for alias, real in _FILL_ALIAS.items():
        out[alias] = out[real]
    out['default'] = T.LIGHT['fill-soft']
    return out


FILL_PAL = _fill_pal()


def _icon_label(spec):
    """`"logos:redis"` -> `"Redis"`. Chú thích dưới icon LẤY THẲNG từ tên icon
    trong `icons=` - không bắt tác giả gõ tên dịch vụ thêm lần hai. Chuyển
    gạch ngang/gạch dưới thành khoảng trắng rồi viết hoa đầu mỗi từ - không
    hoàn hảo về ngữ pháp (`nodejs-icon` -> "Nodejs Icon"), nhưng suy được HOÀN
    TOÀN từ dữ liệu đã có, tất định, không cần tra tên hiển thị ở nơi khác.
    """
    _, _, key = (spec or '').partition(':')
    key = key or spec or ''
    return re.sub(r'[-_]+', ' ', key).strip().title()


@contextlib.contextmanager
def serve(root):
    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    h = functools.partial(Q, directory=str(root))
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(('127.0.0.1', 0), h) as srv:
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            yield f'http://127.0.0.1:{srv.server_address[1]}'
        finally:
            srv.shutdown()


# window.EXCALIDRAW_ASSET_PATH PHẢI được gán trước khi bundle module chạy -
# đặt trong <script> thường (chạy ngay lúc parse), không phải type="module"
# (bị hoãn tới sau khi parse xong HTML).
PAGE = """<!DOCTYPE html><html><head><meta charset="utf-8">
<script>window.EXCALIDRAW_ASSET_PATH = '/node_modules/@excalidraw/excalidraw/dist/prod/';</script>
<link rel="stylesheet" href="/assets/fonts/fonts.css">
<script type="module" src="/.cache/exca.bundle.js"></script>
</head><body><div id="c"></div></body></html>"""


def _ensure_bundle():
    if BUNDLE.exists():
        return
    print('▸ dựng bundle Excalidraw (lần đầu, ~30s)')
    r = subprocess.run(['node', str(ROOT / 'scripts' / 'excalidraw-bundle.mjs')],
                       capture_output=True, text=True)
    if r.returncode != 0 or not BUNDLE.exists():
        raise SystemExit(f'✗ không dựng được bundle Excalidraw:\n{r.stderr[:400]}')


def render(items, theme=None):
    """items: [{id, src, where, color, icons}] -> BỐN phần tử, ĐÚNG BỐN, theo
    thứ tự này - đổi thứ tự hay bớt một phần tử ở nơi gọi là vỡ ngay:

      1. `out`           - {id: svg}. Sơ đồ chuyển được, SVG cuối cùng đã
                            tokenize màu.
      2. `fallback`      - [(id, where, lý_do)]. Sơ đồ bộ chuyển KHÔNG đỡ được
                            (subgraph/stateDiagram-v2/erDiagram) - không có
                            trong `out`, người gọi phải tự quay về mermaid.py.
      3. `scenes`        - {id: {elements, files}}. Scene Excalidraw thô, chỉ
                            Task 4 (viewer thời gian chạy) tiêu thụ - trả về
                            từ Task 1 dù chưa ai đọc, để chữ ký không phải đổi
                            giữa chừng nhánh.
      4. `icon_warnings` - [(id, node_id, lý_do)]. Icon bị BỎ QUA vì `icons=`
                            trỏ node id không có thật trong sơ đồ đó (gõ nhầm,
                            hoặc node bị xoá sau khi viết `icons=`). Thêm ở
                            vòng review Task 2 - CHỮ KÝ ĐÃ ĐỔI TỪ BA THÀNH BỐN
                            phần tử lúc đó; mọi nơi gọi `render()` (kể cả
                            trong `engine/render.py::bake` ở Task 3) PHẢI
                            unpack đủ bốn, không phải ba.

    `icon_warnings` là đường phòng thủ THỨ HAI cho lỗi node id sai -
    `precheck.py` đã chặn được ở đa số trường hợp (đọc trực tiếp nguồn
    mermaid), nhưng ai đó có thể gọi thẳng `render()` mà không qua precheck.
    Thay vì đoán một vị trí để đặt icon lạc chỗ, ta bỏ qua icon đó và báo lại,
    giống hệt cách `fallback` đã báo cho sơ đồ không chuyển được - không có gì
    xảy ra trong im lặng.

    `theme` mặc định `T.LIGHT` - PHẢI là một bảng có hex khớp đúng
    `theme.LIGHT` (không phải màu tuỳ ý) vì `tokenize()` tra khớp CHÍNH XÁC
    qua `_BY_HEX` được dựng từ `T.LIGHT`; truyền một bảng hex khác sẽ làm
    `tokenize()` rơi vào `_nearest()` đoán mò thay vì khớp thẳng, và có thể
    khiến `audit()` không sạch.
    """
    if not items:
        return {}, [], {}, []
    _ensure_bundle()
    page = ROOT / f'_exca-{os.getpid()}.html'
    page.write_text(PAGE, encoding='utf-8')
    pal = dict(theme or T.LIGHT)
    out, fallback, scenes, icon_warnings = {}, [], {}, []
    try:
        with serve(ROOT) as base, sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page()
            errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.goto(f'{base}/{page.name}')
            try:
                pg.wait_for_function('window.__ready === true', timeout=60000)
            except Exception:
                raise SystemExit('✗ bundle Excalidraw không nạp được: ' + ' | '.join(errs[:2]))
            # Ép font vào trạng thái active TRƯỚC khi đo chữ. Bỏ bước này thì
            # Chromium đo bằng font fallback, advance width khác, và mọi hộp
            # nướng ra đều sai kích thước so với chữ thật.
            pg.evaluate("""async () => {
              await document.fonts.load("400 16px Nunito", 'Ăâề đư 100');
              await document.fonts.ready;
            }""")
            for it in items:
                where = it.get('where') or it['id']
                # VÁ 1 · <br/> -> xuống dòng CHỈ cho flowchart/graph (nhãn
                # trong `["..."]` chấp nhận xuống dòng thật). Loại còn lại là
                # cú pháp một dòng một lệnh - sequenceDiagram đã đo THẬT ra lỗi
                # cú pháp (content/backend/02-mang-va-runtime.md, "Parse error
                # on line 6") khi bị chèn \n giữa message; stateDiagram-v2 và
                # erDiagram đã kiểm THẬT không lỗi cú pháp dù dùng \n (chúng
                # rơi về fallback bất kể nội dung, xem docstring module), vẫn
                # đổi sang " · " cho đồng nhất MỘT quy tắc dễ suy luận thay vì
                # ba ngoại lệ khác nhau, và để tránh mọi loại sơ đồ tương lai
                # chưa gặp mặc định rơi vào nhánh nguy hiểm (newline).
                sep = '\n' if _diagram_kind(it['src']) in _MULTILINE_LABEL_KINDS else ' · '
                src = BR_RE.sub(sep, it['src'])
                # icons="A:logos:redis" -> {'A': dataURL} tra sẵn ở Python để
                # trang JS không phải with-fetch gì cả, chỉ nhận dataURL đã có.
                # icsLabel song song {'A': 'Redis'} - chú thích SUY từ icon
                # spec, không cần tác giả gõ tên dịch vụ thêm lần hai.
                ics, ics_label = {}, {}
                for node, nm in I.parse(it.get('icons')).items():
                    u = I.data_url(nm)
                    if u:
                        ics[node] = u
                        ics_label[node] = _icon_label(nm)
                try:
                    r = pg.evaluate(
                        """async ({src, pal, fillPal, color, diagId, ics, icsLabel}) => {
                          const d = await window.__m2e(src, { fontSize: 16 });
                          const kinds = {};
                          for (const e of d.elements) kinds[e.type] = (kinds[e.type] || 0) + 1;
                          // Bộ chuyển không đỡ được thì trả về đúng một <image>.
                          if (kinds.image && d.elements.length <= 2)
                            return { fallback: 'bộ chuyển không đỡ loại sơ đồ này' };
                          const inkHex = pal.ink;
                          const fillHex = fillPal[color] || fillPal.default;
                          for (const e of d.elements) {
                            if (e.type === 'text') {
                              e.fontFamily = window.__FF.Nunito;   // VÁ 2 - đo chữ đúng
                              e.strokeColor = inkHex;              // VÁ 6 - chữ luôn gần đen
                            }
                            if (e.label) { e.label.fontFamily = window.__FF.Nunito; e.label.strokeColor = inkHex; }
                            if (['rectangle','diamond','ellipse'].includes(e.type)) {
                              // VÁ 6 - color= giờ chọn NỀN (fill đặc), viền luôn ink cố
                              // định (không theo tầng nữa - màu tầng chuyển hẳn sang fill).
                              e.strokeColor = inkHex;
                              e.backgroundColor = fillHex;
                              e.fillStyle = 'solid';
                              e.strokeWidth = 2;
                              e.roughness = 2;             // lệch tay rõ hơn (ROUGHNESS.cartoonist)
                              if (e.type === 'rectangle') e.roundness = { type: 3 };  // bo góc (ADAPTIVE_RADIUS)
                            }
                            // sequenceDiagram dựng khung loop/alt/opt và thanh activation
                            // bằng phần tử `line` màu #adb5bd CỨNG (đo trên toàn corpus:
                            // 34 phần tử, 7 sơ đồ, KHÔNG có type nào khác còn sót màu
                            // cứng ngoài cái này). #adb5bd cách token gần nhất (--line,
                            // #C9D4E3) 56,5 trong không gian RGB - vượt ngưỡng _NEAR=30
                            // của theme.py nên tokenize() không bao giờ đoán ra được.
                            // Dùng ĐÚNG BẰNG hex của --line (không phải `inkHex`) vì đây
                            // là NÉT KẺ CẤU TRÚC (khung chia nhóm, thanh activation),
                            // không phải nội dung mang thông tin theo tầng OSI như node -
                            // cùng vai trò với viền bảng/khung trên toàn site, nên đi cùng
                            // token --line. Roughness tăng theo để đồng bộ độ lệch tay với
                            // hình khối xung quanh.
                            if (e.type === 'line') { e.strokeColor = pal.line || inkHex; e.roughness = 2; }
                          }

                          // Convert TRƯỚC khi tính neo icon, KHÔNG sau. Container có chữ
                          // ràng buộc (containerId/boundElements) tự GIÃN kích thước ở
                          // bước convertToExcalidrawElements() để chữ (đo bằng Nunito - VÁ
                          // 2, gán fontFamily NGAY TRÊN dòng này) vẫn nằm vừa trong phần
                          // hình nội tiếp - đo THẬT: ellipse "Circle" cao 67px TRƯỚC convert,
                          // 85px SAU convert (ellipse cần khoảng đệm nhiều hơn rectangle để
                          // chữ lọt vào phần hình nội tiếp). Neo icon theo kích thước TRƯỚC
                          // bước này sẽ lệch khỏi góc thật của hình đã vẽ - bài kiểm tất
                          // định (scripts/test-excalidraw.py) bắt đúng lệch này khi rà lại.
                          //
                          // regenerateIds:false giữ nguyên id mermaid gốc (RCT/DMD/ELL...)
                          // qua bước convert để còn tìm được host bằng chính id đó ngay dưới
                          // đây - mặc định hàm này SINH ID MỚI (nanoid ngẫu nhiên) nên khoá
                          // tìm theo id sẽ trật ngay sau dòng này nếu bỏ tuỳ chọn. VÁ 5 bên
                          // dưới ghi đè lại toàn bộ id/seed nên việc giữ id mermaid ở đây
                          // không rò ra SVG cuối cùng.
                          const baseEls = window.__conv(d.elements, { regenerateIds: false });

                          // Icon neo DƯỚI-PHẢI node, kèm chú thích tên dịch vụ ngay dưới
                          // icon (bản trước đặt icon nổi phía TRÊN, không nhãn - đổi theo
                          // yêu cầu thẩm mỹ khi duyệt bản xem trước). Icon/chú thích là phần
                          // tử MỚI, chuyển bằng một lần __conv() RIÊNG (không cần
                          // regenerateIds:false - chúng không có containerId/binding gì cần
                          // giữ) rồi nối vào `baseEls`.
                          //
                          // NEO THEO ĐƯỜNG VIỀN THẬT CỦA HÌNH, KHÔNG PHẢI GÓC BOUNDING BOX -
                          // đây là lần sửa THỨ BA cho đúng một chỗ này, hai lần trước đều sửa
                          // sai chỗ (neo theo tâm ngang bbox rồi theo góc bbox) vì cả hai vẫn
                          // lấy BOUNDING BOX làm chuẩn. Với rectangle, bbox CHÍNH LÀ hình nên
                          // góc bbox là góc thật - không có gì phải sửa. Với diamond/ellipse,
                          // đường viền chỉ CHẠM bbox ở ĐÚNG BỐN ĐIỂM GIỮA CẠNH (diamond: bốn
                          // đỉnh nằm tại giữa mỗi cạnh bbox; ellipse nội tiếp: tiếp xúc bbox
                          // tại bốn điểm đó, mọi chỗ khác đường cong nằm LỌT VÀO TRONG bbox) -
                          // góc dưới-phải bbox là khoảng trống thật sự, không có cạnh hình
                          // nào ở đó, nên icon neo theo góc đó rơi vào một khoảng trắng tách
                          // rời khỏi hình, đọc như một icon lạc chứ không phải chú thích của
                          // node (đúng như ảnh chụp màn hình đã cho thấy). Neo tại ĐIỂM GIỮA
                          // CẠNH DƯỚI (cx = x+width/2, y+height) - điểm DUY NHẤT ở phía dưới
                          // mà CẢ BA dạng hình đều thật sự chạm bbox (rectangle: giữa cạnh
                          // dưới cũng nằm trên cạnh dưới của nó; diamond: đúng đỉnh dưới;
                          // ellipse: đúng tiếp điểm dưới) - nhưng RECTANGLE giữ nguyên góc
                          // dưới-phải (khác hai dạng kia) vì đó mới là chỗ "dưới-phải" đúng
                          // nghĩa của một hình chữ nhật, và brief gốc muốn icon lệch phải chứ
                          // không phải chính giữa khi hình đã có sẵn một góc thật ở đó.
                          const ICON = 24;
                          const files = Object.assign({}, d.files || {});
                          const missingIconNodes = [];
                          const mctx = document.createElement('canvas').getContext('2d');
                          mctx.font = '12px Nunito';
                          const extra = [];
                          for (const [nodeId, url] of Object.entries(ics || {})) {
                            const host = baseEls.find((e) => e.id === nodeId
                              || (e.label && e.label.text && e.id && e.id.includes(nodeId)));
                            if (!host || host.x === undefined) { missingIconNodes.push(nodeId); continue; }
                            const fid = 'ic-' + nodeId;
                            files[fid] = { id: fid, mimeType: 'image/svg+xml', dataURL: url, created: 1 };
                            const hw = host.width || 0, hh = host.height || 0;
                            // Điểm neo TRÊN ĐƯỜNG VIỀN thật (xem giải thích ở trên) - không
                            // phải một hằng số fudge được dò bằng mắt.
                            const anchor = host.type === 'rectangle'
                              ? { x: host.x + hw, y: host.y + hh }              // góc thật
                              : { x: host.x + hw / 2, y: host.y + hh };         // điểm giữa cạnh dưới
                            const ix = anchor.x - ICON / 2;
                            const iy = anchor.y - ICON / 2;
                            extra.push({ type: 'image', fileId: fid, x: ix, y: iy,
                              width: ICON, height: ICON });
                            // Chú thích canh giữa dưới icon - đo bề rộng chữ thật bằng
                            // canvas (Nunito đã nạp sẵn ở bước dàn trang chung) để không
                            // lệch trái/phải với tên dài ("Postgresql" rộng hơn icon 24px).
                            const label = (icsLabel && icsLabel[nodeId]) || '';
                            if (label) {
                              const w = mctx.measureText(label).width;
                              extra.push({ type: 'text', text: label,
                                x: ix + ICON / 2 - w / 2, y: iy + ICON + 4,
                                fontSize: 12, fontFamily: window.__FF.Nunito, strokeColor: inkHex });
                            }
                          }
                          const allEls = extra.length ? baseEls.concat(window.__conv(extra)) : baseEls;

                          // VÁ 5 · id/seed/versionNonce/updated do __conv() sinh ra đều
                          // ngẫu nhiên (Math.random) - suy tất định từ diagId (ổn định
                          // giữa các lần build) + vị trí phần tử trong mảng (ổn định
                          // trong CÙNG sơ đồ), không đụng tới random seed toàn cục nên
                          // thêm một sơ đồ mới không làm lệch id của sơ đồ khác.
                          const hash32 = (str) => {
                            let h = 0x811c9dc5;
                            for (let i = 0; i < str.length; i++) {
                              h ^= str.charCodeAt(i);
                              h = Math.imul(h, 0x01000193);
                            }
                            return h >>> 0;
                          };
                          const detInt = (...parts) => (hash32(parts.join(':')) % 2147483646) + 1;
                          const idMap = new Map();
                          allEls.forEach((e, i) => idMap.set(e.id, `${diagId}-el${i}`));
                          const remapId = (x) => idMap.get(x) ?? x;
                          allEls.forEach((e, i) => {
                            e.id = `${diagId}-el${i}`;
                            // `index` (fractional indexing, dùng để đồng bộ đa người dùng) -
                            // `baseEls` và phần tử icon/chú thích (`extra`) đi qua HAI lần
                            // gọi __conv() TÁCH BIỆT nên mỗi lần đều tự sinh index riêng bắt
                            // đầu lại từ "a0" - nối hai mảng lại có thể để lại hai phần tử
                            // trùng index. Ép về vị trí mảng CUỐI CÙNG (chuỗi đệm số 0 để so
                            // được bằng '<') cho chắc mỗi phần tử một index duy nhất, không
                            // để lại giá trị trùng từ hai lần convert độc lập.
                            e.index = String(i).padStart(6, '0');
                            e.seed = detInt(diagId, i, 'seed');
                            e.versionNonce = detInt(diagId, i, 'nonce');
                            e.updated = 0;
                            if (e.containerId) e.containerId = remapId(e.containerId);
                            if (Array.isArray(e.boundElements))
                              e.boundElements = e.boundElements.map((b) => ({ ...b, id: remapId(b.id) }));
                            if (e.startBinding)
                              e.startBinding = { ...e.startBinding, elementId: remapId(e.startBinding.elementId) };
                            if (e.endBinding)
                              e.endBinding = { ...e.endBinding, elementId: remapId(e.endBinding.elementId) };
                          });

                          // VÁ 9 · làm tròn HÌNH HỌC (không phải chuỗi SVG) về 3 chữ số thập
                          // phân - xem docstring module mục 9 cho lý do đầy đủ. Chạy TRÊN
                          // CHÍNH `allEls` (cùng mảng sẽ trả về làm `scenes[id]`) nên scene
                          // và SVG xuất ra từ cùng một bộ số đã ghim - không còn hai nguồn
                          // rời nhau như khi làm tròn chuỗi SVG sau khi xuất.
                          const _rnd3 = (v) => Math.round(v * 1000) / 1000;
                          for (const e of allEls) {
                            if (typeof e.x === 'number') e.x = _rnd3(e.x);
                            if (typeof e.y === 'number') e.y = _rnd3(e.y);
                            if (typeof e.width === 'number') e.width = _rnd3(e.width);
                            if (typeof e.height === 'number') e.height = _rnd3(e.height);
                            if (typeof e.angle === 'number') e.angle = _rnd3(e.angle);
                            if (Array.isArray(e.points))
                              e.points = e.points.map((p) => [_rnd3(p[0]), _rnd3(p[1])]);
                          }

                          // VÁ 5b · ghi đè x/y của text buộc vào container - xem docstring
                          // module mục 5 cho lý do đầy đủ (không chép lại ở đây để khỏi hai
                          // bản trôi nhau). Tóm tắt: vị trí thư viện tự tính cho text buộc vào
                          // container nhiều điểm/cong nhạy nhiễu dấu phẩy động của Chromium,
                          // không phải chuyện seed - ghi đè bằng công thức canh giữa chuẩn thì
                          // tất định tuyệt đối vì chỉ phụ thuộc hình học container + kích thước
                          // text, cả hai đã xác nhận ổn định.
                          for (const e of allEls) {
                            if (e.type !== 'text' || !e.containerId) continue;
                            const c = allEls.find((h) => h.id === e.containerId);
                            if (!c || typeof c.x !== 'number' || typeof c.width !== 'number') continue;
                            e.x = _rnd3(c.x + c.width / 2 - e.width / 2);
                            e.y = _rnd3(c.y + c.height / 2 - e.height / 2);
                          }

                          const svg = await window.__toSvg({
                            elements: allEls, files: files,
                            appState: { exportBackground: false, exportWithDarkMode: false },
                          });
                          return { svg: svg.outerHTML, elements: allEls, files: files, missingIconNodes };
                        }""",
                        {'src': src, 'pal': pal, 'fillPal': FILL_PAL, 'color': it.get('color') or 'ink',
                         'diagId': it['id'], 'ics': ics, 'icsLabel': ics_label})
                except Exception as e:
                    first = str(e).strip().split('\n')[0][:180]
                    raise SystemExit(
                        f'✗ sơ đồ Excalidraw lỗi cú pháp - {where}\n'
                        f'  {first}\n'
                        f'  ── nguồn ──\n' +
                        '\n'.join('  ' + l for l in it['src'].strip().split('\n')[:12]))
                if r.get('fallback'):
                    fallback.append((it['id'], where, r['fallback']))
                    continue
                # Icon bị bỏ qua vì node id không có thật trong sơ đồ - báo
                # lại giống hệt cách `fallback` báo, KHÔNG âm thầm bỏ qua.
                for nid in r.get('missingIconNodes') or []:
                    icon_warnings.append(
                        (it['id'], nid, f'icons= trỏ node "{nid}" không có trong sơ đồ - bỏ qua icon này'))
                svg = FONTFACE_RE.sub('', r['svg'])          # VÁ 4
                # VÁ 9 giờ chạy TRONG pg.evaluate (hình học phần tử, không phải
                # chuỗi SVG) - không còn bước làm tròn nào ở tầng Python nữa.
                svg = _FONT_DISPLAY_RE.sub(r"\1'Patrick Hand', Nunito,", svg)   # VÁ 7
                # Hook CSS ổn định cho site.css - khớp tiền lệ `.ec` của
                # echarts (engine/echarts.cjs). Trước bản vá này, site.css tạm
                # dò bằng svg[version="1.1"] (dấu hiệu tình cờ của Excalidraw,
                # không phải hợp đồng do ta kiểm soát).
                svg = svg.replace('<svg ', '<svg class="exd" ', 1)
                svg = _fix_mask_luminance(T.tokenize(svg))  # VÁ 8
                out[it['id']] = svg
                scenes[it['id']] = {'elements': r['elements'], 'files': r['files']}
            b.close()
    finally:
        page.unlink(missing_ok=True)
    return out, fallback, scenes, icon_warnings


if __name__ == '__main__':
    o, fb, sc, iw = render([
        {'id': 't1', 'where': 'test flowchart', 'color': 'l4', 'icons': '', 'src':
         'flowchart LR\n A[Client] -->|POST /pay| B(Server)\n B --> C{Đã có key?}\n'
         ' C -->|có| D[Phát lại response cũ]\n C -->|không| E[Trừ tiền]'},
        {'id': 't2', 'where': 'test sequence', 'color': 'l3', 'icons': '', 'src':
         'sequenceDiagram\n participant C as Client\n participant S as Server\n'
         ' C->>S: SYN seq=x\n S-->>C: SYN-ACK\n Note over C,S: một RTT'},
        {'id': 't3', 'where': 'test state', 'color': 'err', 'icons': '', 'src':
         'stateDiagram-v2\n [*] --> ESTABLISHED\n ESTABLISHED --> FIN_WAIT_1\n'
         ' FIN_WAIT_1 --> TIME_WAIT\n TIME_WAIT --> [*]'},
        {'id': 't4', 'where': 'test er', 'color': 'l7', 'icons': '', 'src':
         'erDiagram\n ORDER ||--o{ ORDER_ITEM : chua\n ORDER { uuid id string status }'},
    ])
    bad_any = False
    for k, v in o.items():
        left = T.audit(v)
        print(f'{k}: {len(v)}B svg={v.lstrip().startswith("<svg")} '
              f'vars={v.count("var(--")} còn-sót={left}')
        if left:
            bad_any = True
    print(f'fallback: {fb}')
    print(f'icon_warnings: {iw}')
    print('\n' + ('✗ CÒN MÀU CHƯA REMAP' if bad_any else '✓ SẠCH - mọi màu đã là token'))
