# Hướng dẫn chạy và kiểm tra bài làm

## 1. Tóm tắt yêu cầu và kết quả

Lab yêu cầu agent loop Python tự viết, xử lý lỗi/trace, chạy 22 case trước/sau,
phân tích lỗi và cải tiến bằng evidence. Không dùng framework agent, không sửa dữ liệu
hoặc grading để pass, không bịa eval; học viên phải giải thích được code.
Rubric: loop 30, robustness/trace 15, eval/phân tích 20, cải tiến/trình bày 20;
bonus tối đa 15. Điểm eval không phải điểm lab.

Đã chạy thật ngày 11/11/2026:

| Bộ | Case đã chấm | Điểm eval |
|---|---:|---:|
| Baseline | 22/22 | 95.23/100 |
| Cải tiến | 22/22 | 96.77/100 |
| Bonus | 10/10 | 94.8/100 (tham khảo 14.22/15) |

45/45 tests offline pass. NOTES.md phân tích A1, so sánh token, giới hạn judge và lỗi B10.

## 2. File đã sửa/tạo

- agent.py: loop, lỗi/trace/usage, source gate, prompt cải tiến, bonus/retry.
- eval_before.json, eval_after.json: hai kết quả core nguyên bản, cùng cấu hình.
- eval_bonus.json: kết quả bonus nguyên bản.
- NOTES.md: báo cáo 5 mục, evidence thật, bảng điểm từng case và bonus.
- HUONG_DAN_CHAY.md: hướng dẫn này.
- tests/test_agent_robustness.py: 5 tests bổ sung.
- scripts/with_env.py: đọc .env an toàn, không thực thi nội dung như lệnh shell, không in key.
- scripts/eval_baseline.py: chạy baseline từ artifacts/agent_before.py, tắt source gate.
- artifacts/agent_before.py: lưu phiên bản code trước cải tiến prompt.
- scripts/demo_offline.py và artifacts/offline_validation_demo.json: demo source gate bằng FakeProvider.
- scripts/summarize_evals.py và artifacts/eval_comparison.json: tổng hợp số liệu, không sửa eval.
- artifacts/baseline_e2.json: case thử kết nối, không phải điểm cả bộ.
- artifacts/verification.json: kiểm tra cấu hình, số case, bí mật và hash file.
- .env: cấu hình cá nhân, Git ignore; tuyệt đối không nộp.

## 3. Kiểm tra offline trước

Mở PowerShell tại thư mục dự án, dùng Python >=3.10; không cần cài package:

```powershell
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
python -m unittest discover -s tests -v
python -m unittest discover -s bonus -p 'test_*.py' -v
python scripts/demo_offline.py
```

Mong đợi: 42 tests OK và 3 tests OK. Demo in before completed model_calls=3,
after completed model_calls=4. Mở JSON demo: after có validation_missing_source,
final có URL. Đây là provider giả, không phải LLM thật.

## 4. Chạy agent với API thật

.env đã được cấu hình cục bộ. Nếu chuyển máy, sao chép .env.example thành .env rồi điền
PROVIDER, MODEL và key tương ứng. Chương trình gốc không tự đọc .env, dùng wrapper sau:

```powershell
python scripts/with_env.py run.py 'GitHub Actions có incident nào trong snapshot?'
python scripts/with_env.py run.py --bonus --max-steps 16 'Kiểm tra status GitHub, Vercel và npm.'
```

Kiểm tra completed, tool trace đúng provider, câu trả lời có nguồn và phân biệt snapshot/lịch sử.
Thêm --mode live chỉ khi muốn lấy public status API hiện tại; kết quả sẽ khác snapshot.

## 5. Đọc kết quả đã có trước khi chạy lại

Mở eval_before.json và eval_after.json, kiểm tra summary: total_cases=scored_cases=22,
unscored_cases=0, score_0_100 khác null. config hai file giống nhau:
OpenAI gpt-5.4-mini-2026-03-17 cho agent/judge, max_steps=8, dataset=core.

```powershell
python scripts/summarize_evals.py
```

Script kiểm tra config bằng nhau và tổng hợp token, calls, từng case vào
artifacts/eval_comparison.json. Đọc NOTES.md để hiểu A1 81→100 nhưng vẫn thiếu timestamp cụ thể;
không kết luận hệ thống hoàn hảo từ điểm judge. Bonus đủ 10 case, max_steps=16.

## 6. Tái lập eval nếu cần (phát sinh phí API)

Các file kết quả đã được tạo; không cần chạy lại chỉ để xem điểm. Lệnh dưới dùng tên
mới để giữ bản đã phân tích trong báo cáo. Chỉ chạy một case khi thử cấu hình:

```powershell
python scripts/with_env.py scripts/eval_baseline.py --case E2 --max-steps 8 --output artifacts/recheck_e2.json
python scripts/with_env.py scripts/eval_baseline.py --max-steps 8 --output artifacts/recheck_before.json
# Đọc trace baseline, xác định lỗi trước khi so sánh bản cải tiến.
python scripts/with_env.py evals/run_evals.py --max-steps 8 --output artifacts/recheck_after.json
python scripts/with_env.py evals/run_evals.py --bonus --max-steps 16 --output artifacts/recheck_bonus.json
```

Giữ cùng provider/model/judge/max_steps/dataset để so sánh. LLM ngẫu nhiên nên điểm mới
có thể khác báo cáo. Nếu tổng null, đọc reason và sửa cấu hình/quota/judge rồi chạy lại;
không sửa tay điểm. Không gộp case từ các lần chạy để tạo bộ điểm đẹp hơn.

## 7. Demo và nộp bài

1. Giải thích run_agent: context, assistant message nguyên vẹn, tool_call_id, mọi calls,
   model step budget, finish stop, errors, source gate.
2. Mở H6 trong eval_after.json: status → incident gốc → incident liên quan → final,
   chỉ ra truncated. Mở A1 trước/sau để nói về cải tiến và trade-off token.
3. Mở B2 (pagination), B4 (2 lần execute + 1 lần chặn), B10 (model kể nhầm provider 429).
4. Đọc lại NOTES.md; bạn cần giải thích được toàn bộ code theo RULES.md.
5. Kiểm tra git diff; không commit .env. Fixtures/cases/scenarios/grading không sửa.
6. Repo public đúng mẫu K5-L3B-DAY04-DuongThiHuyen-2A202604077-ReactLoopAgent;
   tên thư mục hiện tại dùng Day04, kiểm tra tên GitHub thành DAY04 đúng mẫu.
7. Push và tự nộp link LMS theo SUBMISSION.md trước hạn. Chưa thực hiện push hoặc nộp LMS.
