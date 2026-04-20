# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: E403-team-31
- [REPO_URL]: https://github.com/vinai-labs-e403-tttl/Lab13-Observability
- [MEMBERS]:
  - Member A: Trần Kiên Trường | Role: Logging & PII
  - Member B: [Name] | Role: Tracing & Enrichment
  - Member C: Trịnh Ngọc Tú | Role: SLO & Alerts
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
| Latency P95 | < 3000ms | 28d | TBD |
| Error Rate | < 2% | 28d | TBD |
| Cost Budget | < $2.5/day | 1d | TBD |

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

### [MEMBER_B_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

### Trịnh Ngọc Tú
- [TASKS_COMPLETED]: Đã cấu hình và tinh chỉnh các mục tiêu SLOs trong file `config/slo.yaml` (mốc P95 3000ms). Cập nhật ngưỡng thông báo (alert rules) trong `config/alert_rules.yaml` để cảnh báo sớm tình trạng trễ dịch vụ và vượt chi phí.
- [EVIDENCE_LINK]: 

### Trần Tiến Long
- [TASKS_COMPLETED]: Xây script `scripts/build_dashboard.py` (Matplotlib) render 6-panel dashboard từ `data/logs.jsonl` theo đúng `docs/dashboard-spec.md`, có SLO threshold line đỏ và đơn vị rõ ràng trên từng panel (ms, %, USD, count). Chạy `scripts/load_test.py --concurrency 5` cùng `scripts/inject_incident.py` cho cả 3 scenario (`rag_slow`, `tool_fail`, `cost_spike`) để sinh dữ liệu so sánh before/after. Xuất 2 snapshot evidence: `evidence/dashboard_baseline.png` (10 requests, P50/P95/P99 = 150/151/151ms, 0 errors, quality 0.88) và `evidence/dashboard_incidents.png` (30 requests, P95/P99 nhảy lên 2651ms, error rate 16.7% do RuntimeError khi bật `tool_fail`).
- [EVIDENCE_LINK]: 

### [MEMBER_E_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: (Description + Evidence)
- [BONUS_AUDIT_LOGS]: (Description + Evidence)
- [BONUS_CUSTOM_METRIC]: (Description + Evidence)
