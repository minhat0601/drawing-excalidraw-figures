# drawing-excalidraw-figures

Biến một ý tưởng kỹ thuật thành hình Excalidraw nét vẽ tay - thật, chỉnh được, theo theme sáng/tối.
Skill cho Claude Code (hoặc agent nào đọc được SKILL.md): bạn đưa một đoạn văn kỹ thuật, agent viết spec JSON ngắn, chạy `ve.py`, ra bốn file.

```
fig.excalidraw   cảnh gốc - kéo vào excalidraw.com để sửa tiếp
fig.svg          SVG tĩnh, màu theo token var(--token), chạy theme sáng lẫn tối
fig-light.png    bản xem trước ở cột đọc 666px, theme sáng
fig-dark.png     bản xem trước, theme tối
```

## Luật chịu lực

**Vẽ HÌNH DẠNG của ý tưởng, không vẽ danh sách thành phần.**
Một hàng hộp chữ nhật nối mũi tên chỉ nói "A gọi B" - điều một câu văn đã nói xong.
Hình tốt làm cho thời gian thành độ dài, dữ liệu thành ô có giá trị thật, giới hạn thành một đường kẻ, sự cố thành một nét đỏ.

Skill rút ra từ khoảng 600 hình Excalidraw thật của Hello Interview và bộ mẫu của chủ sở hữu:
không đoán, mọi luật đều có nguồn ghi trong `references/sources.md`.

## Quy trình sáu bước

1. Viết đúng một câu: "Nhìn hình này, người đọc THẤY ... mà đoạn văn không cho thấy." Không viết được câu đó thì không vẽ.
2. Ghi danh sách sự thật: actor, bước, nhánh lỗi, số thật lấy nguyên từ nguồn.
3. Chọn loại hình theo cái cần thấy (sequence, swimlane, state, ER, byte cells, timeline, threshold...).
4. Viết spec JSON - chép template từ `examples/`, không viết từ đầu.
5. Render bằng `ve.py`.
6. Mở cả hai PNG ra soi, sửa tới khi hình nói được câu của bước 1. Tool xanh chưa có nghĩa là hình đọc được.

## Cài đặt

Yêu cầu: Python 3.11+, Playwright Chromium, và font nằm sẵn trong `assets/fonts/` (không tải gì từ mạng lúc render).

```bash
git clone https://github.com/nv-minh/drawing-excalidraw-figures.git
cd drawing-excalidraw-figures
pip install -r requirements.txt
python3 -m playwright install chromium

# chạy thử ngay một ví dụ có sẵn
python3 scripts/ve.py examples/03-byte-cells.json --out /tmp/fig
open /tmp/fig/03-byte-cells-light.png
```

Để Claude Code dùng như skill, đặt cả thư mục vào thư mục skill của bạn:

```bash
mkdir -p ~/.claude/skills
cp -R drawing-excalidraw-figures ~/.claude/skills/
```

`ve.py` tự tìm thư mục `engine/` đi lên từ vị trí của nó, nên đặt ở `.claude/skills/` của người dùng hay của một dự án lớn hơn đều chạy được.

## Spec trong 30 giây

```json
{
  "_": "Người đọc THẤY pool 10 connection không đủ cho 14 request, 4 request timeout ở giây 2 trước khi connection đầu tiên trả lại ở giây 3.",
  "elements": [
    {"t":"axis","x":60,"y":352,"length":510,"gap":170,"ticks":["0s","1s","2s","3s"],"label":"t"},
    {"t":"span","x1":60,"x2":570,"y":28,"text":"10 request giữ connection 3s mỗi query · pool = 10","color":"muted"},
    {"t":"cells","id":"q","x":60,"y":46,"cw":510,"ch":13,"labels":["","","","","","","","","",""],"fill":"warn","fillStyle":"hachure"}
  ]
}
```

Chạy `python3 scripts/ve.py spec.json` là ra bốn file.
Cú pháp đầy đủ của mọi phần tử: `references/spec.md`.

## Hai mươi lăm loại hình có template sẵn

`examples/` chứa 25 template: request flow, anatomy, byte cells, timeline, threshold, before/after, two views, ẩn dụ vật lý, failure branch, decision tree, sequence (kể cả alt/opt/loop), state machine, ER table, hash ring, code evidence, layer lanes, progressive series, layer stack, curve, icon, swimlane, composite state, ER crow's foot, system two flows.

Mỗi template là một spec JSON chạy được, nhãn tiếng Việt.

## Màu là nghĩa

Mặc định nét `ink`, không tô nền.
Tối đa ba màu nhấn một hình: `err` cho thứ hỏng, `node` cho kết quả đúng, `l4` cho thứ đang được bàn tới, `warn` cho vùng bị ảnh hưởng, `hot` cho đường đi của một request.
Màu chỉ nhận tên token, công cụ từ chối mã hex - nhờ vậy hình không bao giờ lệch palette và tự đảo đúng ở dark mode.

## Tool tự kiểm những gì

Lỗi cứng (`✗`): hộp bị Excalidraw phình vì chữ không vừa, chữ tràn khung, chữ nhỏ hơn 8px trên màn hình, màu không phải token.
Nhắc nhẹ (`•`): mũi tên xuyên hộp, nhãn dài bằng mũi tên, đầu mũi tên trùng điểm xuất phát của mũi tên khác, hơn ba màu nhấn, hình toàn hộp nối mũi tên.
Còn hình có nói đúng chuyện hay không thì chỉ mắt người kiểm tra được - đó là bước 6.

## Bốn model vẽ cùng một bộ đề

Skill đã được bốn model (Sonnet 5.5, Opus 5.5, Fable 5.2, GLM 5.3) vẽ cùng tám đề - sequence có nhánh, swimlane nghiệp vụ, state lồng nhau, ER crow's foot, system design hai luồng, dải ô byte, ngưỡng và thời gian, trục thời gian.
Xem đủ 32 hình ở [trang so sánh](https://nv-minh.github.io/drawing-excalidraw-figures/#so-sanh), kèm số vòng render và kích thước từng hình.

## Cấu trúc repo

```
SKILL.md            bản dẫn đầy đủ của skill - agent đọc file này
scripts/ve.py       renderer: spec JSON -> 4 file
engine/             engine render thật (Excalidraw + Playwright Chromium)
.cache/             bundle Excalidraw dựng sẵn; dựng lại bằng scripts/excalidraw-bundle.mjs
assets/             icons.json 130 icon + font Nunito, Patrick Hand, IBM Plex Mono
references/         luật loại hình, cú pháp spec, ngôn ngữ hình, checklist soi hình
examples/           25 template spec JSON
evals/              bộ đề đánh giá
docs/               landing page + bộ so sánh bốn model
```

## Nguồn và giấy phép

- Thư viện [Excalidraw](https://excalidraw.com) và `@excalidraw/mermaid-to-excalidraw`: MIT.
- Icon trong `assets/`: xem `assets/ICONS-LICENSE.txt`.
- Nguồn các luật hình học và phong cách: `references/sources.md`.
- Bản chất mọi luật trong skill đều ghi kèm phép đo thật đã tiến hành trên corpus, không phải suy đoán.
