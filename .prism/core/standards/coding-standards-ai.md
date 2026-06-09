# Coding Standards — AI / ML / Automation

> Tiêu chuẩn kỹ thuật cho AI/ML services và hệ thống Agentic AI.
> AI đọc file này khi: thiết kế AI/ML component, định nghĩa agent architecture, review kế hoạch deployment AI.

---

## 1. Core Questions (AI phải hỏi user để gen đúng)

Trước khi thiết kế AI/ML component, cần xác nhận:
- Loại AI: LLM-based / ML model thuần / Rule-based automation / Agentic AI?
- `Scope of agency`: No Agency / Prescribed / Supervised / Full? (xem mục 5)
- Có tương tác với `user-facing` input không? (→ cần prompt injection protection)
- Dữ liệu training có chứa PII không?
- Có model artifacts từ bên thứ 3 không? (→ cần binary scan)
- `Human-in-the-loop` requirement là gì?

---

## 1A. Software Design Principles for AI/ML Code

AI / ML code is still code. Inference services, training pipelines, agent orchestration, prompt construction, and evaluation harnesses all live inside the same codebase as the rest of the system and MUST honor the same design discipline. `validate implementation --mode quality` checks rule IDs `CODE-4..CODE-9` from `core/phase-quality-standards.md` against AI code too.

- **SOLID**
  - **S — Single Responsibility**: one module owns prompt rendering, one owns model invocation, one owns post-processing / guardrail enforcement, one owns evaluation. A "do-everything" `run_agent()` is a `CODE-4` fail.
  - **O — Open / Closed**: add a new tool / skill / evaluator by registering it, not by editing a switch inside the orchestrator.
  - **D — Dependency Inversion**: business code depends on `LLMClient`, `EmbeddingClient`, `VectorStore`, `Guardrail` interfaces — not directly on OpenAI / Anthropic / Bedrock SDK classes. This makes swapping providers and unit-testing without API calls possible.
- **Loose coupling between layers**
  - **Domain logic** (decision rules, eligibility, transformations) — pure functions, framework-free.
  - **Prompt / model layer** — owns templates, parsing, retries, schema validation.
  - **Tool / capability layer** — wraps each external action behind a typed interface with guardrails.
  - **Orchestration layer** — composes the above.
- **DRY**: shared prompt scaffolds, structured-output schemas, retry policies, and guardrails belong in one place. Copy-pasted prompts that drift independently is a `CODE-9` blocker.
- **KISS & YAGNI**: do not add a vector store, fine-tune step, or RAG layer that the problem does not need.
- **Determinism seams for testing**
  - Inject the `LLMClient` so unit tests can replay recorded responses.
  - Pin `temperature` for evaluation runs; record `seed` when supported.
  - Time, randomness, IDs, and clock come from injected interfaces — never from `time.time()` / `uuid.uuid4()` directly in business logic.
  - Generated unit / integration tests follow `unit-test-standards.md`: technique discipline, deterministic tests (no live LLM/network call), 90% branch coverage on new code; mutation optional/suggested (`CODE-3a..3d`).
- **Pattern guidance**
  - Strategy: swap between provider / model variants.
  - Adapter: wrap a provider SDK to the project's `LLMClient` interface.
  - Decorator / middleware: layer guardrails, logging, cost metering, prompt-injection scanning around the base client.
  - Repository: persist conversations, evals, prompt traces.
  - Command / Tool registry: register agent tools by name + schema, dispatch through the registry.
- **Anti-patterns to avoid**
  - Inline prompt string literals scattered across files (centralize them; version them).
  - Parsing model output by regex when the model supports JSON / structured output — request structured output instead.
  - Calling the model from inside a request handler without retry, timeout, or guardrail.
  - Storing API keys in code — secret refs only.

---

## 2. Development Standards

### 2.1 Language & Framework
- Ngôn ngữ: **Python** (ưu tiên cho AI/ML), cũng có thể Java/Kotlin, C/C++ tùy use case
- Serving / API: **FastAPI** cho inference & agent endpoints (khớp `coding-standards-backend.md` §2 + §8)
- LLM / agent code: tổ chức quanh các abstraction `LLMClient` / `EmbeddingClient` / `VectorStore` / `Guardrail` (xem §1) thay vì gọi trực tiếp provider SDK — để swap provider & unit-test không cần API thật
- Model lifecycle / experiment tracking: **MLflow** (registry, versioning, metrics) — xem §2.3 Model Artifact Registry

### 2.2 Model Card — Bắt buộc cho mọi model artifact

Mỗi model được sử dụng trong hệ thống phải có Model Card với:
- **Tên, chức năng, version** (version phải gắn với data version và code version)
- **Download links** (source repository)
- **Type**: LLM, VLM, CatBoost, scikit-learn, custom, v.v.
- **Metrics đã đo lường**: kết quả, dữ liệu đánh giá, cách đánh giá
- **Thông tin training**: dữ liệu training, thời gian, hạ tầng sử dụng
- **Notes quan trọng**: limitations, bias known, known failure modes

### 2.3 Model Artifact Registry

Ngoài code registry trên GitLab, model artifacts và Docker images sau khi build phải được lưu:
- Cloud/on-prem storage phù hợp: GCS / S3, Artifact Registry, GCR / ECR
- Đảm bảo: khả năng sao lưu, rollback, versioning

### 2.4 Human-in-the-Loop

- Thiết kế cho HITL khi `scope of agency` từ Prescribed trở lên
- Phải có cơ chế **user feedback loop** để cải thiện model

---

## 3. Data Governance Requirements

- **PII masked** trong mọi dataset dùng cho training/evaluation
- **Data versioning**: artifacts phải được đánh version, gắn với data version và code version
- **Retention policy**: xác định rõ thời gian giữ dữ liệu customer để xử lý và audit
- **Phân quyền**: ai được access dữ liệu gốc, ai chỉ được access dữ liệu đã masked
- **Data labeling**: dữ liệu phải được đánh dấu rõ: được phép / không được phép dùng để train model

---

## 4. Security Requirements

### 4.1 Software & Model Supply Chain
- **Kiểm tra license** của mọi 3rd-party software và pre-trained model
- **Scan binary artifacts** — model được phân phối dạng binary (pkl, pth, v.v.) ẩn chứa rủi ro bảo mật cao; phải scan trước khi deploy
- **CVE handling**: xử lý High+ trước khi lên prod; có plan cho Medium và thấp hơn

### 4.2 LLM / Conversational AI
- **Bắt buộc test prompt injection** cho mọi hệ thống AI có tương tác với user input
- **Tích hợp Guardrail AI** (Onemount AI Guardrail) — bắt buộc cho mọi GenAI/Agent solution

### 4.3 CI/CD Security
- Scan Docker image for vulnerabilities trước khi deploy to prod (chạy trong CI pipeline)

---

## 5. Agentic AI — Agency Scope Matrix

Xác định `scope of agency` **trước khi thiết kế** để apply đúng security requirements:

| Scope | Mô tả | Trigger | Yêu cầu Security | Risk |
|-------|-------|---------|-----------------|------|
| **Phạm vi 1 — No Agency** | AI chỉ read-only, không thực hiện thay đổi | Người dùng | Read-only permissions; không cấp secret/token; data minimization + PII masking; prompt & output guardrails; log đầy đủ | Thấp |
| **Phạm vi 2 — Prescribed Agency** | AI có thể thực hiện thay đổi nhưng **bắt buộc có người duyệt** (HITL) | Người dùng | HITL bắt buộc; action gắn với identity người duyệt; RBAC + least privilege; audit trail đầy đủ (AI đề xuất → người duyệt → action); kill switch | Trung bình |
| **Phạm vi 3 — Supervised Agency** | Người kích hoạt, AI tự động thực hiện — có giám sát | Người dùng | Pre-authorization per action type; boundary rõ ràng (AI được/không được làm gì); runtime monitoring & alert; rollback/recovery bắt buộc cho mọi action; checkpoint; review định kỳ scope & log | Cao |
| **Phạm vi 4 — Full Agency** | AI hoàn toàn tự chủ, tự khởi động và tự thực hiện | Hệ thống / Event | Phê duyệt cấp cao (CISO/Board) bằng văn bản; independent guardrails (không override được); isolation environment; continuous monitoring + drift detection; emergency kill switch theo anomaly; IR và legal accountability rõ ràng | Rất cao |

---

## 6. Observability Requirements

AI/ML systems phải có observability riêng ngoài standard app observability:
- **Theo dõi sức khoẻ model** sau deployment: performance metrics, accuracy drift
- **Concept drift monitoring**: phát hiện khi data distribution thay đổi làm model kém chính xác
- **Kiểm soát chi phí**: theo dõi GPU/CPU usage, log storage, pipeline cost (đặc biệt với BigQuery, LLM API calls)
- **Explainability**: không để AI/ML là hộp đen — cung cấp lý do đưa ra quyết định (khi applicable)

---

## 7. Deployment Standards

- **Scan Docker image** for vulnerabilities trước khi deploy
- **Deployment plan** bao gồm: scaling plan, rollout plan, rollback plan
- **Shadow deployment** + A/A test + A/B test plan trước khi full rollout
- **Retrain / Rebuild schedule** phải được định nghĩa
- **Transparency**: dự đoán/quyết định của AI cần có thông tin hỗ trợ giải thích (Explainable AI)

---

## 8. Code Quality Thresholds & Traceability

These thresholds are enforced by `validate implementation --mode quality` against rules `CODE-4..CODE-9`. They apply to Python / Java / Kotlin / Go AI code. Project-specific overrides go in `prism-config.md` under `quality_profile.code_thresholds`.

### 8.1 Size and complexity thresholds

| Metric | Threshold (default) | Rule | Severity | Exception |
|--------|--------------------|----- |----------|-----------|
| Function length | ≤ 80 effective lines | `CODE-6` | warn at 80, blocker at 120 | Generated boilerplate, declarative pipeline DSL |
| File length | ≤ 500 lines | `CODE-6` | warn at 500, blocker at 800 | Model schema, vocabulary, weights |
| Cyclomatic complexity per function | ≤ 10 | `CODE-7` | warn at 10, blocker at 15 | Eval scoring, rule dispatch (with comment) |
| Prompt template length | ≤ 4000 chars per template | `CODE-6` | warn at 4000 | Few-shot heavy templates with explicit rationale |
| Parameter count per function | ≤ 5 | `CODE-6` | warn at 5, blocker at 7 | DTO-style config objects |
| Public API surface per module | Minimal — only what `/docs/architecture/project-reference.md` lists as `public_entrypoints` | `CODE-5` | blocker | — |

### 8.2 Code traceability comment (CODE-1 marker)

Every new or materially changed inference handler, agent capability, training step, evaluator, or guardrail MUST carry a concise traceability comment.

```python
# Sprint: v2 | Feature: FR-018 | US: US-042 | Task Group: 2.1 Smart retry suggestion
# Contract: /docs/architecture/api-specs.md §API-019 POST /agents/retry-suggestion | Project: /docs/architecture/project-reference.md §PR-006
# Model: model-card §RetrySuggest-v1.3 | Pack: v2.3.8-fix-payment | Ticket: PAY-114
def suggest_retry(...):
    ...
```

Rules:
- Omit `Pack:` when the scope is not from a change pack.
- Omit `Ticket:` when no approved ticket / task ID exists.
- Include `Model:` whenever the function depends on a specific model version. Link to the model card.
- Do not spray markers across trivial helpers (`CODE-2`).
- Inline comments explain *why* a prompt design / temperature / retry choice was made, not *what* the code does.

### 8.3 Dependency direction and module boundaries

- The dependency graph (`api / handler → orchestration → domain → adapters (LLM/store/tool)`) MUST be acyclic.
- Domain logic NEVER imports a provider SDK directly. Cycles between orchestration and adapters are a `CODE-5` blocker.
- A task group's allowed code zone is declared by Plan as `code_ownership_zones`. Code that strays is a `CODE-5` blocker.

### 8.4 Test seams

- `LLMClient`, `EmbeddingClient`, `VectorStore`, `Tool`, `Guardrail` are injected. Tests provide replay / fake / stub implementations.
- Recorded golden conversations + eval suites live next to the agent code, not in a separate "QA only" repo.
- Hardcoding a model name string inside business logic is a `CODE-8` warn; centralize model selection through config.

### 8.5 Self-check before claiming implementation done

Before declaring a task group done, the developer / AI MUST mentally walk these questions:

1. Does every new function have a single, named responsibility? (`CODE-4`)
2. Are domain modules free of provider SDK imports? (`CODE-5`)
3. Is every function ≤ size / complexity threshold? (`CODE-6`, `CODE-7`)
4. Are LLM / store / clock / id dependencies injected so tests can run without API calls? (`CODE-8`)
5. Are prompts centralized, versioned, and not duplicated with subtle drift? (`CODE-9`)
6. Does every business-facing function carry the `CODE-1` traceability comment with `Model:` line when applicable?
7. Has the eval / replay suite been run on the new scope and recorded next to the validate report?

A "no" on any of the above is a blocker for `approve implement` until resolved.

---

## 9. Framework Idioms — Note

Generated AI / ML code MUST follow the idiomatic patterns of the chosen SDK and runtime (official Claude / Anthropic SDK, OpenAI SDK, Bedrock, Vertex; LangChain / LangGraph when chosen; pydantic / asyncio for Python; etc.). PRISM intentionally does NOT enumerate every SDK idiom in this file — the catalog would bloat and drift with SDK releases.

How the AI applies this:

- At code-gen time, draw from model training knowledge of the chosen SDK's well-known conventions (streaming, structured output, tool-use schema, prompt caching, retry / timeout, model selection, vendor abstraction, eval harness layout, etc.).
- When training knowledge is uncertain or the SDK has shipped a relevant change since cutoff, consult the official SDK documentation. This is a **narrow exception** to `INDEX.md` rule "never load standards from web / training data" — that rule applies to **PROJECT standards** (security, compliance, model governance, agency scope, data governance). General **SDK / framework idioms** are public ecosystem knowledge, not project standards.
- Do not paste idioms from one SDK into another (no OpenAI-shaped calls inside an Anthropic SDK code path, no LangChain idioms inside raw SDK code, etc.).
- When in genuine doubt, ask the user via `feedback:` rather than guess.

`validate implementation --mode quality` checks idiom adherence against the chosen stack's conventions. Drift surfaces as `warn`; defects from drift (runaway cost, missing structured output where contract requires it, missing prompt caching on stable system prompts, unsafe tool dispatch, etc.) escalate to `blocker`.
