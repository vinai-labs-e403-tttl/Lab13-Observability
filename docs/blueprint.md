# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: E403-team-31
- [REPO_URL]: https://github.com/vinai-labs-e403-tttl/Lab13-Observability
- [MEMBERS]:
  - Member A: Trần Kiên Trường | Role: Logging & PII
  - Member B: Đặng Thanh Tùng | Role: Tracing & Enrichment
  - Member C: [Name] | Role: SLO & Alerts
  - Member D: Trần Tiến Long | Role: Load Test & Dashboard
  - Member E: [Name] | Role: Demo & Report

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: /100
- [TOTAL_TRACES_COUNT]: 
- [PII_LEAKS_FOUND]: 

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: [Path to image]
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: [Path to image]
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: [Path to image]
- [TRACE_WATERFALL_EXPLANATION]: (Briefly explain one interesting span in your trace)

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: [Path to image]
- [SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | |
| Error Rate | < 2% | 28d | |
| Cost Budget | < $2.5/day | 1d | |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: [Path to image]
- [SAMPLE_RUNBOOK_LINK]: [docs/alerts.md#L...]

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: (e.g., rag_slow)
- [SYMPTOMS_OBSERVED]: 
- [ROOT_CAUSE_PROVED_BY]: (List specific Trace ID or Log Line)
- [FIX_ACTION]: 
- [PREVENTIVE_MEASURE]: 

---

## 5. Individual Contributions & Evidence

### Trần Kiên Trường
- [TASKS_COMPLETED]: Implemented PII scrubbing processor in logging_config.py, correlation ID middleware with contextvar binding, request context enrichment in /chat endpoint, and added passport/vietnamese_address PII patterns
- [EVIDENCE_LINK]: [(Link to specific commit or PR)](https://github.com/vinai-labs-e403-tttl/Lab13-Observability/pull/1)

### Đặng Thanh Tùng
- [TASKS_COMPLETED]: Tích hợp Langfuse tracing tương thích v4.3.1: cập nhật `tracing.py` dùng decorator `@observe()` và `get_client()` API mới, tạo wrapper `_LangfuseContext` để ánh xạ `update_current_trace`/`update_current_observation` sang v4 API, sửa fallback dùng `ImportError` thay vì `Exception` rộng, thêm `load_dotenv()` vào `main.py` để tự động nạp credentials từ `.env`, làm giàu trace với `user_id` (đã hash), `session_id`, `tags`, `doc_count`, `query_preview` và `usage_details` cho mỗi request, nâng cấp langfuse từ 3.2.1 lên 4.3.1 và cập nhật `requirements.txt`, sửa schema `ChatRequest` thêm field `model` tùy chọn, xác minh traces hiển thị trên Langfuse cloud dashboard qua load test
- [EVIDENCE_LINK]: https://github.com/vinai-labs-e403-tttl/Lab13-Observability/commit/0458433

### [MEMBER_C_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

### Trần Tiến Long
- [TASKS_COMPLETED]: Built `scripts/build_dashboard.py` (Matplotlib) that renders the 6-panel dashboard from `data/logs.jsonl` per `docs/dashboard-spec.md`, with SLO threshold lines and units labeled on every axis (ms, %, USD, count). Ran `scripts/load_test.py --concurrency 5` together with `scripts/inject_incident.py` across all three scenarios (`rag_slow`, `tool_fail`, `cost_spike`) to produce before/after comparison data. Exported two evidence snapshots: `evidence/dashboard_baseline.png` (10 requests, P50/P95/P99 = 150/151/151ms, 0 errors, quality 0.88) and `evidence/dashboard_incidents.png` (30 requests, P95/P99 rose to 2651ms, error rate 16.7% from RuntimeError under `tool_fail`).
- [EVIDENCE_LINK]: 

### [MEMBER_E_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: (Description + Evidence)
- [BONUS_AUDIT_LOGS]: (Description + Evidence)
- [BONUS_CUSTOM_METRIC]: (Description + Evidence)
