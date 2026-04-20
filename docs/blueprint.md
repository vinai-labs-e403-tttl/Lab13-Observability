# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: E403-team-31
- [REPO_URL]: https://github.com/vinai-labs-e403-tttl/Lab13-Observability
- [MEMBERS]:
  - Member A: Trần Kiên Trường | Role: Logging & PII
  - Member B: Đặng Thanh Tùng | Role: Tracing & Enrichment
  - Member C: Trịnh Ngọc Tú | Role: SLO & Alerts
  - Member D: Trần Tiến Long | Role: Load Test & Dashboard
  - Member E: TBD | Role: Demo & Report

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: 100/100
- [TOTAL_TRACES_COUNT]: 42
- [PII_LEAKS_FOUND]: 0

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: evidence/correlation_id_log.png
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: evidence/pii_redaction_log.png
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: evidence/trace_waterfall.png
- [TRACE_WATERFALL_EXPLANATION]: In the `rag_slow` scenario, the retrieval span is the most interesting one because it dominates end-to-end latency while the downstream LLM work remains comparatively stable. This proves the slowdown came from the RAG step rather than response generation.

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: evidence/dashboard.png
- [SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | 150ms |
| Error Rate | < 2% | 28d | 0.0% |
| Cost Budget | < $2.5/day | 1d | $0.0868 |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: evidence/alert_rules.png
- [SAMPLE_RUNBOOK_LINK]: [docs/alerts.md#L3]

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: rag_slow
- [SYMPTOMS_OBSERVED]: Latency increased sharply during the incident window while successful responses still returned. The trace waterfall showed one retrieval-related span taking much longer than the rest of the request path.
- [ROOT_CAUSE_PROVED_BY]: Log line `incident_enabled` at `2026-04-20T10:20:22.614003Z` with payload `{\"name\": \"rag_slow\"}` in `data/logs.jsonl`, together with the slow retrieval span in `evidence/trace_waterfall.png`.
- [FIX_ACTION]: Disabled the `rag_slow` incident toggle and re-ran traffic to confirm latency returned to the normal baseline.
- [PREVENTIVE_MEASURE]: Keep the high-latency alert active, watch trace span breakdowns for retrieval regressions, and add mitigations such as truncating long queries or using a fallback retrieval source.

---

## 5. Individual Contributions & Evidence

### Trần Kiên Trường
- [TASKS_COMPLETED]: Implemented PII scrubbing processor in logging_config.py, correlation ID middleware with contextvar binding, request context enrichment in /chat endpoint, and added passport/vietnamese_address PII patterns
<<<<<<< HEAD
- [EVIDENCE_LINK]: https://github.com/vinai-labs-e403-tttl/Lab13-Observability/commit/2023be8
=======
- [EVIDENCE_LINK]: [(Link to specific commit or PR)](https://github.com/vinai-labs-e403-tttl/Lab13-Observability/pull/1)
>>>>>>> 99a027258d09051232bbea845f6ce092791d8b7b

### Đặng Thanh Tùng
- [TASKS_COMPLETED]: Tích hợp Langfuse tracing tương thích v4.3.1: cập nhật `tracing.py` dùng decorator `@observe()` và `get_client()` API mới, tạo wrapper `_LangfuseContext` để ánh xạ `update_current_trace`/`update_current_observation` sang v4 API, sửa fallback dùng `ImportError` thay vì `Exception` rộng, thêm `load_dotenv()` vào `main.py` để tự động nạp credentials từ `.env`, làm giàu trace với `user_id` (đã hash), `session_id`, `tags`, `doc_count`, `query_preview` và `usage_details` cho mỗi request, nâng cấp langfuse từ 3.2.1 lên 4.3.1 và cập nhật `requirements.txt`, sửa schema `ChatRequest` thêm field `model` tùy chọn, xác minh traces hiển thị trên Langfuse cloud dashboard qua load test
- [EVIDENCE_LINK](https://github.com/vinai-labs-e403-tttl/Lab13-Observability/commit/0458433)

### Trịnh Ngọc Tú
- [TASKS_COMPLETED]: Đã cấu hình và tinh chỉnh các mục tiêu SLOs trong file `config/slo.yaml` (mốc P95 3000ms). Cập nhật ngưỡng thông báo (alert rules) trong `config/alert_rules.yaml` để cảnh báo sớm tình trạng trễ dịch vụ và vượt chi phí.
- [EVIDENCE_LINK]: https://github.com/vinai-labs-e403-tttl/Lab13-Observability/commit/2ac546d

### Trần Tiến Long
- [TASKS_COMPLETED]: Built `scripts/build_dashboard.py` (Matplotlib) that renders the 6-panel dashboard from `data/logs.jsonl` per `docs/dashboard-spec.md`, with SLO threshold lines and units labeled on every axis (ms, %, USD, count). Ran `scripts/load_test.py --concurrency 5` together with `scripts/inject_incident.py` across all three scenarios (`rag_slow`, `tool_fail`, `cost_spike`) to produce before/after comparison data. Exported two evidence snapshots: `evidence/dashboard_baseline.png` (10 requests, P50/P95/P99 = 150/151/151ms, 0 errors, quality 0.88) and `evidence/dashboard_incidents.png` (30 requests, P95/P99 rose to 2651ms, error rate 16.7% from RuntimeError under `tool_fail`).
- [EVIDENCE_LINK]: https://github.com/vinai-labs-e403-tttl/Lab13-Observability/commit/ef7e620

### Member E
- [TASKS_COMPLETED]: Consolidated the final blueprint report, mapped each required screenshot into the submission, summarized the incident-response narrative for `rag_slow`, and prepared the demo flow covering logs, traces, dashboard, and alerts for the live presentation.
- [EVIDENCE_LINK]: https://github.com/vinai-labs-e403-tttl/Lab13-Observability/commit/0ade15e

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: (Description + Evidence)
- [BONUS_AUDIT_LOGS]: (Description + Evidence)
- [BONUS_CUSTOM_METRIC]: (Description + Evidence)
