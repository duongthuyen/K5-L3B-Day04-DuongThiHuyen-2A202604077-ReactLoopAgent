# Ghi chú phân tích · Day 04

Họ và tên: Dương Thị Huyền
MSSV: 2A202604077
Ngày thực hiện: 11/11/2026

Đã chạy LLM thật: bộ chính 22/22 case trước và sau, bonus 10/10 case.
Agent và judge cùng OpenAI `gpt-5.4-mini-2026-03-17`; core max_steps=8,
bonus max_steps=16. Snapshot/dataset/scenarios/grading giữ nguyên.
Các file eval được runner sinh trực tiếp, không sửa tay điểm hoặc answer.
Có dùng AI hỗ trợ code và báo cáo; học viên cần hiểu toàn bộ code trước demo.

## 1. Case được chọn

**A1**, đối chiếu GitHub Actions với Cloudflare Spectrum về incident, trạng thái,
phạm vi và nguồn, không suy đoán chung nguyên nhân. Baseline đạt **81/100**,
case thấp nhất của lần chạy đầu; bản cải tiến đạt **100/100**.

Trích câu trả lời baseline trong `eval_before.json`, case id=A1:

- `Trạng thái hiện tại của component: operational` (có định dạng Markdown trong bản gốc).
- ID bị chép thành `xr3myzjms51`, trong khi tool trả `xr3myzj7ms51`.
- Liệt kê dài nhiều incident, không nêu captured_at và không nói rõ là snapshot.

Judge chấm factuality=29/40, completeness=20/25, evidence=18/20, boundaries=14/15;
đề xuất bám chính xác từng incident và rút gọn. Tôi đối chiếu lại trace và xác nhận
lỗi ID cùng thiếu giới hạn thời gian, không chỉ dựa vào nhận xét judge.

## 2. Bằng chứng trong trace

Chọn case theo `id`, không dựa vào thứ tự file. Chỉ số trace bên dưới bắt đầu từ 0.

**Baseline A1 — `eval_before.json`:**

- `result.trace[1]`: get_status github/Actions, captured_at=`2026-11-09T03:50:47.065020+00:00`,
  component Actions=operational, danh sách có id=`xr3myzj7ms51`.
- `result.trace[2]`: get_status cloudflare/Spectrum, captured_at=`2026-11-09T03:50:47.638054+00:00`,
  Spectrum=degraded_performance; incident `c60k3g4vsoc1`=monitoring.
- `result.trace[5]`: get_incident_details github, id=`xr3myzj7ms51`,
  components=[Webhooks, Actions, Pages], url=`https://stspg.io/pjgptg3cfc6n`.
- Final có URL nhưng chép sai ID; gọi 7 tools trong 3 model calls.

**Sau cải tiến A1 — `eval_after.json`:**

- `trace[1]` và `trace[2]`: lấy status hai provider.
- `trace[4]`: đọc `t89g2q1800fr`; `trace[6]`: đọc `c60k3g4vsoc1`.
- `trace[8]`: completed tại step 4.
- Final mở đầu `Dưới đây là đối chiếu theo snapshot đã lấy`, tập trung 1 incident mỗi bên,
  dẫn đúng hai URL; không xuất ID sai của baseline.

Nguyên nhân khả dĩ: prompt baseline có nhắc phân biệt snapshot và dẫn nguồn nhưng chưa
hướng dẫn rõ cách trình bày, chép định danh và giảm chi tiết thừa. Không thể chứng minh
quan hệ nhân quả chỉ từ một cặp run vì model/judge có tính ngẫu nhiên.

## 3. Thay đổi đã thực hiện

### Agent loop và xử lý lỗi

`agent.py`: context system/user → provider.complete → append nguyên assistant message
→ parse mọi calls → tools.execute → append role=tool đúng tool_call_id → lặp.
Một step là một lần gọi model, không phải một tool. Trace lưu model/tool/error/completed,
usage giữ từng response. Không yêu cầu hoặc lưu chain-of-thought.

JSON lỗi/non-object trả INVALID_ARGUMENTS; tool lỗi thành observation để model xử lý;
provider lỗi trả error và chỉ ghi loại exception, tránh lộ request/key.
finish bất thường, output bị cắt và final rỗng không completed; hết budget trả max_steps.

### Cải tiến sau phân tích baseline

Thêm vào GUIDANCE: ghi captured_at theo provider, không biến snapshot thành live,
chép chính xác ID/tên/URL, ưu tiên incident liên quan thay vì danh sách dài,
tách components và tác động trong updates, không suy diễn phần nguyên nhân bị cắt.
Không hard-code ID hoặc câu trả lời của case vào agent.

Bật source gate: thu URL từ get_incident_details thành công; nếu final không chứa bất kỳ
URL đã đọc nào, ghi validation_missing_source và yêu cầu sửa trong max_steps.
Gate có từ giai đoạn kiểm thử offline, baseline tắt gate; bản after bật gate cùng prompt mới.
**Cả hai run core không có lỗi thiếu tất cả URL; gate không kích hoạt trong after.**
Vì vậy không kết luận mức tăng điểm là do gate. Đây là hai thay đổi cùng lúc, chưa tách
được tác động riêng bằng ablation.

`artifacts/agent_before.py` là bản code được lưu trước khi sửa prompt;
`scripts/eval_baseline.py` dùng bản này với validate_sources=False để tái lập baseline.
Các tests gốc không sửa. Tests cuối: 42 tests trong tests/ và 3 tests trong bonus/ pass.

File thêm mới (đề không cấm tạo file; mọi file gốc của repo đề giữ nguyên, trừ
agent.py và NOTES.md theo yêu cầu): `tests/test_agent_robustness.py` (5 test biên),
`artifacts/agent_before.py` + `scripts/eval_baseline.py` (tái lập baseline),
`scripts/summarize_evals.py` (tổng hợp token/điểm, kiểm tra config trước/sau giống nhau),
`scripts/with_env.py` (nạp .env, không in key), `scripts/demo_offline.py`, `HUONG_DAN_CHAY.md`.

## 4. So sánh hai lần chạy

| Chỉ số | eval_before.json | eval_after.json |
|---|---:|---:|
| Case được chấm | 22/22 | 22/22 |
| Điểm tổng eval | 95.23 | 96.77 |
| Điểm A1 | 81 | 100 |
| Agent model calls | 57 | 62 |
| Agent input tokens | 57,668 | 70,913 |
| Agent output tokens | 12,869 | 11,228 |
| Agent total tokens | 70,537 | 82,141 |
| Judge input tokens | 46,099 | 43,953 |
| Judge output tokens | 3,140 | 3,077 |
| Judge total tokens | 49,239 | 47,030 |
| Tổng token agent + judge | 119,776 | 129,171 |

Điểm tăng 1.54, nhưng agent tăng 5 calls và tổng token agent+judge tăng 9,395.
Provider không trả số tiền thực thu; không coi bảng token là hóa đơn. Case thử E2 trước
full run (95 điểm) nằm riêng tại artifacts/baseline_e2.json, không cộng vào bảng trên.

Lỗi cải thiện: A1 không lặp ID sai, nêu snapshot và chọn bằng chứng gọn hơn.
Hạn chế còn lại: A1 đạt 100 nhưng **vẫn không in captured_at cụ thể**; prompt chưa được
model tuân thủ hoàn toàn. A6 tăng 89→91 nhưng judge vẫn nhận xét diễn đạt nguyên nhân/scope
hơi rộng. H6 giảm 94→93 dù đã theo liên kết và nói truncated. E5 giảm 100→93, judge chê
cách nói 'gần đây'; nhận xét này có tính chủ quan vì câu hỏi cũng hỏi incident gần đây.
Không chạy lại nhiều lần để chọn điểm đẹp hơn.

### Bonus

Đạt **94.8/100**, quy đổi tham khảo **14.22/15**, đủ 10/10 case.
30 agent calls, 66,335 agent tokens (59,694 input; 6,641 output),
32,422 judge tokens (30,897 input; 1,525 output).

- B2 (98): trace[3], [5], [7] đọc Vercel offsets 0→3→6, cuối next_offset=null.
- B3 (98): trace[2] RATE_LIMITED, trace[4] thành công; không coi 429 là outage.
- B4 (96): trace[3], [6] hai lần RATE_LIMITED; trace[8] RETRY_BUDGET_EXCEEDED.
  Có 3 tool requests trong trace nhưng chỉ **2 lần tools.execute** cho Vercel,
  lần thứ ba bị loop chặn. Judge nói '3 lần' nên cần phân biệt request với thực thi API.
- B5 (94): trace[1] INVALID_ARGUMENTS giả lập dù offset=0/limit=3 hợp lệ;
  model đổi limit=2, đọc offsets 0 rồi 2. Đây không phải bằng chứng JSON đầu vào thật bị sai.
- B6 (95): xử lý dữ liệu nhiễu; B7 (98): không xuất marker injection trong final.
- **B10 (80), lỗi còn lại rõ ràng:** trace[4] get_vercel_status bị 429, trace[8] thành công;
  get_cloudflare_status tại trace[5] không lỗi. Final lại nói Vercel không cần retry và
  Cloudflare bị 429. Loop thực thi đúng nhưng model kể nhầm lịch sử giữa provider.
  Final còn diễn đạt components DigitalOcean rỗng như thuộc tính toàn snapshot,
  trong khi query component='DigitalOcean' có thể không khớp tên component.

Retry: sau 429 chỉ retry ngay nếu delay=0, giới hạn số lần; nếu Retry-After cần chờ
hoặc không xác định thì dừng để báo thiếu dữ liệu. Không retry live liên tục.
Schemas/system_prompt lấy từ tools nếu có; pagination và lọc bằng chứng do model quyết định.

## 5. Giới hạn và cách demo

- Điểm eval khác điểm lab; không thể tự quy đổi 96.77 thành điểm bài chính 85.
- Judge cùng model với agent có thể thiên lệch; một run mỗi phiên bản không chứng minh ổn định.
  A1=100 nhưng thiếu timestamp và B4 mô tả số lần thử chưa phân biệt API là ví dụ cần review.
- Source gate kiểm tra một URL dạng chuỗi, không bảo đảm mọi claim đúng hoặc đủ nguồn từng provider.
  URL đúng vẫn có thể đi kèm ID sai hoặc kể sai retry như các lỗi đã thấy.
- Snapshot chính 09/11/2026, bổ sung bonus 10/11/2026 không đại diện status hiện tại.
  Tìm trong 50 incident/response giới hạn, danh sách ngắn và updates truncated không phải toàn lịch sử.
- Prompt chống injection không bảo đảm miễn nhiễm. Context nhiễu vẫn được đưa vào model;
  chưa có cơ chế lọc tự động hoặc kiểm tra ngữ nghĩa các nhận định cuối.
- Demo offline artifacts/offline_validation_demo.json dùng FakeProvider và snapshot thật,
  chỉ chứng minh gate thiếu nguồn hoạt động (3→4 calls), không phải LLM eval.
- Demo thật: mở H6 trong eval_after.json, theo trace[1] status → trace[3] incident gốc
  → trace[5] incident liên quan → final. Giải thích truncation và giới hạn nguyên nhân.
  Sau đó mở B10 để chỉ ra lỗi còn lại dù status=completed.
- API key chỉ nằm trong .env bị Git ignore; không đưa key vào báo cáo.
- Chưa push GitHub hoặc nộp LMS; học viên tự nộp repo cá nhân đúng tên/hạn.

### Bảng điểm từng case (sinh từ file eval nguyên bản)

| Case | Trước | Sau | Chênh lệch |
|---|---:|---:|---:|
| E1 | 91 | 96 | +5 |
| E2 | 97 | 94 | -3 |
| E3 | 95 | 97 | +2 |
| E4 | 97 | 96 | -1 |
| E5 | 100 | 93 | -7 |
| E6 | 96 | 100 | +4 |
| A1 | 81 | 100 | +19 |
| A2 | 98 | 95 | -3 |
| A3 | 100 | 96 | -4 |
| A4 | 99 | 100 | +1 |
| A5 | 95 | 98 | +3 |
| A6 | 89 | 91 | +2 |
| A7 | 94 | 96 | +2 |
| A8 | 96 | 98 | +2 |
| H1 | 92 | 96 | +4 |
| H2 | 100 | 98 | -2 |
| H3 | 97 | 100 | +3 |
| H4 | 94 | 98 | +4 |
| H5 | 100 | 100 | +0 |
| H6 | 94 | 93 | -1 |
| H7 | 95 | 96 | +1 |
| H8 | 95 | 98 | +3 |

| Bonus | Điểm |
|---|---:|
| B1 | 97 |
| B2 | 98 |
| B3 | 98 |
| B4 | 96 |
| B5 | 94 |
| B6 | 95 |
| B7 | 98 |
| B8 | 95 |
| B9 | 97 |
| B10 | 80 |
