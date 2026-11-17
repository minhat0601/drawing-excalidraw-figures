# Tổng hợp tài liệu Excalidraw: system design, sequence, luồng nghiệp vụ, state (kèm sơ đồ mẫu tự làm)

Cập nhật: 2026-11-17. Mức kiểm chứng: [Đã mở] = đã đọc trang; [Từ search] = chỉ thấy trong kết quả tìm kiếm, chưa mở.

## A. File .excalidraw thật để học cách người khác vẽ

| Nguồn | Nội dung | Kiểm chứng |
|---|---|---|
| https://github.com/karanpratapsingh/system-design (thư mục `diagrams/`, vd `rate-limiting.excalidraw`) | Repo system design nổi tiếng (~46.9k sao), có thư mục diagrams; xác nhận có file .excalidraw qua kết quả search | Đã mở repo; file cụ thể [Từ search] |
| https://github.com/Prakash-sa/system-design-ultimatum | Thư viện sơ đồ Excalidraw theo nhóm: nội dung/media, mạng xã hội, search, storage, analytics/streaming, security, DevOps, AI patterns, HPC; có `Libraries/`, `Notes/`, file gộp `system_design_all.excalidraw`. MIT (code), CC BY 4.0 (nội dung) | Đã mở |
| https://github.com/enkr1/interview_preparation_system_design_excalidraw_examples | Fork của swaymun/system-design-excalidraws: TinyURL, WhatsApp, Netflix, Newsfeed, Google Maps, Nearby Friends, Ticketmaster, File Storage, Tweet Search... (gắn nguồn: Jordan Has No Life, Alex Xu SDI v2, System Design Fight Club, Hello Interview). Không thấy license, nên chỉ dùng để học | Đã mở |
| https://github.com/Everoot/System-Design/blob/main/Design%20A%20Rate%20Limiter.excalidraw | Một sơ đồ rate limiter | [Từ search] |
| https://github.com/Nilay1999/system-design-diagrams | Sơ đồ system design | [Từ search], chưa đọc được (bị rate limit) |
| https://github.com/sanket7474/system-design-lab | System design lab | [Từ search], chưa đọc được (bị rate limit) |
| https://www.teamblind.com/post/sharing-my-system-design-excalidraws-ojhwogam | Bài chia sẻ bộ Excalidraw system design | [Từ search] |

## B. Thư viện shape (.excalidrawlib) để vẽ nhanh và đồng nhất

| Nguồn | Nội dung | Kiểm chứng |
|---|---|---|
| https://github.com/DeKinci/sysdeslib | Service, DB (relational, document, KV, graph, time-series, vector, columnar), queue, object storage, CQRS, load balancer, DNS, proxy, observability, retry/rate limiter/circuit breaker/outbox; thiết kế để đẹp cả ở style strict lẫn sloppy, mũi tên bám tốt | Đã mở (qua mirror) |
| https://github.com/Dinesh-Sunny/excalidraw-system-design-kit | Library tìm kiếm được (Ctrl/Cmd + /): interview notes, clients, edge/network, services, data stores, cache, messaging, AI/RAG/agents, trust boundary, pattern và thiết kế hoàn chỉnh. MIT. Số item trong trang không nhất quán (292 / 458; 21 / 52 designs) | Đã mở |
| https://github.com/aretecode/system-design-templates-excalidraw | Shape rough/emoji cho front-end, back-end, distributed. MIT | Đã mở |
| https://github.com/excalidraw/excalidraw-libraries/pull/462 | AWS Architecture Icons (Anna Pastushko): S3, RDS, DynamoDB, Lambda, SQS, SNS, VPC, CloudFront... (sau đó được tách thành 2 library) | Đã mở |
| https://libraries.excalidraw.com | Thư mục thư viện công khai (MIT). Trang cần JS nên tôi không đọc được danh sách; hãy mở bằng trình duyệt | Đã mở nhưng không có danh sách |
| https://github.com/excalidraw/excalidraw-libraries | Repo nguồn của thư mục trên | [Từ search] |

## C. Hướng dẫn / nguyên tắc vẽ (phù hợp làm input cho skill)

| Nguồn | Nội dung chính | Kiểm chứng |
|---|---|---|
| https://tessl.io/registry/skills/github/coleam00/excalidraw-diagram-skill/excalidraw-diagram | Một skill mẫu về Excalidraw: "isomorphism test" (bỏ chữ vẫn hiểu cấu trúc), "education test" (dùng ví dụ/format thật), multi-zoom, ít hơn ~30% text nằm trong container, hình khối mang ý nghĩa (ellipse = start/end, diamond = quyết định), palette cố định, roughness 0, stroke 1/2/3, mọi quan hệ phải có mũi tên, render PNG rồi sửa 2-4 vòng | Đã mở |
| https://plus.excalidraw.com/use-cases/software-architecture-diagram | Hướng dẫn chính thức: chọn pattern (layered, microservices, MVC, client-server), giữ đơn giản, xin feedback sớm, màu/font nhất quán, phím tắt Ctrl/Cmd+Mũi tên | Đã mở |
| https://github.com/github/awesome-copilot (skill `excalidraw-diagram-generator`) | Skill sinh file .excalidraw từ mô tả | [Từ search] |
| https://www.designgurus.io/answers/detail/tips-for-drawing-effective-diagrams-during-system-design-discussions | Mẹo vẽ sơ đồ khi thảo luận system design | [Từ search] |
| https://algomaster.io/learn/system-design-interviews/diagramming-tips | Mẹo vẽ sơ đồ cho phỏng vấn | [Từ search] |
| https://formation.dev/blog/how-to-create-clear-effective-technical-diagrams | Cách tạo sơ đồ kỹ thuật rõ ràng | [Từ search] |
| https://www.tryexponent.com/courses/software-engineering/system-design-interviews/whiteboarding | Kỹ thuật whiteboard | [Từ search] |
| https://handbook-hld.pages.dev/curriculum/interview-framework/diagramming-skills/ | Kỹ năng vẽ sơ đồ HLD | [Từ search] |

## Gợi ý dùng làm input cho skill
1. Lấy 5-10 file .excalidraw từ nhóm A, phân tích bố cục (hướng luồng, nhóm, màu, cách đặt nhãn mũi tên) và rút thành quy tắc.
2. Dùng nhóm B làm bộ biểu tượng chuẩn để skill vẽ đồng nhất.
3. Đưa nhóm C vào phần nguyên tắc/kiểm tra chất lượng (isomorphism test, render và chỉnh lặp).
4. Kiểm tra license trước khi tái sử dụng nguyên file; repo không có license thì chỉ dùng để học.

## D. Sequence, luồng nghiệp vụ, state (bổ sung 2026-11-17)

| Nguồn | Nội dung | Kiểm chứng |
|---|---|---|
| https://plus.excalidraw.com/use-cases/sequence-diagram | Hướng dẫn vẽ sequence: lifeline, activation box, sync/async/return/self message, create/destroy, khung alt/opt/loop; mẹo giảm return message, mỗi sơ đồ một mục tiêu; có link template thành phần (excalidraw.com/#json=k7WWW7YVXimGF8ZmicIY8,BExBs1nljtieIA0D9myDnA) | Đã mở |
| https://plus.excalidraw.com/use-cases/uml-diagram | Class, activity, sequence, state, dùng chung ví dụ CI/CD (Queued → Running → Passed → Deploying → Deployed, Failed/Cancelled/Blocked); template UML (excalidraw.com/#json=EImvP9bnLMkx01CZA6TCh,4WTEkvIR1qX8ZbAjSlYEkA) và board read-only (link.excalidraw.com/readonly/8wJozUMB8Zh2GqszEg9G) | Đã mở |
| https://plus.excalidraw.com/use-cases/flowchart | 4 loại flowchart (process, swimlane, data, decision), mẹo giữ đơn giản và dùng shape nhất quán; không có template tải về | Đã mở |
| https://www.npmjs.com/package/@grethel-labs/excaliplant (README qua cdn.jsdelivr.net/npm/@grethel-labs/excaliplant@0.19.5/README.md) | Chuyển PlantUML (sequence, state, activity có swimlane/fork/alt/loop) sang file .excalidraw; MIT. Dùng để sinh sơ đồ mẫu có bố cục chuẩn | Đã mở README |
| https://wildandfreetools.com/blog/excalidraw-miro-figma-sequence-diagram-alternatives/ | Nhận xét: vẽ sequence thủ công mất 10-15 phút, Mermaid-to-Excalidraw nhanh hơn | Đã mở (blog bên thứ ba) |
| Excalidraw: More tools → "Mermaid to Excalidraw" / "Text to diagram" | Dán Mermaid (sequenceDiagram, stateDiagram, flowchart) để ra sơ đồ phong cách Excalidraw | Theo trang hướng dẫn chính thức |

Lưu ý: chưa tìm thấy repo công khai nào chứa nhiều file .excalidraw về sequence/luồng nghiệp vụ như nhóm A. Nguồn thực tế nhất là các template chính thức ở trên, kết hợp Mermaid/PlantUML để sinh sơ đồ mẫu.

## E. Sơ đồ mẫu tự làm (sinh bằng excaliplant từ PlantUML, đã render PNG và xem lại)

File nằm trong thư mục `excalidraw-samples/`: mỗi sơ đồ có `.puml` (nguồn), `.excalidraw` (mở/chỉnh trong excalidraw.com) và `.png` (ảnh kiểm tra).

### E1. Sequence: Checkout (`01-checkout-sequence`)
Nguồn PlantUML:
```
@startuml
title Checkout - Sequence
actor Customer
participant "Web App" as Web
participant "Order Service" as Order
participant "Payment Service" as Pay
database "Orders DB" as DB
queue "Event Bus" as Bus

Customer -> Web : Click "Place order"
Web -> Order : POST /orders
Order -> DB : Insert order (PENDING)
Order -> Pay : Charge(orderId, amount)
alt payment approved
  Pay --> Order : approved
  Order -> DB : Update status = PAID
  Order -> Bus : publish OrderPaid
  Order --> Web : 201 Created
  Web --> Customer : Show confirmation
else payment declined
  Pay --> Order : declined
  Order -> DB : Update status = FAILED
  Order --> Web : 402 Payment Required
  Web --> Customer : Show retry
end
@enduml
```
Kết quả: 6 lifeline, icon riêng cho actor/database/queue, khung `alt` có hai nhánh thành công và thất bại, return message nét đứt.

### E2. Luồng nghiệp vụ có swimlane: Order fulfilment (`02-order-activity`)
Nguồn PlantUML:
```
@startuml
title Order fulfilment - Business flow
|Customer|
start
:Place order;
|System|
:Validate order;
if (Stock available?) then (yes)
  :Reserve stock;
  :Request payment;
  if (Paid?) then (yes)
    |Warehouse|
    :Pick and pack;
    :Ship;
    |System|
    :Send tracking email;
  else (no)
    :Release stock;
    :Notify customer;
  endif
else (no)
  :Notify out of stock;
endif
stop
@enduml
```
Kết quả: 3 swimlane (Customer, System, Warehouse), decision dùng màu vàng khác với bước xử lý màu xanh, nhánh yes/no có nhãn.

### E3. State machine: Order (`03-order-state`)
Nguồn PlantUML:
```
@startuml
[*] --> Created
Created --> PendingPayment : submit
PendingPayment --> Paid : payment_ok
PendingPayment --> Failed : payment_declined
PendingPayment --> Cancelled : timeout / user_cancel
Paid --> Shipped : ship
Shipped --> Delivered : delivered
Paid --> Refunded : refund
Delivered --> Refunded : refund
Failed --> [*]
Cancelled --> [*]
Refunded --> [*]
@enduml
```

### Bài học rút ra khi tự làm (dùng được làm quy tắc cho skill)
1. **Đặt tên theo sự kiện thật**: nhãn chuyển trạng thái như `payment_ok`, `timeout / user_cancel`, và message như `POST /orders`, `402 Payment Required` làm sơ đồ dạy được nhiều hơn nhãn chung chung.
2. **Phân biệt bằng hình và màu**: bước xử lý (xanh), decision (vàng), start/end (đen), khung điều kiện `alt` (tím). Mỗi loại một dấu hiệu nhất quán.
3. **Một sơ đồ một mục tiêu**: happy path và lỗi nằm trong cùng khung `alt`, còn vòng đời trạng thái tách sang sơ đồ state riêng.
4. **Giới hạn của việc tự sinh bố cục** (cần chỉnh tay sau khi sinh):
   - `title` không được hỗ trợ trong sơ đồ state của excaliplant: nó bị đọc thành hai state "title Order" và "State machine". Cách xử lý: bỏ `title` và đặt tiêu đề bằng text riêng trong Excalidraw.
   - State diagram sinh ra có dạng cột dọc rất dài, và nhiều mũi tên cuối (Failed, Cancelled, Refunded) dồn vào một điểm kết thúc nên chồng lên nhau. Cách xử lý: chỉnh tay, hoặc tạo nhiều điểm kết thúc riêng.
   - Swimlane tự sinh có đường nối đi ngang dài qua các lane và hai nút gộp nhánh (merge) cuối sơ đồ; nên kéo lại vị trí để đường nối ngắn hơn.
5. **Quy trình làm**: viết PlantUML/Mermaid trước (nhanh, dễ review), sinh `.excalidraw`, render PNG xem lại, rồi chỉnh tay phần bố cục.


## F. 10 sơ đồ mẫu bổ sung (cơ bản → phức tạp)

Cùng quy trình như phần E: viết PlantUML → sinh `.excalidraw` bằng excaliplant → render PNG → xem lại và sửa. Tất cả file nằm trong `excalidraw-samples/`.

| # | Mức | Loại | Nội dung | Điểm học về cách vẽ |
|---|---|---|---|---|
| 04-login-sequence | Cơ bản | Sequence | Đăng nhập: User → Web → Auth API → DB, khung `alt` đúng/sai mật khẩu. | Sơ đồ sequence tối thiểu: 4 lifeline, 1 khung alt, return message nét đứt. |
| 05-password-reset-activity | Cơ bản | Activity | Quên mật khẩu: token 15 phút, không lộ email có tồn tại hay không, thu hồi mọi session. | Decision (vàng) và merge node; nhãn bước chứa quy tắc nghiệp vụ thật. |
| 06-pull-request-state | Cơ bản | State | Vòng đời Pull Request: Draft → Open → ChangesRequested ⇄ Open → Approved → Merged/Closed. | State có vòng lặp quay lại (push_fix) và hai trạng thái kết thúc. |
| 07-cache-aside-sequence | Trung bình | Sequence | Cache-aside với Redis + PostgreSQL: luồng đọc (hit/miss) và luồng ghi (invalidate). | Dùng divider `== Read ==` / `== Write ==` để tách 2 kịch bản; note giải thích vì sao DEL thay vì SET. |
| 08-ecommerce-er | Trung bình | ER (IE / crow's foot) | Customer, Address, Order, OrderItem (khoá kép), Product, Payment. | Ký hiệu crow's foot (1-n, 1-1..n), PK/FK/UNIQUE ghi trong thuộc tính. |
| 09-leave-approval-swimlane | Trung bình | Activity + swimlane | Duyệt nghỉ phép: Employee, Manager, HR, System; nghỉ trên 5 ngày cần HR duyệt. | Khai báo thứ tự lane trước; gom quyết định về một bước 'Save decision' để tránh lặp bước và đường nối chéo. |
| 10-oauth2-pkce-sequence | Nâng cao | Sequence | OAuth 2.0 Authorization Code + PKCE: code_verifier/challenge, kiểm tra state, đổi code lấy token, gọi API, refresh token rotation. | `autonumber` đánh số bước, self-message cho xử lý nội bộ, delay `...` cho mốc thời gian. |
| 11-microservices-deployment | Nâng cao | Deployment | User → CDN → LB → API Gateway trong Kubernetes; mỗi service một DB; Kafka cho sự kiện; Redis cho session. | Container lồng nhau (AWS VPC ⊃ Kubernetes cluster), màu tách compute (xanh lá) và data/queue (cam). |
| 12-saga-orchestration-sequence | Phức tạp | Sequence | Saga điều phối: ReserveStock → ChargePayment → CreateShipment, bù trừ theo thứ tự ngược khi lỗi. | `alt` lồng `alt`, khung `group` cho bước compensation, note nêu yêu cầu idempotency và retry. |
| 13-payment-composite-state | Phức tạp | State (composite) | Vòng đời thanh toán: Authorizing (có 3DS) → Authorized → Captured (Settled/PartiallyRefunded/FullyRefunded) → Disputed; Declined/Expired/Voided/Lost. | State lồng nhau (composite) có điểm bắt đầu/kết thúc riêng bên trong. |

### Lỗi gặp khi vẽ và cách đã sửa (bổ sung vào bài học ở phần E)
1. **Swimlane lặp bước, đường nối cắt ngang nút** (bản đầu của 09): các nhánh if lồng nhau đều kết thúc bằng "Deduct balance / Notify rejection" nên công cụ vẽ lặp bước ở nhiều chỗ, đường đi xuyên qua nút. Cách sửa: khai báo thứ tự lane ngay đầu (`|Employee|`, `|Manager|`, `|HR|`, `|System|`), gộp điều kiện ("Approve and more than 5 days?") và đưa mọi nhánh về một bước chung ("Save decision") rồi mới rẽ nhánh tiếp.
2. **Khối `cloud` làm hình méo và đẩy node ra ngoài** (bản đầu của 11): Redis bị đặt ngoài vùng AWS. Cách sửa: dùng `rectangle "AWS (VPC)"` làm vùng bao.
3. **`loop` chỉ chứa note là vô nghĩa** (bản đầu của 12): khung loop phải bao quanh message thật. Quy tắc chung như retry hay idempotency nên ghi bằng note ở đầu sơ đồ.
4. **Self-transition làm nhãn đè lên tên state** (bản đầu của 13): bỏ self-loop `PartiallyRefunded → PartiallyRefunded`, hoặc chỉnh tay vị trí nhãn sau khi sinh.
5. **Nhãn trong ngoặc vuông lồng nhau** như `Compensation [reverse order]` hiển thị thành `[Compensation [reverse order]]`. Nên dùng ngoặc tròn trong tiêu đề group.
6. **Còn tồn tại**: state diagram (03, 13) vẫn dồn nhiều mũi tên vào một điểm kết thúc. Nên chỉnh tay trong Excalidraw hoặc vẽ một điểm kết thúc cho mỗi trạng thái cuối.

### Lộ trình luyện vẽ gợi ý theo bộ mẫu
- **Bước 1 (cơ bản)**: 04 → 05 → 06. Học ký hiệu chuẩn của từng loại sơ đồ.
- **Bước 2 (trung bình)**: 07 → 08 → 09. Học cách chia kịch bản, quan hệ dữ liệu, phân vai bằng swimlane.
- **Bước 3 (nâng cao/phức tạp)**: 10 → 11 → 12 → 13. Học điều kiện lồng nhau, container lồng nhau, state lồng nhau, và cách ghi quy tắc phi chức năng (idempotency, retry, timeout) lên sơ đồ.


## G. 6 sơ đồ hệ thống tự vẽ (system design + data flow)

File trong `excalidraw-samples/` (14 → 19), cùng quy trình PlantUML → excaliplant → PNG → kiểm tra.

| # | Mức | Loại | Nội dung | Điểm học về cách vẽ |
|---|---|---|---|---|
| 14-url-shortener-system | Cơ bản | System design | Ghi: LB → Shorten API → ID generator (base62) → DB. Đọc: Redirect API → Redis → DB khi miss → 301/302. | Đánh số 2 luồng riêng (1-4 ghi, A-E đọc); nhãn DB ghi cả schema rút gọn. |
| 15-notification-system | Trung bình | System design | Producers → Notification API (validate, rate limit, dedupe) → hàng đợi theo kênh → workers → APNs/FCM, Twilio, SES; retry/DLQ, log trạng thái. | Fan-out theo kênh; cloud = bên thứ ba; queue và DB cùng màu cam để tách khỏi compute. |
| 16-news-feed-system | Trung bình | System design | Fan-out on write qua Kafka vào feed cache Redis; tác giả > 1M follower thì pull lúc đọc (hybrid). | Gom thành 2 vùng 'Write path' / 'Read path' để người xem thấy ngay 2 luồng. |
| 17-chat-system | Nâng cao | System design | WebSocket qua L4 LB, Message Service gán seq id, Cassandra, Kafka, delivery workers tra session registry; online thì route, offline thì push. | Nhánh 7a/7b cho hai tình huống; nhãn DB ghi khoá phân vùng (PK/CK). |
| 18-cqrs-event-sourcing | Nâng cao | Data flow | Command → Aggregate → Event store (optimistic lock) → outbox/CDC → Kafka → projectors → Postgres view, Elasticsearch, ClickHouse → Query API. | Tách vùng Write side / Read side; ghi rõ 'eventually consistent' trên mũi tên đọc. |
| 19-analytics-pipeline | Phức tạp | Data flow | Clickstream, business events, CDC → Kafka; speed layer (Flink → ClickHouse, alert) và batch layer (S3 Parquet → Spark/dbt → warehouse) → BI. | Ba vùng (Sources, Speed, Batch), đánh số a/b cho hai nhánh song song; DLQ và schema registry làm rõ chất lượng dữ liệu. |

Lỗi gặp và cách sửa:
- Sơ đồ 16 bản đầu bị công cụ nhận nhầm thành sequence diagram (vì dòng đầu là `actor` và `database`), các `node` bị bỏ qua. Cách sửa: mở đầu file bằng khối `rectangle { node ... }` để công cụ nhận đúng là deployment diagram.
- Khi một actor vừa gửi vừa nhận nhiều luồng (14), mũi tên trả về sẽ đi vòng quanh sơ đồ. Có thể chấp nhận, hoặc chỉnh tay cho gọn.

Quy ước dùng chung cho cả 6 sơ đồ (nên đưa vào skill):
- Compute (service, worker): hộp node màu xanh lá. Data (DB, cache): trụ màu cam. Queue/stream: ống ngang màu cam. Bên thứ ba: hình đám mây.
- Đánh số bước trên mũi tên; luồng thứ hai dùng chữ cái (A, B, C) hoặc hậu tố a/b cho các nhánh song song.
- Nhãn thành phần ghi vai trò kèm quyết định thiết kế quan trọng, ví dụ "(sticky WebSocket)", "PK=conversation, CK=seq", "(optimistic lock on version)".
- Gom thành phần theo vùng có ý nghĩa: Write/Read path, Speed/Batch layer, cluster, VPC.


## H. Sơ đồ thật tải từ mạng (176 file, thư mục `excalidraw-downloaded/`)

Mỗi repo nằm trong một thư mục riêng, kèm `SOURCE.md` (URL, commit, giấy phép) và file LICENSE nếu có. File được chép nguyên trạng. Đã bỏ các file rỗng hoặc không có phần tử nào.

**Giấy phép:** chỉ Prakash-sa (CC BY 4.0), Dinesh-Sunny và aretecode (MIT) cho phép tái sử dụng và chỉnh sửa khi ghi nguồn. karanpratapsingh là CC BY-NC-ND 4.0: được dùng phi thương mại và phải ghi nguồn, nhưng không được phân phối bản đã sửa. Các repo không có LICENSE thì mặc định tác giả giữ bản quyền, nên chỉ dùng để học cá nhân, không đưa nguyên file vào sản phẩm hay chia sẻ lại.

### karanpratapsingh/system-design (44 file)
- Nguồn: https://github.com/karanpratapsingh/system-design (commit 6dcea40)
- Giấy phép: CC BY-NC-ND 4.0 (ghi nguồn, phi thương mại, không phân phối bản đã sửa)
- File: diagrams/api-gateway; diagrams/caching; diagrams/cap; diagrams/cdn; diagrams/circuit-breaker; diagrams/clustering; diagrams/consistent-hashing; diagrams/cqrs; diagrams/database-replication; diagrams/db-dbms; diagrams/disaster-recovery; diagrams/distributed-transactions; diagrams/domain-name-system; diagrams/enterprise-service-bus; diagrams/event-driven-architecture; diagrams/event-sourcing; diagrams/federated-database; diagrams/geohashing-quadtrees; diagrams/indexes; diagrams/library (library); diagrams/load-balancing; diagrams/lp-ws-sse; diagrams/message-brokers; diagrams/message-queues; diagrams/monoliths-microservices; diagrams/n-tier-architecture; diagrams/netflix; diagrams/oauth-openid-connect; diagrams/osi; diagrams/pacelc; diagrams/proxy; diagrams/pubsub; diagrams/rate-limiting; diagrams/scaling; diagrams/service-discovery; diagrams/sharding; diagrams/sso; diagrams/tcp-udp; diagrams/transactions; diagrams/twitter; diagrams/uber; diagrams/url-shortener; diagrams/virtualization-containerization; diagrams/whatsapp

### Everoot/System-Design (29 file)
- Nguồn: https://github.com/Everoot/System-Design (commit c26f03e)
- Giấy phép: Không có file LICENSE (mặc định giữ bản quyền) – chỉ dùng để học cá nhân
- File: Core Concepts/API Design; Core Concepts/CAP Theorem; Core Concepts/Caching; Core Concepts/Consistent Hashing; Core Concepts/Data Modeling; Core Concepts/Database Indexing; Core Concepts/Delpoyment Strategies; Core Concepts/Message Queue; Core Concepts/Security; Core Concepts/Sharding; Design A Distributed Cache System; Design A News Feed System (Twitter or Facebook); Design A Rate Limiter; Design A URL Shortener; Design Chat System (WhatsApp or Messenger); Design Dropdox A File Storage Service; Design Payment System (Stripe); Design Ride Sharing System (Uber or Lyft); Design Search Autocomplete (Google Suggest); Design Ticketmaster; Design Video Streaming Platform (YouTube or Netflix); Key Technologies/API Gateway; Key Technologies/AWS; Key Technologies/DynamoDB; Key Technologies/Flink; Key Technologies/Kafka; Key Technologies/Kubernetes; Key Technologies/ZooKeeper; Patterns/Realtime Updates

### swaymun/system-design-excalidraws (15 file)
- Nguồn: https://github.com/swaymun/system-design-excalidraws (commit 6c16b8d)
- Giấy phép: Không có file LICENSE – chỉ dùng để học cá nhân
- File: Donation Drive - S.G; File Storage - JHNL; Google Maps - SDI V2; Mock - Google Photos; Nearby Friends - SDI V2; Netflix - JHNL; Newsfeed - JHNL; Price Tracker - SDFC; Proximity Service - SDI V2; Ticketmaster - HI; Ticketmaster - SDFC; TinyURL -JHNL; Tweet Search - HI; WhatsApp - JHNL; newsfeed

### Prakash-sa/system-design-ultimatum (69 file)
- Nguồn: https://github.com/Prakash-sa/system-design-ultimatum (commit 859c8de)
- Giấy phép: Code MIT, nội dung CC BY 4.0 (ghi nguồn)
- Bỏ qua 14 file rỗng
- File: Libraries/architecture-diagram-components (library); Libraries/data-viz (library); Libraries/drwnio (library); Libraries/software-architecture (library); system_design_all; ☁️ 11. Deployment Strategies/ab_testing_deployment; ☁️ 11. Deployment Strategies/blue_green_deployment; ☁️ 11. Deployment Strategies/canary_deployment; ☁️ 11. Deployment Strategies/feature_flag_deployment; ☁️ 11. Deployment Strategies/rolling_deployment; ☁️ 5. Storage, Data, and Compute Infrastructure/Amazon; ☁️ 5. Storage, Data, and Compute Infrastructure/File Storage (Dropbox, Google Drive); 🌐 2. Content Delivery & Media Systems/Facebook Live Comments; 🌐 2. Content Delivery & Media Systems/Google Photos; 🌐 2. Content Delivery & Media Systems/Netflix; 🌐 2. Content Delivery & Media Systems/YouTube (Video Hosting & Streaming); 💬 3. Social & Communication Systems/Chat System(Messaging); 💬 3. Social & Communication Systems/Donation Drive; 💬 3. Social & Communication Systems/Facebook NewsFeed; 💬 3. Social & Communication Systems/Global Notification Service; 💬 3. Social & Communication Systems/NewsFeed; 💬 3. Social & Communication Systems/NewsFeedV1; 💬 3. Social & Communication Systems/Ticket Booking System; 💬 3. Social & Communication Systems/Ticketmaster; 💬 3. Social & Communication Systems/Tinder; 💬 3. Social & Communication Systems/Twitter (Tweets, Timelines); 💬 3. Social & Communication Systems/WhatsApp; 🔒 8. Security, Identity, and Access Systems/Auth System; 🔒 8. Security, Identity, and Access Systems/Payment Gateway; 🔒 8. Security, Identity, and Access Systems/Stock Broker Trading (Upstox); 🕸️ 4. Search, Discovery & Recommendation/Facebook Post Search; 🕸️ 4. Search, Discovery & Recommendation/Google Maps; 🕸️ 4. Search, Discovery & Recommendation/Hotel Booking (Airbnb); 🕸️ 4. Search, Discovery & Recommendation/Local Delivery Service; 🕸️ 4. Search, Discovery & Recommendation/Nearby Friends; 🕸️ 4. Search, Discovery & Recommendation/Proximity Service; 🕸️ 4. Search, Discovery & Recommendation/Search Auto-Complete; 🕸️ 4. Search, Discovery & Recommendation/Tweet Search (Real Time Indexing); 🕸️ 4. Search, Discovery & Recommendation/Uber; 🖥️ 13. High Performance Computing/GPU; 🖥️ 13. High Performance Computing/Quantum; 🤖 12. AI Design Patterns/Introduction; 🤖 12. AI Design Patterns/Multi Agent Conversational Recommender System (MACRS); 🧠 7. Analytics, Streaming, and Data Pipelines/Ad Click Aggregator; 🧠 7. Analytics, Streaming, and Data Pipelines/Batch Inference System; 🧠 7. Analytics, Streaming, and Data Pipelines/Distributed Logging & Monitoring; 🧠 7. Analytics, Streaming, and Data Pipelines/Leetcode (Online Coding Competition); 🧠 7. Analytics, Streaming, and Data Pipelines/Log Ingestion Service; 🧠 7. Analytics, Streaming, and Data Pipelines/Top K Leaderboard; 🧠 7. Analytics, Streaming, and Data Pipelines/Top K Youtube Videos; 🧩 1. Foundational(Introductory) Design/Communication Patterns; 🧩 1. Foundational(Introductory) Design/DNS; 🧩 1. Foundational(Introductory) Design/Data Structure; 🧩 1. Foundational(Introductory) Design/Database Strategies; 🧩 1. Foundational(Introductory) Design/Distributed Transactions; 🧩 1. Foundational(Introductory) Design/Kafka; 🧩 1. Foundational(Introductory) Design/Load Balancer; 🧩 1. Foundational(Introductory) Design/Price Checking System; 🧩 1. Foundational(Introductory) Design/Price Tracker; 🧩 1. Foundational(Introductory) Design/Proximity Search; 🧩 1. Foundational(Introductory) Design/Rate Limiter; 🧩 1. Foundational(Introductory) Design/Redis; 🧩 1. Foundational(Introductory) Design/SSO; 🧩 1. Foundational(Introductory) Design/Tiny URL; 🧩 1. Foundational(Introductory) Design/URL Shortener; 🧩 1. Foundational(Introductory) Design/Web Crawler; 🧮 10. Hybrid or AI-Augmented Systems/ChatGPT; 🧮 10. Hybrid or AI-Augmented Systems/RAG Chatbot; 🧰 9. DevOps-Cloud-SaaS Infrastructure/Distributed Job Scheduler (Airflow, Temporal, Celery)

### kranthiraju/system-design-docs (10 file)
- Nguồn: https://github.com/kranthiraju/system-design-docs (commit 1b400d6)
- Giấy phép: Không có file LICENSE – chỉ dùng để học cá nhân
- File: LLD/Docs/LLD_docs; LLD/Examples/Communication & Messaging/Notification Service/notification_service; LLD/Examples/Communication & Messaging/Pub-Sub Service/pub_sub; LLD/Examples/Data Structures/LRU Cache/lru_cache; LLD/Examples/Developer Tools/Logging Framework/logging_framework; LLD/Examples/Financial & Payment System/Splitwise/splitwise; LLD/Examples/Management Systems/ParkingLot/parking_lot; LLD/Examples/Managing States/Vending Machine/vending_machine; RAG/RAG; URL Shortener/design_url_shortener

### sanket7474/system-design-lab (6 file)
- Nguồn: https://github.com/sanket7474/system-design-lab (commit ce3a0f4)
- Giấy phép: Không có file LICENSE – chỉ dùng để học cá nhân
- File: Distributed Locking System/diagrams/design; Distributed Logging/diagrams/design; Distributed Tracing System/diagrams/design; MyGate Delivery Preapproval/diagrams/design; Nearby Friends/diagrams/design; Proximity Service/diagrams/design

### DeKinci/sysdeslib (1 file)
- Nguồn: https://github.com/DeKinci/sysdeslib (commit 94640ab)
- Giấy phép: Không có file LICENSE – chỉ dùng để học cá nhân
- File: nick-s-system-design (library)

### Dinesh-Sunny/excalidraw-system-design-kit (1 file)
- Nguồn: https://github.com/Dinesh-Sunny/excalidraw-system-design-kit (commit cc077fe)
- Giấy phép: MIT
- File: library/system-design-ai-kit (library)

### aretecode/system-design-templates-excalidraw (1 file)
- Nguồn: https://github.com/aretecode/system-design-templates-excalidraw (commit 8dafdf3)
- Giấy phép: MIT
- File: src/system-design-template-emoji (library)

### Gợi ý dùng bộ tải về làm input cho skill
- **Học khái niệm từng thành phần**: karanpratapsingh (`diagrams/`, 44 sơ đồ ngắn như caching, sharding, CQRS, load balancing) và Everoot (`Core Concepts/`, `Key Technologies/` như Kafka, DynamoDB, Flink).
- **Học bài toán hoàn chỉnh**: Everoot (`Design A ...`), swaymun, Prakash-sa (chia theo nhóm hệ thống), sanket7474 (distributed locking, logging, tracing).
- **Học thiết kế chi tiết (LLD) và luồng trạng thái**: kranthiraju (LRU cache, parking lot, vending machine, notification).
- **Bộ icon và shape để vẽ nhanh**: DeKinci, Dinesh-Sunny, aretecode, `Prakash-sa/Libraries` (AWS icons, software architecture).
- **Cách đọc file**: `.excalidraw` là JSON. Có thể cho skill đọc trực tiếp các trường `elements[].type`, `x`, `y`, `strokeColor`, `backgroundColor`, `text`, `startBinding`/`endBinding` để rút quy tắc về bố cục, màu sắc và cách nối mũi tên. Mở bằng excalidraw.com (kéo file vào) để xem trực quan.
