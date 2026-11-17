---
tags: [skill-creator]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Bài dưới đây đang toàn chữ, chưa có hình nào. Vẽ giúp tôi một hình Excalidraw minh hoạ cơ chế chính của bài đó, chữ trong hình bằng tiếng Việt. Lưu spec và các file xuất ra vào thư mục hinh-ve/ ở thư mục làm việc.

<bai>
import { ket } from '../../viz/doc-so-lieu'

export const CASE = 'oom-exit-137'
export const EXIT = 'exit code khi vuot memory.max'

Bài [3.2](/khoa-hoc/container-duoi-nap-capo/cgroup-bo-nho/page-cache-tinh-vao) đo `memory.current` tăng lên khi ghi một file, nhưng container đó KHÔNG bị giết - 100MB cache vẫn còn cách trần 256MiB khá xa, và kernel kịp evict phần không cần tới.
Bài này đo cái xảy ra khi tổng bộ nhớ - cache cộng anonymous - THẬT SỰ vượt `memory.max`, không chỉ áp sát nó.

## Một vòng lặp, một giới hạn 16MiB

Case của bài này bật một container `--memory=16m`, rồi chạy đúng một dòng shell: một vòng lặp tăng gấp đôi một chuỗi liên tục, không dừng.
Khác với `dd` ở bài 3.2 (page cache, có thể evict), chuỗi này là bộ nhớ ANONYMOUS - vùng nhớ `sh` tự cấp phát cho chính biến của nó, không sao lưu bằng file nào cả, nên kernel không có cách nào evict nó để lấy lại RAM.

| lệnh trong container `--memory=16m` | kết quả |
|---|---|
| `a=A; while true; do a="$a$a"; done` | <code>{ket(CASE, EXIT)}</code> |

Không có ngoại lệ nào được ném ra bên trong `sh`, không có dòng log nào từ ứng dụng.
Container dừng đột ngột, và dấu vết duy nhất Docker để lại là đúng con số đó.

## 137 là 128 cộng một tín hiệu, không phải một mã lỗi riêng

Quy ước POSIX của shell: một tiến trình bị một tín hiệu giết thì mã thoát bằng 128 cộng số hiệu tín hiệu đó.
`137 - 128 = 9`, và tín hiệu số 9 là `SIGKILL` - tín hiệu DUY NHẤT trên Linux mà một tiến trình không thể bắt, không thể chặn, không thể tự dọn dẹp trước khi thoát.
Đây chính là lý do không có stack trace, không có log "đang tắt": kernel không hỏi ý kiến tiến trình, nó chấm dứt tiến trình ngay lập tức.

Vài mã thoát cùng dạng, hay gặp khi đọc log container:

| exit code | 128 + tín hiệu | ý nghĩa |
|---|---|---|
| 137 | 128 + 9 (`SIGKILL`) | OOM killer, hoặc ai đó gõ `docker kill -s SIGKILL` |
| 143 | 128 + 15 (`SIGTERM`) | dừng "êm" - tiến trình có cơ hội tự dọn trước khi thoát |
| 139 | 128 + 11 (`SIGSEGV`) | lỗi truy cập bộ nhớ trong chính code ứng dụng, không phải OOM |

`143` khác `137` đúng một bit ý nghĩa: `SIGTERM` (tín hiệu Docker gửi khi `docker stop` hay Kubernetes tắt pod bình thường) BẮT ĐƯỢC, nên ứng dụng có cơ hội đóng kết nối, flush log, rồi mới thoát.
`SIGKILL` thì không - đây là lý do một container bị OOM luôn "im lặng" theo đúng nghĩa đen, còn một container dừng êm thường để lại ít nhất một dòng log cuối.

<Aha cau="exit 137 không phải một mã lỗi ứng dụng - nó là bằng chứng một tiến trình bị SIGKILL từ BÊN NGOÀI, và SIGKILL là tín hiệu duy nhất không ai bắt được để tự log lại trước khi chết." />

## Phân biệt OOM thật với một SIGKILL thủ công

`exit 137` một mình không đủ để kết luận đó là OOM killer - `docker kill -s SIGKILL <container>` cũng cho đúng mã đó.
Docker lưu riêng một cờ để phân biệt: `docker inspect --format '{{.State.OOMKilled}}' <container>` trả về `true` CHỈ KHI kernel OOM killer là bên ra tay, không phải một người vận hành gõ lệnh.

Trên Kubernetes, `kubectl describe pod` hiện đúng cặp thông tin đó ở mục `Last State`: `Reason: OOMKilled` đi kèm `Exit Code: 137` khi cgroup thật sự đứng sau, còn một tiến trình tự thoát bằng `exit(1)` cho `Reason: Error` với một exit code khác hẳn.
Đọc `Reason`, đừng đoán chỉ từ con số exit code - hai nguyên nhân khác nhau hoàn toàn có thể cho cùng một con số `137`.

<Callout loai="nen-lam" tieuDe="Xác nhận OOM bằng cờ, đừng suy từ mỗi exit code">
`exit 137` chỉ nói "có SIGKILL", không nói "vì sao".
`docker inspect --format '{{.State.OOMKilled}}'` (hay `Reason: OOMKilled` của `kubectl describe pod`) mới nói rõ chính cgroup memory limit là nguyên nhân, tách bạch khỏi một lệnh `kill -9` thủ công hay một tiến trình giám sát bên ngoài.
</Callout>

## Sai thì chuyện gì xảy ra

Tiếp câu chuyện bài 3.2: sau khi container bị Kubernetes restart giữa giờ cao điểm, người trực mở log ứng dụng trước tiên - và không thấy gì cả, vì `SIGKILL` không cho ứng dụng kịp ghi một dòng log cuối.
Log rỗng ngay trước thời điểm crash khiến người trực nghi ngờ một lỗi hạ tầng ngẫu nhiên: mất kết nối mạng, node bị đánh giá không lành mạnh, hay một sự cố phía cloud provider - toàn những hướng điều tra không liên quan gì tới nguyên nhân thật.

Phải mất gần một giờ nhảy qua nhiều giả thuyết sai, người trực mới chạy `kubectl describe pod` và đọc đúng dòng `Last State: Terminated`, `Reason: OOMKilled`, `Exit Code: 137`.
Từ đó việc điều tra mới đi đúng hướng: không phải mạng, không phải node, mà là bộ nhớ cgroup - và bài 3.2 đã chỉ ra chính xác nơi bắt đầu tìm: `memory.stat`, không phải log ứng dụng.

Bài học không phải "log ứng dụng vô dụng" - nó là: khi mã thoát mang dấu hiệu SIGKILL, đừng tốn thời gian đọc log ứng dụng để tìm nguyên nhân, vì log đó CHẮC CHẮN không có gì.
Đi thẳng tới `Reason`/`OOMKilled` trước, rồi mới đọc `memory.stat` của lần chạy trước khi nó bị giết.

<Recap>
- **`exit 137` = 128 + 9, tín hiệu `SIGKILL`.** Không phải một mã lỗi ứng dụng - đây là bằng chứng một tiến trình bị chấm dứt từ bên ngoài, không có cơ hội tự dọn.
- **`SIGKILL` không bắt được, nên không có log, không có stack trace.** So sánh với `exit 143` (`SIGTERM`, bắt được, dừng êm) làm rõ vì sao container bị OOM luôn "im lặng".
- **`exit 137` một mình không chứng minh được đó là OOM.** `docker kill -s SIGKILL` cho cùng mã đó - phải đọc `docker inspect --format '{{.State.OOMKilled}}'` hoặc `Reason: OOMKilled` của `kubectl describe pod` để xác nhận cgroup memory limit đúng là nguyên nhân.
- **Log ứng dụng không giúp gì khi mã thoát mang dấu SIGKILL.** Đi thẳng tới `Reason`/`OOMKilled`, rồi tới `memory.stat` (bài 3.2), tiết kiệm cả giờ điều tra sai hướng.
</Recap>

<CauHoi hoi="Container của bạn thoát với exit code 137, nhưng bạn không chắc đó là OOM killer hay ai đó gõ tay docker kill -9. Kiểm bằng cách nào?">
**Đọc cờ `OOMKilled` của Docker, đừng suy diễn từ riêng con số exit code.**

`docker inspect --format '{{.State.OOMKilled}}' <container>` trả về `true` chỉ khi kernel OOM killer thật sự can thiệp vì cgroup chạm `memory.max`.
Một `docker kill -s SIGKILL` thủ công cho đúng `exit 137` giống hệt, nhưng cờ này vẫn là `false`, vì cgroup không hề bị chạm giới hạn.

**Trên Kubernetes:** `kubectl describe pod <pod>` hiện thông tin tương đương ở mục `Last State` - `Reason: OOMKilled` là dòng cần tìm, đứng cùng `Exit Code: 137`.

**Điểm mấu chốt mà nhiều người bỏ sót:** `137` chỉ nói "có SIGKILL", nó không tự nói "vì sao".
Hai nguyên nhân hoàn toàn khác nhau - cgroup memory limit, và một người vận hành gõ lệnh - có thể cho ra CÙNG MỘT exit code, và chỉ có cờ `OOMKilled` (hay `Reason` trên Kubernetes) mới tách bạch được hai trường hợp đó.
</CauHoi>
</bai>
