---
tags: [skill-creator]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Bài dưới đây đang toàn chữ, chưa có hình nào. Vẽ giúp tôi một hình Excalidraw minh hoạ cơ chế chính của bài đó, chữ trong hình bằng tiếng Việt. Lưu spec và các file xuất ra vào thư mục hinh-ve/ ở thư mục làm việc.

<bai>
Bài trước để lại một chi tiết chưa khai thác: ảnh chụp được lấy lúc nào.

`READ COMMITTED` lấy lại ảnh chụp ở mỗi câu lệnh.
`REPEATABLE READ` lấy một lần cho cả transaction.

Nghe như chuyện học thuật. Nó không phải.
Bài này chạy thật ba kịch bản làm hỏng dữ liệu, ở cả hai mức, để thấy khác biệt đó biến thành tiền mất như thế nào.

## Bốn mức, và mức bạn đang dùng

| Mức | Postgres làm gì | Ai dùng |
|---|---|---|
| `READ UNCOMMITTED` | Postgres coi như `READ COMMITTED` | không ai |
| `READ COMMITTED` | ảnh chụp mới ở **mỗi câu lệnh** | **mặc định**, gần như mọi app |
| `REPEATABLE READ` | một ảnh chụp cho **cả transaction** | báo cáo, job đọc nhiều bảng |
| `SERIALIZABLE` | như trên, cộng phát hiện xung đột thật | chỗ dữ liệu phải tuyệt đối đúng |

Nếu bạn chưa bao giờ gõ `SET TRANSACTION ISOLATION LEVEL`, bạn đang ở `READ COMMITTED`.
Prisma, TypeORM, Sequelize, Rails, Django: tất cả đều để nguyên mặc định của server.

## Dị thường 1: mất bản ghi

Kịch bản tầm thường nhất thế giới. Hai request cùng trừ tiền một ví.

Tầng ứng dụng đọc số dư lên, tính trong JavaScript, rồi ghi số mới xuống - đúng cái mà mọi ORM khuyến khích bạn viết:

```js
const vi = await repo.findOne({ where: { id: 1 } })   // đọc 100
vi.so_du = vi.so_du - 10                              // tính ở đây
await repo.save(vi)                                   // ghi 90
```

<BienBan id="iso-mat-ban-ghi" />

Hai người trừ, một người 10 và một người 20, từ số dư 100.
Đúng ra phải còn 70. Kết quả còn **80**.

Phép trừ 10 đồng của A bốc hơi, và **không có một dòng lỗi nào** ở bất kỳ đâu.
Cả hai request đều trả về 200 OK.

Bước 6 và 7 cho thấy Postgres không hề thờ ơ: nó **có** chặn B lại.
B nằm chờ đúng lúc A đang giữ dòng đó, và bước 7 nhìn từ ngoài vào thấy A ở trạng thái `idle in transaction` - A không chạy gì cả, nó chỉ đang giữ khoá trong lúc code phía ứng dụng làm việc khác.

Nhưng chặn xong rồi thì B vẫn được phép ghi đè, vì B ghi một hằng số 80 mà nó tính từ số dư đã cũ.
Postgres không có cách nào biết số 80 đó được suy ra từ dữ liệu nào.

<Aha cau="Postgres không mất dữ liệu của bạn. Tầng ứng dụng đọc một số ra, quên nó ở đó quá lâu, rồi ghi đè bằng thứ tính từ số cũ.">
Đây là loại hỏng khó phát hiện nhất, vì không có lỗi, không có log, không có cảnh báo.
Bạn chỉ biết khi có người kêu số dư sai, thường là vài tuần sau.
</Aha>

### Cách sửa rẻ nhất: đừng mang số ra khỏi database

<BienBan id="iso-tru-trong-sql" />

Không đổi isolation level, không thêm khoá, không thêm một dòng code xử lý lỗi nào.
Chỉ đổi chỗ đặt phép trừ.

```sql
UPDATE vi SET so_du = so_du - 10 WHERE id = 1;
```

Kết quả: **70**. Đúng.

Cơ chế: ở `READ COMMITTED`, khi B hết bị chặn, Postgres **đọc lại** dòng đã đổi rồi mới áp câu lệnh lên phiên bản mới nhất.
Vì giá trị cần đọc nằm trong chính câu lệnh chứ không nằm trong biến của ứng dụng, lần đọc lại đó cứu được phép tính.

<Callout loai="nen-lam" tieuDe="Ba cách sửa, theo thứ tự nên thử">
**1. Để phép tính trong SQL.** `SET so_du = so_du - 10`. Không tốn gì, không phải retry.

**2. `SELECT ... FOR UPDATE`.** Khi thật sự cần đọc lên rồi mới quyết định. Khoá dòng ngay từ lúc đọc, người thứ hai chờ.

**3. Nâng isolation level.** Khi luật cần bảo vệ nằm vắt ngang nhiều dòng, nên không có dòng nào để khoá.
</Callout>

### Cùng kịch bản, nâng lên REPEATABLE READ

<BienBan id="iso-mat-ban-ghi-rr" />

Lần này B không âm thầm ghi đè.
Nó nhận lỗi `40001` với câu `could not serialize access due to concurrent update`.

Nghĩa là: "dòng anh định ghi đã bị người khác đổi sau khi anh chụp ảnh. Tôi không đoán được ý anh, anh làm lại từ đầu đi."

Số dư còn 90 - tức là chỉ phép trừ của A có hiệu lực, còn của B thì bị huỷ hẳn.
Đúng, nhưng chỉ đúng **nếu tầng ứng dụng biết bắt `40001` và chạy lại**.

<Callout loai="nguy-hiem" tieuDe="Nâng isolation level mà không viết vòng lặp thử lại là đổi một lỗi âm thầm lấy một lỗi ồn ào">
`40001` không phải bug, nó là hợp đồng: database nói "tôi từ chối, anh thử lại".
Không thử lại thì người dùng nhận HTTP 500 ở đúng những lúc hệ thống đông nhất.

```js
for (let lan = 0; lan < 3; lan++) {
  try { return await chay() }
  catch (e) { if (e.code !== '40001' && e.code !== '40P01') throw e }
}
```

Chờ ngẫu nhiên vài chục mili-giây giữa các lần thử, nếu không cả hai bên sẽ lại đâm vào nhau đúng như cũ.
</Callout>

## Dị thường 2: bóng ma

Lần này A không sửa gì cả. A chỉ đếm, hai lần, trong cùng một transaction.

<BienBan id="iso-bong-ma" />

Hai câu `SELECT count(*)` giống hệt nhau, trong cùng một transaction, ra **2 rồi 3**.

Mọi logic kiểu "đếm xem đủ chỗ chưa rồi mới cho đặt thêm" đều vỡ ở đây.
Số bạn vừa đếm đã cũ ngay khi câu lệnh tiếp theo chạy.

<BienBan id="iso-bong-ma-rr" nhan="Cùng kịch bản, chỉ thêm ISOLATION LEVEL REPEATABLE READ vào câu BEGIN." />

Ở `REPEATABLE READ`, A đếm hai lần đều ra 2.
Dòng của B đã nằm sẵn trên đĩa từ bước 3, A chỉ đơn giản là không được phép thấy nó.

Bước 6, sau khi commit, A lấy ảnh chụp mới và thấy đủ 3.

<Callout loai="quy-tac" tieuDe="Postgres chặt hơn chuẩn SQL đúng ở chỗ này">
Chuẩn SQL cho phép `REPEATABLE READ` vẫn còn bóng ma, và MySQL/InnoDB thì chống bóng ma bằng gap lock - một cơ chế khác hẳn, có giá riêng của nó.

Ở Postgres, `REPEATABLE READ` là ảnh chụp thật nên bóng ma **không thể xảy ra**, và không tốn thêm khoá nào.

Đây là một trong những chỗ kiến thức Postgres không mang thẳng sang MySQL được. Phụ lục cuối khoá liệt kê đủ.
</Callout>

## Dị thường 3: lệch ghi

Cái này mới là cái khó chịu, vì `REPEATABLE READ` **không** chặn được nó.

Hai bác sĩ đang trực. Luật: lúc nào cũng phải còn ít nhất một người.
Mỗi người mở app, thấy "đang có 2 người trực", và bấm rời ca.

<BienBan id="iso-lech-ghi" />

Cả hai đều kiểm tra đúng luật trước khi ghi.
Cả hai đều thấy 2 người đang trực.
Cả hai đều commit thành công, không ai nhận lỗi.

Kết quả: **0 người trực**.

Lý do `REPEATABLE READ` bó tay: A sửa dòng của An, B sửa dòng của Bình.
**Hai dòng khác nhau** nên không có khoá nào va chạm, không có phiên bản nào bị ghi đè.
Thứ bị phá là một luật vắt ngang cả bảng, và ảnh chụp không biết gì về luật đó.

Đây cũng là lý do không có chỗ nào để đặt `SELECT FOR UPDATE`: dòng cần khoá là **dòng chưa tồn tại**, tức là "trạng thái của cả bảng".

### SERIALIZABLE

<BienBan id="iso-lech-ghi-ss" />

Đổi hai chữ trong câu `BEGIN`.
A commit trót lọt, B nhận `40001` với lý do khác hẳn lần trước: `read/write dependencies among transactions`.

Postgres theo dõi cả những dòng transaction chỉ **đọc** chứ không sửa.
Nó thấy A đã đọc dòng của Bình rồi B lại sửa dòng đó, và ngược lại - một vòng phụ thuộc không thể xếp thành thứ tự nối tiếp.
Không xếp được thì huỷ một bên.

Kết quả cuối: **1 người trực**. Luật được giữ.

## Mức nào chặn được gì

Tổng kết, mọi ô đều từ những kịch bản vừa chạy ở trên:

| | Mất bản ghi | Bóng ma | Lệch ghi |
|---|---|---|---|
| `READ COMMITTED` | không chặn | không chặn | không chặn |
| `REPEATABLE READ` | chặn bằng `40001` | chặn | **không chặn** |
| `SERIALIZABLE` | chặn bằng `40001` | chặn | chặn bằng `40001` |

Cột thứ ba là cột đáng nhớ: **giữa `REPEATABLE READ` và `SERIALIZABLE` có một khoảng trống thật**, và nó chính là chỗ các luật nghiệp vụ hay rơi vào.

## Chọn thế nào, từ ghế dev

**Giữ `READ COMMITTED` cho hầu hết mọi thứ.** Nó là mặc định vì nó đúng cho phần lớn request, và nó không bắt bạn viết vòng lặp thử lại.

**Đừng mang giá trị ra khỏi database rồi ghi lại.** `SET x = x + 1` xử lý được đa số trường hợp mà không cần đổi gì khác.

**Dùng `SELECT ... FOR UPDATE`** khi buộc phải đọc lên rồi mới quyết định. Nó khoá đúng dòng, và người thứ hai chờ thay vì ghi đè.

**Nâng lên `SERIALIZABLE`** khi luật cần bảo vệ nằm vắt ngang nhiều dòng: kiểm tra số dư trước khi rút, đếm chỗ trống trước khi đặt, xét trùng lịch trước khi tạo.
Nhớ kèm vòng lặp thử lại.

**Đừng để transaction mở trong lúc gọi API ngoài.**
Bước 7 của kịch bản đầu tiên cho thấy hậu quả: một transaction `idle in transaction` giữ khoá suốt thời gian nó ngủ, và mọi người khác xếp hàng phía sau.

<Recap>
- **`READ COMMITTED` lấy ảnh chụp mới ở mỗi câu lệnh**, nên hai câu `SELECT` giống nhau có thể ra hai kết quả.
- **Mất bản ghi xảy ra ở tầng ứng dụng**, và cách sửa rẻ nhất là để phép tính trong SQL.
- **`REPEATABLE READ` của Postgres chặn được bóng ma** nhưng không chặn được lệch ghi.
- **`SERIALIZABLE` chặn nốt phần còn lại**, đổi lại bạn phải xử lý `40001`.
</Recap>

<CauHoi hoi="Vì sao lỗi 40001 lại là tin tốt?">
Vì nó là loại hỏng duy nhất mà bạn **nhìn thấy được**.

Ba kịch bản trong bài này đều là cùng một vấn đề: hai transaction đè lên nhau.
Ở `READ COMMITTED` thì dữ liệu sai âm thầm, ứng dụng trả về 200 OK, và bạn phát hiện ra sau vài tuần khi có người kêu.
Ở mức cao hơn thì Postgres từ chối, ném ra một mã lỗi, và chỗ hỏng lộ ra ngay tại chỗ.

Điều kiện là bạn phải bắt nó và thử lại.
Một `40001` không được xử lý chỉ đơn giản là đổi một lỗi âm thầm lấy một lỗi ồn ào, chứ chưa sửa được gì.
</CauHoi>

Bài tiếp theo đi vào thứ đứng phía sau mọi lần "bị chặn" ở trên: khoá.
Ai chờ ai, chờ cái gì, và làm sao hai transaction tự treo nhau đến mức Postgres phải bắn chết một bên.
</bai>
