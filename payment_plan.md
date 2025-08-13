### Goal
Implement PayTR iFrame with a clean separation: backend creates sessions and handles notifications; frontend embeds the iFrame and handles UX. No secrets on the client. Orders are persisted and updated idempotently.

### Milestones
- Backend data model and endpoints
- Frontend flows and pages
- Environment, security, and testing

### Backend (Flask) plan
- Secrets and config
  - Add env vars: `PAYTR_MERCHANT_ID`, `PAYTR_MERCHANT_KEY`, `PAYTR_MERCHANT_SALT`, `PAYTR_TEST_MODE`, `PAYTR_CURRENCY`, `PAYTR_OK_URL`, `PAYTR_FAIL_URL`.
  - Never expose these to the frontend.

- Data model (Supabase)
  - Table `orders`:
    - `id` (uuid), `merchant_oid` (text, unique), `user_id` (uuid), `status` (enum: pending|paid|failed), `amount_kurus` (int), `currency` (text), `basket_json` (jsonb), `total_amount_kurus` (int, nullable), `failed_reason_code` (text, nullable), `failed_reason_msg` (text, nullable), `created_at`, `updated_at`.
  - Optional `order_events` for audit.

- IP extraction
  - Utility to get client IP with proxy awareness: `X-Forwarded-For` → remote addr. For local dev, allow override with your public IP if needed.

- New blueprint `src/routes/payments.py`
  - POST `/payments/paytr/session` (Step 1)
    - Auth: protected (use `verify_supabase_token`) if tying orders to logged-in users.
    - Input: Either a plan/product ID (preferred) or a validated cart. Do not trust raw amount from client.
    - Server-side:
      - Generate `merchant_oid` (e.g., `uuid4`).
      - Build `user_basket` as Base64 of JSON matrix `[["Title","18.00",1], ...]`.
      - Compute `payment_amount` in kuruş (e.g., 9.99 TL → 999).
      - Determine `user_ip`.
      - Set `no_installment`, `max_installment`, `timeout_limit`, `currency`, `test_mode`, `merchant_ok_url`, `merchant_fail_url`.
      - Compute `paytr_token` with HMAC-SHA256 over the PayTR-required fields (per your `iframe_ornek.py`).
      - Call `https://www.paytr.com/odeme/api/get-token`.
      - On success:
        - Insert order row with status `pending`.
        - Return `{ token, merchant_oid }`.
      - On error: return a safe error; log the full PayTR response.
  - POST `/payments/paytr/callback` (Step 2 - Bildirim URL)
    - Public, CSRF-exempt. Content-Type: form POST.
    - Read `merchant_oid`, `status`, `hash`, `total_amount`, `failed_reason_code`, `failed_reason_msg`.
    - Recompute HMAC using `merchant_key` and `merchant_salt`; compare with posted `hash`. If mismatch: 400 (and do NOT say OK).
    - Find order by `merchant_oid`. If already finalized, return `OK` (idempotent).
    - If `status == 'success'`: set `paid`, save `total_amount`.
    - Else: set `failed`, save failure fields.
    - Respond plain text `OK`.
  - GET `/payments/paytr/status`
    - Query param: `merchant_oid`.
    - Return `{ status, total_amount_kurus, failed_reason_code, failed_reason_msg }`.
  - Optional:
    - GET `/payments/paytr/ok` and `/payments/paytr/fail` that redirect to frontend pages. Note: do not finalize here.

- Register blueprint
  - Import and `api.register_blueprint(payments_blp)` in `Backend/app.py`.

- Security
  - Validate product/price on the server from your catalog; never accept client-sent amounts for chargeable items.
  - Idempotency: ensure callback can be processed multiple times safely.
  - Logging: log callback payloads and signature results (without leaking secrets).
  - CORS: ensure frontend origin is allowed for the session and status endpoints; callback should not need CORS.

### Frontend (React) plan
- Service functions in `Frontend/src/services/api.js` or a new `paymentsService.js`
  - `createPaytrSession(payload)` → POST to `/payments/paytr/session`.
  - `getOrderStatus(merchant_oid)` → GET `/payments/paytr/status`.

- Pages/components
  - Checkout or Payment page (protected if payment requires login)
    - Calls `createPaytrSession` with minimal input (e.g., planId).
    - Receives `{ token, merchant_oid }`.
    - Store `merchant_oid` (e.g., localStorage) for redirect page to reference.
    - Render iFrame:
      - `<script src="https://www.paytr.com/js/iframeResizer.min.js"></script>`
      - `<iframe src="https://www.paytr.com/odeme/guvenli/{token}" id="paytriframe" ...></iframe>`
      - `iFrameResize({}, '#paytriframe');`
  - Payment result page(s): `/payment/success` and `/payment/fail`
    - Read last `merchant_oid` from storage (or pass it via state if same-session).
    - Poll `/payments/paytr/status?merchant_oid=...` until `paid` or `failed` (or show cached final state immediately).
    - Display outcome and next steps. Clear stored `merchant_oid`.

- UX notes
  - The true source of truth is the server (callback). Always show server-confirmed status.
  - Even on “success” redirect, wait for status `paid`, in case the redirect arrives before the callback.

### Environment and deployment
- Local dev
  - Backend on `http://localhost:5000`.
  - Frontend on `http://localhost:5173`.
  - Use a tunnel (ngrok/cloudflared) to expose `POST /payments/paytr/callback` publicly; configure this URL in PayTR panel.
  - For `user_ip`, use real public IP (PayTR requirement) if running fully local; otherwise ensure proxy forwards client IP.
  - Set `PAYTR_TEST_MODE=1`.
- Production
  - HTTPS domain for callback and ok/fail URLs.
  - Lock CORS to production frontend origin(s).
  - Rotate and protect secrets.

### API contracts (concise)
- POST `Backend:/payments/paytr/session`
  - Body: `{ planId: "pro_monthly" }` (or similar minimal identifier)
  - Response: `{ token: "abc...", merchant_oid: "uuid..." }`
- POST `Backend:/payments/paytr/callback`
  - Form: PayTR fields; returns `OK`
- GET `Backend:/payments/paytr/status?merchant_oid=...`
  - Response: `{ status: "pending|paid|failed", total_amount_kurus?: number, failed_reason_code?: string, failed_reason_msg?: string }`

### Testing checklist
- Happy path: token creation → iFrame loads → callback `success` → order `paid` → status endpoint shows `paid` → frontend success page shows paid.
- Failure path: payment rejected → callback `failed` → order `failed` → status reflects failure → frontend fail page shows reason.
- Idempotency: send the same callback multiple times; state remains stable; always returns `OK`.
- Signature: tamper with `hash` to ensure callback rejects.
- Local IP handling: verify token creation does not fail with invalid IP.
- OK/FAIL redirect: ensure pages do not finalize orders and only read status.

### Open items to confirm
- Which product/plan(s) and pricing source (so backend can derive amount).
- Where to store orders (Supabase schema names and any relations to existing users/products).
- Final public URLs for callback, ok, and fail.

- High-level impact:
  - Backend: new `payments` blueprint, env vars, order persistence, and 3–4 endpoints.
  - Frontend: new payment page with iFrame, success/fail pages, and two service calls.