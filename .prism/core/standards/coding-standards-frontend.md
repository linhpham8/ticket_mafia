# Coding Standards — Frontend

> Tiêu chuẩn kỹ thuật cho frontend development (Web và Mobile).
> AI đọc file này khi: thiết kế frontend architecture, chọn framework, gen code frontend.

---

## 1. General Principles

### 1.1 Foundational rules

- **Component-based architecture** — reuse and clear separation of concerns.
- Strict separation of **UI layer**, **state management**, and **business logic** so each layer can be replaced without rewriting the others.
- **State management** is explicit and consistent — never let state scatter across random places.
- Important business logic lives on the backend first; the frontend optimizes the experience.
- Critical business decisions are **never** made entirely on the frontend.

### 1.2 Software design principles (apply across React / Angular / Flutter / native)

These principles are non-negotiable. `validate implementation --mode quality` checks them via rule IDs `CODE-4..CODE-9` in `core/phase-quality-standards.md`.

- **SOLID for component design**
  - **S — Single Responsibility**: a component renders or a hook computes; a component that fetches + transforms + renders + handles forms is doing too much. Extract into a hook + presentational component + form component.
  - **O — Open / Closed**: extend behavior via composition (children, render props, slots), not by editing a shared component to add a new prop branch.
  - **L — Liskov**: replacement component versions must honor the original prop contract; do not silently change required props into optional.
  - **I — Interface Segregation**: keep prop interfaces small. A component that takes 15 props is a sign of two components mashed together.
  - **D — Dependency Inversion**: components depend on hooks / services / providers (abstractions), not directly on `axios` / `fetch` / `localStorage`.
- **Loose coupling**: feature folders communicate via their public `index.ts` only (see §2.1 folder structure rule). Reaching into another feature's internals is a `CODE-5` blocker.
- **DRY**: shared UI primitives live in `shared/components`; cross-feature hooks live in `shared/hooks`. Copy-pasted JSX with one-line variation is a `CODE-9` fail — extract a primitive or use composition.
- **KISS & YAGNI**: ship the state shape and abstraction the screen needs today; do not pre-build "flexible" components for screens that do not exist.
- **Container / Presentational separation**
  - **Container** owns data fetching + state + side effects (hooks, store wiring).
  - **Presentational** renders props; pure, testable, story-friendly.
  - A leaf component reaching into a global store directly is a `CODE-4` smell.
- **Design pattern guidance**
  - Custom hook for reusable stateful logic (data fetching, debounced inputs, feature flag access).
  - Render prop / children-as-function or compound components for flexible composition.
  - Provider / Context for cross-tree dependencies (theme, i18n, auth) — not for high-frequency state.
  - Adapter pattern for wrapping a third-party UI library to the project's design system.
  - Anti-patterns: prop drilling beyond 3 levels (use context or composition), `useEffect` for derived state (compute during render), god `App` component, business logic inside JSX.
- **Pure rendering**: components are pure functions of props + state. Side effects belong inside `useEffect` / lifecycle / equivalent — never in the render body.
- **Error boundaries**: every top-level route is wrapped in an error boundary; user-visible error states come from Design, not from raw exception messages.

### 1.3 Testability rules

- Every presentational component is unit-testable without mounting a router, store, or query client. Heavy collaborators are injected via props or context.
- Custom hooks are unit-testable in isolation (e.g. `@testing-library/react-hooks` or framework equivalent).
- Avoid `setTimeout` / `Date.now()` directly in business logic; depend on a timer / clock abstraction so tests can fake time.
- Generated unit / integration tests follow `unit-test-standards.md`: technique discipline, deterministic tests, 90% branch coverage on new code; mutation optional/suggested (`CODE-3a..3d`). Pure-presentational UI is in the exclusion list.

---

## 2. Conventions (apply to all frameworks)

### 2.1 Folder Structure

Organize by **feature** (not by type). Each feature owns its components, hooks, services, and tests:

```
src/
  features/
    auth/
      components/      # UI components owned by this feature
      hooks/           # React hooks / composables specific to this feature
      services/        # API calls for this feature
      store/           # Local state (slice / provider / store)
      types.ts         # Types/interfaces specific to this feature
      index.ts         # Public API — only export what other features need
    orders/
      ...
  shared/
    components/        # Reusable UI primitives (Button, Modal, Input)
    hooks/             # Generic hooks (useDebounce, useLocalStorage)
    utils/             # Pure utility functions
    types/             # Shared domain types
  core/
    api/               # API client setup (axios instance, interceptors)
    router/            # Route definitions
    store/             # Global state store configuration
    config/            # Environment-specific config
```

**Rules:**
- Features MUST NOT import directly from another feature's internal files — only from the feature's `index.ts`
- `shared/` contains only generic UI; domain knowledge belongs in `features/`
- No circular imports between features

### 2.2 Component Naming

| Element | Convention | Example |
|---------|-----------|---------|
| Component file | `PascalCase.tsx` | `OrderSummaryCard.tsx` |
| Component function | `PascalCase` | `export function OrderSummaryCard()` |
| Hook file | `use` prefix, `camelCase` | `useOrderStatus.ts` |
| Service / API file | `camelCase.service.ts` or `camelCase.api.ts` | `order.api.ts` |
| Store slice | `camelCase.slice.ts` (Redux) or `camelCase.store.ts` (Zustand) | `order.slice.ts` |
| Test file | Same name + `.test.ts` / `.spec.ts` | `OrderSummaryCard.test.tsx` |

### 2.3 State Management Pattern (per framework)

| Framework | Local UI state | Server / Async state | Global shared state | When to use global |
|-----------|---------------|---------------------|---------------------|-------------------|
| **React** | `useState` / `useReducer` | React Query / SWR | Zustand or Redux Toolkit | Only for cross-feature state (auth session, cart, notifications) |
| **Angular** | Component property | RxJS Observable + service | NgRx Store or BehaviorSubject service | Auth, routing-level state |
| **Flutter** | `setState` / local BLoC | Riverpod `FutureProvider` | BLoC or Riverpod global provider | Cross-screen state |

**Rules:**
- Server state (API data) belongs in React Query / SWR / Riverpod — NOT in Redux/Zustand
- Form state belongs in React Hook Form / Angular Reactive Forms — NOT in global store
- `useEffect` for data fetching is an anti-pattern — use React Query instead

### 2.4 API Client Pattern

All API calls MUST go through a typed service layer — never call `axios.get()` / `fetch()` directly inside components or hooks.

```typescript
// core/api/client.ts — single axios instance with interceptors
const apiClient = axios.create({ baseURL: config.API_BASE_URL });
apiClient.interceptors.request.use(addAuthHeader);
apiClient.interceptors.response.use(handleSuccess, handleError);

// features/orders/orders.api.ts — typed service
export const ordersApi = {
  getOrder: (id: string): Promise<Order> =>
    apiClient.get(`/orders/${id}`).then(r => r.data),
  createOrder: (payload: CreateOrderRequest): Promise<Order> =>
    apiClient.post('/orders', payload).then(r => r.data),
};

// features/orders/hooks/useOrder.ts — consuming via React Query
export function useOrder(id: string) {
  return useQuery({ queryKey: ['orders', id], queryFn: () => ordersApi.getOrder(id) });
}
```

**Rules:**
- Error handling in interceptors (401 → redirect to login, 5xx → toast notification)
- Request/response types are explicit — no `any`
- Correlation ID headers forwarded from response: `X-Request-ID` **and** `X-Trace-ID` (per `devsecops-standards.md §2.3`) → included in error reporting

---

## 3. Web Standards

### 3.1 Frameworks được phép sử dụng

| Framework | Khi nào ưu tiên |
|-----------|----------------|
| **React** | Mặc định cho SPA, component ecosystem phong phú |
| **Angular** | Team đã có kinh nghiệm Angular, cần opinionated full-framework |
| **NextJS / Node.js** | Khi cần SEO — xem quy tắc NextJS bên dưới |

**Quy tắc NextJS:**
- Chỉ dùng NextJS khi có **nhu cầu SEO thực sự**
- NextJS server-side (Node.js) **chỉ được dùng** cho SSR/SSG phục vụ mục đích SEO
- Không dùng NextJS server-side để chứa business logic — business logic thuộc về backend service

> AI hỏi user để xác nhận framework nếu chưa được khai báo.
> Việc lựa chọn phải dựa trên: năng lực đội ngũ và khả năng tái sử dụng component.

### 3.2 Security Requirements (Web)

Bắt buộc:
- **CSP** (Content Security Policy) — cấu hình đúng, không dùng `unsafe-inline` / `unsafe-eval` trừ khi ADR
- **XSS protection** — sanitize mọi user input trước khi render
- **CSRF protection** — cho mọi state-changing request
- **Không lưu credentials / secrets** ở client-side (localStorage, sessionStorage cho secrets)
- **Token**: phải có expiry + refresh mechanism; không lưu raw token ở localStorage nếu XSS là risk

---

## 4. Mobile Standards

### 4.1 Chọn Native vs Cross-platform

Quyết định dựa trên:
- Yêu cầu thực tế (performance, native features cần thiết)
- Nguồn lực: thời gian, chi phí, nhân lực

Nguyên tắc:
- **Offline-first** nếu khả dụng và phù hợp
- **Secure storage** bắt buộc cho credentials và thông tin nhạy cảm

### 4.2 Technology Standards

| Nền tảng | Language | Framework / Library | Reactive | Unit Testing | Local Storage | Secure Storage |
|----------|----------|---------------------|----------|--------------|---------------|----------------|
| **iOS** | Swift | UIKit / SwiftUI | Combine | Swift Testing / XCTest | UserDefaults / Core Data | KeyChain |
| **Android** | Kotlin | Jetpack / Jetpack Compose | Coroutines | JUnit / MockK | SharedPreferences / Room | Keystore + Local storage |
| **Hybrid** | Dart | Flutter (flutter_bloc + get_it + dio + go_router) | Dart stream | test / flutter_test | shared_preferences / sqlite / hive / sembast | flutter_secure_storage |

### 4.3 Tooling Standards

| Nền tảng | IDE | Code Gen | Code Quality | CI/CD |
|----------|-----|----------|--------------|-------|
| iOS | XCode | SwiftGen | SwiftLint | xcodebuild |
| Android | Android Studio | Gradle KSP | Ktlint | gradle build |
| Hybrid | VS Code / Android Studio | build_runner | flutter_lints | flutter build |

### 4.4 Mobile Security (xem `security-standards.md` — mục Mobile Application Security)

Các yêu cầu security cho mobile app được định nghĩa đầy đủ trong `security-standards.md`. Tóm tắt nhanh:
- Không hardcode secrets
- Obfuscation khi build production
- Anti-tamper + anti-jailbreak/root detection
- System trusted certificates only
- Secure storage cho keys và credentials

### 4.5 Flutter Platform Scaffold (bắt buộc khi project là Flutter)

Khi project là Flutter, gen code KHÔNG được dừng ở Dart. Bắt buộc scaffold đầy đủ 3 lớp:

| Lớp | Files bắt buộc | Khi nào |
|-----|---------------|---------|
| Dart business | `lib/...` | Mọi task |
| iOS | `ios/Podfile`, `ios/Runner/Info.plist`, `ios/Runner/Runner.entitlements` | Mọi project Flutter |
| Android | `android/app/build.gradle`, `android/app/src/main/AndroidManifest.xml`, `android/app/proguard-rules.pro` | Mọi project Flutter |
| Platform channels | Dart `MethodChannel` + native impl (Swift + Kotlin) | Khi cần native capability (camera, biometric, sensor, deep link, push, file picker, share sheet) |
| Permissions | iOS `Info.plist` usage descriptions (`NSCameraUsageDescription`, ...) ↔ Android `<uses-permission>` | Theo capability sử dụng |
| Build config | iOS signing/provisioning, Android signing config; `versionName` / `versionCode`; app icon; launch screen | Trước khi release |

`start implement` cho Flutter task slice phải verify scaffold tồn tại; nếu thiếu → gen scaffold trước khi gen Dart code.

### 4.6 Native Mobile — Capability Standards

| Capability | iOS | Android | Cross-platform abstraction |
|------------|-----|---------|---------------------------|
| Push notification | APNs + UNNotificationCenter | FCM + NotificationManager | Firebase Messaging |
| Deep link | Universal Links (associated domain) | App Links (Digital Asset Links) | uni_links / branch.io |
| Background task | BGTaskScheduler | WorkManager | — |
| In-app purchase | StoreKit 2 | Google Play Billing | RevenueCat / inhouse |
| Biometric | LocalAuthentication | BiometricPrompt | local_auth / native bridge |
| Camera | AVFoundation | CameraX | image_picker / native bridge |
| Location | CoreLocation | FusedLocationProvider | geolocator / native bridge |

**Store submission:**
- iOS: signing & provisioning profile; App Transport Security; privacy manifest (iOS 17+); App Store Review guideline check.
- Android: signing config; ProGuard / R8 rules; Google Play Data Safety form; target SDK ≥ Play Store requirement của năm hiện tại.
- Versioning: semver `major.minor.patch`; build number tăng monotonic.

**OTA update** (nếu dùng): CodePush / Expo Update / Firebase Remote Config — chỉ cho non-binary content (config, JS bundle), tuân thủ Apple / Google policy.

---

## 5. Frontend Observability (Web / Mobile Web / PWA / Mobile native)

Bắt buộc capture các sự kiện:
- Uncaught error / unhandled promise rejection
- Navigation / route error
- Fetch / XHR failures (status >= 4xx hoặc network error)
- Render error (React / Vue / Angular ErrorBoundary, Flutter `FlutterError.onError`)
- Performance: Core Web Vitals (LCP, INP, CLS) cho web; FPS / dropped frames / startup time cho native

Bắt buộc context per event:
- `app_version`, `build_id`
- `session_id`, `user_id` (nếu logged-in)
- device / OS version / browser version / viewport / network type
- Breadcrumbs: 5–10 actions gần nhất

Tooling: Sentry / Rollbar / Bugsnag (chọn 1 cho project — quyết định ở Architecture). Source maps / dSYM / `mapping.txt` upload BẮT BUỘC cho production build.

Offline (mobile web / PWA / mobile native flaky network): queue error locally (IndexedDB / SharedPreferences / NSUserDefaults), retry on reconnect.

PII redaction: cùng quy tắc backend logging — không log password, token, biometrics, full PII (email / phone full); mask trước khi gửi ra ngoài.

---

## 6. Accessibility (a11y)

WCAG 2.1 Level **AA** mặc định cho production. Level AAA cho gov / health / fin nếu khách yêu cầu.

Bắt buộc:
- **Keyboard navigation:** mọi interactive element reach được bằng Tab; focus indicator nhìn thấy được.
- **ARIA:** icon-only button có `aria-label`; live region cho thông báo dynamic; landmark roles cho navigation.
- **Color contrast:** ≥ 4.5:1 cho text thường, ≥ 3:1 cho large text + UI components.
- **Screen reader:** test trên VoiceOver (iOS / macOS), TalkBack (Android), NVDA (Web). Mọi flow chính phải readable.
- **Form:** label gắn với input; error message gắn với field qua `aria-describedby`.
- **Motion:** respect `prefers-reduced-motion`.
- **Touch target:** ≥ 44×44 pt (iOS) / 48×48 dp (Android).

Tooling: axe-core trong CI; manual screen reader test mỗi release; Lighthouse a11y audit ≥ 90.

---

## 7. Internationalization (i18n) & Localization (l10n)

Bắt buộc:
- **String externalization:** không hardcode UI text; mọi text qua i18n framework (react-i18next / vue-i18n / Angular i18n / Flutter `intl` / SwiftUI `LocalizedStringKey` / Android `strings.xml`).
- **Locale-aware format:** date / time / number / currency dùng API locale (`Intl.DateTimeFormat`, `NumberFormatter`, `NSLocale`).
- **RTL support:** dùng CSS logical properties (`margin-inline-start`), flexbox; test bằng `dir="rtl"` cho web; mobile dùng leading/trailing.
- **Pluralization:** ICU MessageFormat / plurals rules — không tự ghép string.
- **Pseudolocalization:** test trước GA để bắt string-overflow / hard-coded text.

Tool: i18n keys phải có namespace; missing-key reporter trong dev build; translation memory cho team translator.

---

## 8. Performance Budgets

| Platform | Metric | Budget |
|----------|--------|--------|
| Web | JS initial bundle | ≤ 200 KB gzipped |
| Web | CSS initial | ≤ 50 KB gzipped |
| Web | LCP | ≤ 2.5s (P75 mobile 4G) |
| Web | INP | ≤ 200ms |
| Web | CLS | ≤ 0.1 |
| Web | Lighthouse Performance | ≥ 90 |
| Mobile Web / PWA | Time-to-interactive | ≤ 3.5s (mid-tier mobile) |
| iOS native | App size (IPA) | ≤ 150 MB |
| Android native | App size (APK base) | ≤ 50 MB; AAB optimized |
| Mobile native | Cold start | ≤ 2s P75 |
| Mobile native | Frame rate | ≥ 60 FPS, dropped frames < 1% |

CI gate: budget vượt = block merge. Source: Lighthouse CI / size-limit / Bundle Analyzer / Xcode app thinning report.

---

## 9. PWA / Service Worker

Áp dụng khi project là PWA (web có offline / installable):

| Concern | Standard |
|---------|----------|
| Service Worker registration | Lifecycle managed (Workbox recommended) |
| Caching strategy per resource | App shell: cache-first; API GET: stale-while-revalidate; API POST/mutation: network-only + background sync |
| `manifest.json` | name, short_name, start_url, display, theme_color, icons (192 / 512 / maskable) |
| Install prompt | Defer `beforeinstallprompt`; show CTA ở UX phù hợp (không spam) |
| Background sync | Queue offline actions, replay khi online |
| Storage quota | Cache API + IndexedDB; theo dõi `navigator.storage.estimate`; LRU evict |
| Update flow | `skipWaiting` + `clients.claim` hoặc prompt user reload |

Test: Lighthouse PWA score ≥ 90; Chrome DevTools "Offline" mode mọi flow chính phải work.

---

## 10. Code Quality Thresholds & Traceability

These thresholds are enforced by `validate implementation --mode quality` against rules `CODE-4..CODE-9`. They apply to TypeScript / JavaScript / Dart / Swift / Kotlin. Project-specific overrides go in `prism-config.md` under `quality_profile.code_thresholds`.

### 10.1 Size and complexity thresholds

| Metric | Threshold (default) | Rule | Severity | Exception |
|--------|--------------------|----- |----------|-----------|
| Component function length | ≤ 150 lines (JSX-heavy) / ≤ 80 lines (logic-heavy) | `CODE-6` | warn at 150 / 80, blocker at 250 | Generated code |
| Hook / utility function length | ≤ 60 lines | `CODE-6` | warn at 60, blocker at 100 | — |
| File length | ≤ 400 lines | `CODE-6` | warn at 400, blocker at 600 | Generated code (route trees, i18n dictionaries) |
| Component nesting depth (rendered tree depth inside one component) | ≤ 4 | `CODE-6` | warn | — |
| Cyclomatic complexity per function | ≤ 10 | `CODE-7` | warn at 10, blocker at 15 | — |
| Prop count per component | ≤ 7 | `CODE-6` | warn at 7, blocker at 10 | — |
| `useEffect` per component | ≤ 3 | `CODE-4` | warn | A 4th effect is a hint the component holds two responsibilities. |
| Public API surface per feature | Only what `<feature>/index.ts` re-exports | `CODE-5` | blocker | — |

Functions / components that breach `blocker`-level numbers must be split before `approve implement` unless an ADR explicitly accepts the deviation.

### 10.2 Code traceability comment (CODE-1 marker)

Every new or materially changed page, route, business-facing component, hook, store slice, API service, or migration / build-time artifact MUST carry a concise traceability comment.

```tsx
// Sprint: v2 | Feature: FR-018 | US: US-042 | Task Group: 2.1 Retry failed payment
// Design: /docs/design/design-system.md §SCREEN-003 | Contract: /docs/architecture/api-specs.md §API-002 POST /payments/authorize
// Pack: v2.3.8-fix-payment | Ticket: PAY-114
export function PaymentRetryButton({ orderId }: Props) { ... }
```

Rules:
- Omit `Pack:` when the scope is not from a change pack.
- Omit `Ticket:` when no approved ticket / task ID exists. Never invent one.
- Do not spray boilerplate markers across trivial leaf primitives (`Button`, `Icon`).
- For Dart / Flutter widgets, place the marker above the `class` or top-level `Widget build(...)`.
- For Swift / Kotlin, place the marker above the `struct` / `class` / top-level function.
- Inline comments explain *why* (constraint, UX rationale, performance trade-off), not *what*.

### 10.3 Module boundaries

- The feature folder is the unit of ownership (`features/<feature>/`). Cross-feature imports go through `<feature>/index.ts` only — reaching into `<feature>/components/Internal*` from another feature is a `CODE-5` blocker.
- A task group's allowed code zone is declared by Plan as `code_ownership_zones`. Code that strays outside the declared zone without an approved plan change is a `CODE-5` blocker.
- Circular feature dependencies are a `CODE-5` blocker.

### 10.4 Test seams

- Custom hooks that talk to backend go through the typed API client (§2.4). Tests stub the API client, not `fetch` / `axios` global.
- Date / time / random / id generation goes through a small injected module (`useClock()`, `useId()`) — direct `new Date()` inside business logic is a `CODE-8` warn.
- Avoid implicit global state (module-level mutable vars). Use a store or context.

### 10.5 Self-check before claiming implementation done

Before declaring a task group done, the developer / AI MUST mentally walk these questions:

1. Does every new component have a single, named responsibility? (`CODE-4`)
2. Are imports respecting feature boundaries and `code_ownership_zones`? (`CODE-5`)
3. Is every component ≤ size/prop threshold and cyclomatic ≤ 10? Run the configured linter if available. (`CODE-6`, `CODE-7`)
4. Are time / id / network calls injected, not hardcoded? (`CODE-8`)
5. Is there any duplicated JSX or hook logic that should become a shared primitive? (`CODE-9`)
6. Does every business-facing component / hook / service carry the `CODE-1` traceability comment?
7. Has the component been verified against Design states (Empty / Loading / Populated / Error) with a screenshot for each state when applicable?

A "no" on any of the above is a blocker for `approve implement` until resolved.

---

## 11. Framework Idioms — Note

Generated frontend code MUST follow the idiomatic patterns of the chosen framework (React, Angular, Vue, NextJS, Flutter, iOS / SwiftUI, Android / Compose, etc.). PRISM intentionally does NOT enumerate every framework idiom in this file — the catalog would bloat and drift with framework releases.

How the AI applies this:

- At code-gen time, draw from model training knowledge of the chosen framework's well-known conventions (hook rules, change-detection strategy, widget lifecycle, state management, theming, accessibility wiring, etc.).
- When training knowledge is uncertain or the framework has shipped a relevant change since cutoff, consult the official framework documentation. This is a **narrow exception** to `INDEX.md` rule "never load standards from web / training data" — that rule applies to **PROJECT standards** (security, compliance, design tokens, architecture, naming). General **framework idioms** are public ecosystem knowledge, not project standards.
- Do not paste idioms from one ecosystem into another (no React patterns inside Flutter, no Angular template syntax inside SwiftUI, etc.).
- When in genuine doubt, ask the user via `feedback:` rather than guess.

`validate implementation --mode quality` checks idiom adherence against the chosen framework's conventions. Drift surfaces as `warn`; defects from drift (a11y regression, measurable perf hit, memory leak, contract drift) escalate to `blocker`.
