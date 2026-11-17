---
tags: [skill-creator]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Bài dưới đây đang toàn chữ, chưa có hình nào. Vẽ giúp tôi một hình Excalidraw minh hoạ cơ chế chính của bài đó, chữ trong hình bằng tiếng Việt. Lưu spec và các file xuất ra vào thư mục hinh-ve/ ở thư mục làm việc.

<bai>
import { n } from '../../../../src/course/lab'
import { soKet } from '../../viz/doc-so-lieu'
import { HinhVe } from '../../viz/HinhVe'
export const CASE = 'kafka-lag'
export const CASE_PEL = 'pel-lag'
export const P = [0, 1, 2]
export const CUR = P.map((p) => soKet(CASE, `current offset p${p}`))
export const LAG_HET = P.map((p) => soKet(CASE, `tieu thu het: lag p${p}`))
export const LOG_END = P.map((p) => soKet(CASE, `log-end p${p}`))
export const LAG = P.map((p) => soKet(CASE, `lag sau 3 key moi p${p}`))
// DAU VAO cua kich ban, khong phai so do: bo ba key gui sau khi nhom da commit.
export const BO_BA = ['k9', 'order-1001', 'user-42']
export const PART_BO_BA = BO_BA.map((k) => soKet(CASE, `partition cua ${k}`))
// CUNG MOT PHEP TRU voi nhan lag cua kich ban (log-end tru current), chi viet
// lai o day de hien phep tinh - khong phai phep kiem doc lap.
export const LAG_TINH = P.map((p) => LOG_END[p] - CUR[p])
export const TONG_LAG = LAG.reduce((a, b) => a + b, 0)
// Suy ra tu so do: log-end luc nhom vua commit = current + lag luc do.
export const END_TRUOC = P.map((p) => CUR[p] + LAG_HET[p])
export const TANG = P.map((p) => LOG_END[p] - END_TRUOC[p])
// Duong doc thu ba: partition cua bo ba doc tu ban ghi, dem moi partition nhan may key moi.
export const MOI_THEO_P = P.map((p) => PART_BO_BA.filter((x) => x === p).length)
export const TANG_KHOP = P.every((p) => TANG[p] === MOI_THEO_P[p])
// Streams, case pel-lag cua bai 4.3.
export const S_LAG_TAO = soKet(CASE_PEL, 'tao nhom tu 0: lag')
export const S_LAG_A = soKet(CASE_PEL, 'A doc 2: lag')
export const S_PENDING_A = soKet(CASE_PEL, 'A doc 2: pending')
// DAU VAO cua cau chuyen, khong phai so do.
export const SO_PARTITION_DOI = 12
export const NGUONG_TONG = 5_000
export const LAG_KET = 4_200
export const DON_MOI_PHUT = 30

Bài [8.1](/khoa-hoc/hang-doi-duoi-nap-capo/kafka-consumer/offset-cua-nhom) đọc một đầu: nhóm `nhom-lab-lag` commit {CUR.map((c) => n(c)).join('/')} rồi dừng.
Bài [4.3](/khoa-hoc/hang-doi-duoi-nap-capo/consumer-group/lag-do-lui-bao-nhieu) đã định nghĩa lag cho Redis Streams, và hứa rằng lag Kafka không phải cùng một phép tính.
Bài này đặt đầu kia vào, rồi giữ lời hứa đó.

**Trả lời: lag Kafka tính riêng từng partition, bằng log-end offset trừ offset nhóm đã commit.
Broker không trả về trường lag nào - con số đó do client tự trừ, từ hai con số đọc bằng hai request khác nhau.
Case `kafka-lag` gửi ba key mới sau khi nhóm đã commit: log-end lên {LOG_END.map((x) => n(x)).join('/')}, trừ {CUR.map((c) => n(c)).join('/')} ra lag {LAG.map((x) => n(x)).join('/')}.**

## Hai đầu, hai request

Sau bước commit của bài 8.1, kịch bản làm tiếp ba việc:

1. Producer gửi bộ ba {BO_BA.join(', ')}, từng bản một.
2. Admin hỏi broker offset mới nhất của từng partition bằng `fetchTopicOffsets` - nhóm nhãn `log-end`.
3. Kịch bản lấy số đó trừ offset của nhóm đã đọc ở bài 8.1 - nhóm nhãn `lag sau 3 key moi`.

Hai con số của phép trừ đi hai đường khác nhau.
Offset của nhóm là thứ consumer đã gửi lên bằng commit, và admin đọc lại qua `fetchOffsets` từ bộ điều phối của nhóm.
Log-end là thứ của partition, không dính gì tới nhóm nào: admin hỏi bằng request `ListOffsets`, và với topic một bản sao như lab thì đó là offset mà bản ghi kế tiếp sẽ nhận.

| Partition | log-end | current của nhóm | nhãn lag |
|---|---|---|---|
| p0 | {n(LOG_END[0])} | {n(CUR[0])} | {n(LAG[0])} |
| p1 | {n(LOG_END[1])} | {n(CUR[1])} | {n(LAG[1])} |
| p2 | {n(LOG_END[2])} | {n(CUR[2])} | {n(LAG[2])} |

Nhẩm hộ: {P.map((p) => n(LOG_END[p]) + ' - ' + n(CUR[p]) + ' = ' + n(LAG_TINH[p])).join(' · ')}.
Phép trừ này ra đúng cột nhãn lag, và điều đó **không** kiểm được gì: cột nhãn lag chính là phép trừ đó, kịch bản làm trước, bài này làm lại.
Lab không đọc một trường lag nào từ broker, vì không có trường đó để đọc.

## Phép kiểm có thật nằm ở đường thứ ba

Có một đối chiếu không phải đọc lại chính mình.
Lúc nhóm vừa commit, lag là {LAG_HET.map((x) => n(x)).join('/')}, nên log-end lúc đó bằng current: {END_TRUOC.map((x) => n(x)).join('/')}.
Sau bộ ba, log-end là {LOG_END.map((x) => n(x)).join('/')}.
Mỗi partition tăng {TANG.map((x) => n(x)).join('/')} - hai con số của admin, đọc ở hai thời điểm.

Đường thứ ba là bản ghi thật.
Kịch bản mở một nhóm đọc riêng, đọc cả topic từ đầu, và ghi partition của từng key trong bộ ba: {BO_BA.map((k, i) => k + ' ở ' + n(PART_BO_BA[i])).join(', ')}.
Đếm theo partition, mỗi partition nhận {MOI_THEO_P.map((x) => n(x)).join('/')} key mới.
Hai đường {TANG_KHOP ? 'trùng nhau' : 'không trùng nhau'}: offset của admin tăng đúng bằng số bản ghi mà consumer thấy rơi vào từng partition.

Đó là lý do cả ba partition cùng lag {n(LAG[0])}, và không phải vì Kafka chia đều.
Ba key tình cờ rơi vào ba partition khác nhau theo công thức của bài [7.3](/khoa-hoc/hang-doi-duoi-nap-capo/kafka-phan-manh/key-quyet-dinh-partition).
Gửi ba key cùng rơi vào p1 thì lag sẽ là 0/{n(TONG_LAG)}/0, tổng vẫn {n(TONG_LAG)}.

<Aha cau={'Không có trường lag nào trong Kafka để đọc. Lag ' + LAG.map((x) => n(x)).join('/') + ' là log-end ' + LOG_END.map((x) => n(x)).join('/') + ' trừ offset của nhóm ' + CUR.map((c) => n(c)).join('/') + ', hai con số từ hai request, và phép trừ là việc của client.'} />

## Hai chữ lag, hai phép tính

Bài 4.3 định nghĩa lag của một nhóm Streams là số entry đã ghi trừ số entry nhóm đã giao, và `XINFO GROUPS` trả thẳng con số đó.
Đặt cạnh nhau:

| | Redis Streams | Kafka |
|---|---|---|
| Phép tính | `entries-added` của stream trừ `entries-read` của nhóm | log-end offset trừ offset nhóm đã commit |
| Ai trừ | Redis, trả sẵn trường `lag` | client: `kafka-consumer-groups.sh`, dashboard, hoặc code của bạn |
| Phạm vi | cả stream, một số cho một nhóm | từng partition; tổng là cộng tay |
| Đã giao mà chưa xong | **không** tính vào lag, nằm ở PEL | **có** tính vào lag, vì con trỏ chỉ dời khi commit |
| Khi không tính được | tài liệu nói lag có thể là nil | thiếu offset đã commit thì không có hiệu nào để trừ |

Dòng "đã giao mà chưa xong" là chỗ hai con số lệch nhau thật.
Case `pel-lag` của bài 4.3: A đọc hai entry, lag Streams xuống {n(S_LAG_A)} từ {n(S_LAG_TAO)}, trong khi pending A là {n(S_PENDING_A)} - hai entry đó chưa xong nhưng đã ra khỏi lag.
Ở Kafka, consumer đọc mà chưa commit thì offset nhóm đứng yên, và hai bản ghi đó vẫn nằm trong lag.

Lag Kafka còn đếm bằng offset, không đếm bằng bản ghi.
Theo tài liệu Kafka, topic có giao dịch ghi thêm marker vào log và marker cũng chiếm offset, nên trên topic đó lag có thể lớn hơn số bản ghi thật còn lại.
Lab không dùng giao dịch, nên ở đây hai thứ trùng nhau.

<Callout loai="nguy-hiem" tieuDe="Đừng mang ngưỡng lag từ Streams sang Kafka, và đừng chỉ canh tổng">
Lag Streams bằng 0 vẫn có thể còn việc dở trong PEL; lag Kafka lớn hơn 0 có thể chỉ là việc đang chạy chưa kịp commit.
Và vì lag Kafka là từng partition, một partition kẹt có thể nằm lẫn trong một tổng trông bình thường.
Canh lag lớn nhất trong các partition, không chỉ canh tổng.
</Callout>

<SoDo tieuDe="Lag là khoảng giữa hai con trỏ" goi="" chu={<>Nửa trên: offset nhóm đã commit nằm ở bộ điều phối nhóm, log-end nằm ở broker giữ partition, và lag là khoảng giữa hai con trỏ đó, gồm cả hai bản ghi đã đọc mà chưa commit. Nửa dưới: cộng mười hai khoảng đó thành một tổng thì partition kẹt nằm lọt dưới ngưỡng. Offset và chiều cao cột là minh hoạ, không phải số đo.</>}>
  <HinhVe ten="kafka-consumer-lag-hai-con-tro" nhan="Hai nửa. Trên: partition p0 là dãy ô offset 40 tới 48 và ô trống 49. Bộ điều phối nhóm trả offset đã commit 44 qua fetchOffsets, broker giữ partition trả log-end 49 qua ListOffsets. Ô 40 tới 43 nhóm đã commit xong, ô 44 và 45 đã đọc nhưng chưa commit, ô 46 tới 48 chưa đọc, ô 49 là chỗ bản ghi kế tiếp. Lag bằng log-end trừ offset đã commit, 49 trừ 44 bằng 5, gồm cả hai bản ghi đã đọc; broker không trả trường lag, client tự trừ; Redis Streams thì để entry đã giao mà chưa XACK ở PEL, ngoài lag. Dưới: topic don-hang mười hai partition, cảnh báo khi tổng lag vượt 5 000. Mười một partition lag gần 0, p7 lag 4 200, tổng xấp xỉ 4 200 vẫn dưới ngưỡng nên không ai bị gọi. Sửa: cảnh báo theo lag lớn nhất trong các partition, và khi offset một partition không dời." />
</SoDo>

## Sai thì chuyện gì xảy ra

Một đội chạy dịch vụ tính phí vận chuyển trên topic `don-hang` {n(SO_PARTITION_DOI)} partition.
Các con số là giả định của câu chuyện, không phải số đo.
Cảnh báo của họ: tổng lag của nhóm vượt {n(NGUONG_TONG)} thì gọi người trực.

Một chiều thứ sáu, consumer giữ partition 7 gặp một bản ghi làm nó kẹt trong vòng thử lại, và offset của partition đó không dời nữa.
{n(SO_PARTITION_DOI - 1)} partition còn lại chạy êm, lag gần 0.
Partition 7 nhận khoảng {n(DON_MOI_PHUT)} đơn mỗi phút, và sau hơn hai tiếng lag của riêng nó là {n(LAG_KET)} - tổng vẫn dưới ngưỡng.
Không ai bị gọi.

Sáng thứ bảy, bộ phận chăm sóc khách hàng nhận hàng trăm cuộc gọi: đơn đã thanh toán mà không có phí vận chuyển, nên không đơn nào được giao cho bên vận chuyển.
Tất cả là đơn có key rơi vào partition 7.
Chỗ bất ngờ: dashboard vẫn xanh suốt đêm, vì con số nó vẽ là tổng - một phép cộng mà chính đội tự làm, xoá mất đúng thông tin cần thấy.

Bản sửa là đổi cảnh báo sang lag lớn nhất trong các partition, cộng một cảnh báo riêng khi offset của một partition không dời trong một khoảng thời gian.
Bản ghi làm consumer kẹt là chuyện của bài [9.1](/khoa-hoc/hang-doi-duoi-nap-capo/sai-thi-sao/poison-message).

<Recap>
- **Lag Kafka là log-end trừ offset nhóm đã commit, riêng từng partition:** sau bộ ba key mới, {LOG_END.map((x) => n(x)).join('/')} trừ {CUR.map((c) => n(c)).join('/')} ra {LAG.map((x) => n(x)).join('/')}.
- **Broker không có trường lag:** lab và mọi công cụ đều tự trừ; tính lại phép trừ đó rồi so với nhãn lag là đọc lại chính nó, không phải kiểm.
- **Phép kiểm có thật là đường thứ ba:** log-end tăng {TANG.map((x) => n(x)).join('/')} đúng bằng số key mới mà nhóm đọc riêng thấy ở từng partition.
- **Lag đều là do ba key rơi ba chỗ, không phải do Kafka chia đều:** partition do công thức của key chọn.
- **Streams không tính việc đã giao vào lag, Kafka thì có:** A đọc hai entry là lag Streams giảm, còn Kafka chỉ giảm khi commit.
- **Canh lag lớn nhất, không chỉ tổng:** một partition kẹt nằm lẫn được trong một tổng bình thường.
</Recap>

<CauHoi hoi="Lag của consumer group Kafka được tính thế nào, và ai tính?">
**Mỗi partition, log-end offset trừ offset nhóm đã commit; client tính, broker không trả sẵn.**

Case `kafka-lag` làm đúng như `kafka-consumer-groups.sh`:

1. Hỏi offset đã commit của nhóm - {CUR.map((c) => n(c)).join('/')}.
2. Hỏi log-end của từng partition - {LOG_END.map((x) => n(x)).join('/')}.
3. Trừ từng cặp - {LAG.map((x) => n(x)).join('/')}.

Hai số lấy ở hai thời điểm gần nhau chứ không cùng lúc, nên lag là một ước lượng của khoảnh khắc đọc.

**Điểm mấu chốt mà đa số ứng viên bỏ sót:** con trỏ của nhóm chỉ dời khi commit, nên lag Kafka gồm cả phần đã đọc mà chưa commit - khác hẳn lag của Redis Streams.
</CauHoi>

<CauHoi hoi="Lag của hệ Redis Streams bằng 0, của hệ Kafka bằng 0. Cả hai có cùng nghĩa là không còn việc gì không?">
**Không - lag Streams bằng 0 chỉ nói mọi entry đã được giao; lag Kafka bằng 0 nói mọi bản ghi đã được commit.**

Hai định nghĩa, hai điểm mù:

1. **Streams:** việc đã giao mà chưa `XACK` nằm trong PEL, ngoài lag - case `pel-lag` có pending A {n(S_PENDING_A)} trong khi lag đã giảm.
   Phải canh thêm tổng `XPENDING`.
2. **Kafka:** commit là con số dồn, nên lag 0 thật sự nghĩa là nhóm đã báo xong mọi bản ghi - miễn là code chỉ commit sau khi xử lý.

**Sai thì sao:** chuyển từ Kafka sang Streams mà giữ nguyên cảnh báo lag là mù đúng chỗ việc bị kẹt nhiều nhất - consumer chết khi đang giữ PEL.
</CauHoi>

<CauHoi hoi="Vì sao dashboard nên vẽ lag từng partition chứ không chỉ tổng lag?">
**Vì một partition chỉ có một consumer của nhóm đọc, và nó kẹt thì mọi key của partition đó dừng theo - trong khi tổng có thể vẫn nhỏ.**

Case `kafka-lag` cho thấy tổng giấu phân bố: lag {LAG.map((x) => n(x)).join('/')} có tổng {n(TONG_LAG)}, và ba key cùng rơi một partition cũng cho đúng tổng đó.

**Cách phòng:**

1. Cảnh báo theo lag lớn nhất trong các partition.
2. Cảnh báo khi offset đã commit của một partition không dời.
3. Khi điều tra, xem partition nào kẹt rồi tìm bản ghi ở ngay offset đã commit - đó thường là thủ phạm.

**Sai thì sao:** vài nghìn đơn của một partition đứng im cả đêm dưới một tổng trông bình thường.
</CauHoi>

Tới đây mỗi nhóm mới có một consumer.
Bài [8.3](/khoa-hoc/hang-doi-duoi-nap-capo/kafka-consumer/hai-consumer-chia-ba) cho hai consumer vào cùng một nhóm, và đo xem ba partition được chia ra sao.
</bai>
