# HomeBuddy — Smart Home Service Booking Marketplace

**Full-stack on-demand home-services marketplace** · Django 5 + MySQL/SQLite + Bootstrap 5 + React (showcase)
**Owner:** Atul Patel · **Level:** TYBSc Computer Science Mini Project / Capstone
**Reference UI:** `safsafaiwala.com` · **Region:** Pune, Maharashtra

---

## 1. What it does

HomeBuddy manages the complete service transaction, not just a listing:

1. **Discovery** — browse by category, search, filter by pincode / verified-only / max price, paginated.
2. **Booking** — date + time-slot selection, 45-minute Emergency Express Dispatch with surcharge, slot-conflict prevention.
3. **Payments** — Razorpay (online, signature-verified) or Cash on Service, with invoices.
4. **KYC** — technicians upload Aadhaar / PAN / police verification; admins approve before the Verified badge is granted.
5. **Mandatory work proof** — before + after photos and notes; the customer must sign off before completion.
6. **Settlement** — automatic 10% platform commission, technician earnings ledger, payout requests with admin approval.
7. **Disputes** — complaint tickets with evidence, admin resolution, automatic booking-state repair.

---

## 2. Quick start (5 commands)

```bash
# 1. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create your environment file
copy .env.example .env         # Windows
cp .env.example .env           # macOS / Linux

# 4. Build the database and load demo data
python manage.py migrate
python manage.py seed_homebuddy

# 5. Run
python manage.py runserver
```

Open <http://127.0.0.1:8000>

### Demo accounts (created by `seed_homebuddy`)

| Role | Email | Password |
|---|---|---|
| Admin | `admin@homebuddy.local` | `Admin@123` |
| Customer | `rahul.sharma@example.com` | `Customer@123` |
| Customer | `sneha.patil@example.com` | `Customer@123` |
| Technician | `suresh.cleaner@example.com` | `Provider@123` |

> The seed command sets these passwords explicitly. Change them before any real deployment.

### URL map

| Area | URL |
|---|---|
| Public site | `/` |
| Customer portal | `/customer/dashboard/` |
| Technician portal | `/provider/dashboard/` |
| **Operations admin panel** | `/admin-panel/` |
| **Django admin (full CRUD)** | `/django-admin/` |
| REST API | `/api/v1/...` |
| Sitemap | `/sitemap.xml` |

---

## 3. Razorpay setup

The project runs in **two clearly distinct modes**. It never fakes a signature.

### DEMO mode (default — works immediately)

Leave the keys empty in `.env`:

```env
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
RAZORPAY_DEMO_MODE=True
```

The checkout page shows a **"DEMO MODE — no real money will be charged"** banner and a
*Simulate payment* button. The resulting `Payment` row is stored with `is_demo=True`, so
a demo payment can never be mistaken for revenue. Admin refunds are disabled for demo rows.

### LIVE / TEST mode (real gateway)

1. Sign in at <https://dashboard.razorpay.com>.
2. Go to **Account & Settings → API Keys → Generate Key** (test mode toggle ON).
3. Put them in `.env`:

```env
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxx
RAZORPAY_KEY_SECRET=xxxxxxxxxxxxxxxxxxxxxxxx
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret
RAZORPAY_DEMO_MODE=False
```

4. Restart the server. The checkout page now opens real Razorpay Checkout.js.

**How verification works** (`apps/payments/razorpay_service.py`):

* The order is created **server-side** with `client.order.create(...)` — the amount is never trusted from the browser.
* Checkout.js returns `razorpay_order_id`, `razorpay_payment_id`, `razorpay_signature`.
* The callback view calls `client.utility.verify_payment_signature(...)`, which performs the
  HMAC-SHA256 check with your key secret.
* **If verification fails the payment is marked `FAILED` and the booking is not confirmed.**
* A webhook endpoint `/payments/webhook/razorpay/` verifies `X-Razorpay-Signature`
  against `RAZORPAY_WEBHOOK_SECRET` to catch payments where the browser closed early.

**Test cards** (Razorpay test mode): `4111 1111 1111 1111`, any future expiry, CVV `123`,
OTP `1234` when prompted.

### MySQL instead of SQLite

```env
DB_ENGINE=mysql
DB_NAME=homebuddy_db
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_PORT=3306
USE_SQLITE_FALLBACK=False
```

Then: `CREATE DATABASE homebuddy_db CHARACTER SET utf8mb4;` and re-run `migrate`.

---

## 4. Project layout

```
config/                 settings, urls, wsgi/asgi
apps/
  accounts/             custom User (role-based), auth, decorators
  customers/            profiles, addresses, dashboard, history
  professionals/        provider profiles, KYC docs, jobs, earnings
  services/             categories, services, provider pricing, search
  bookings/             booking engine, state machine, work proof
  payments/             Razorpay service layer, payments, invoices, payouts
  reviews/              ratings -> provider average
  complaints/           dispute tickets
  messaging/            per-booking chat
  notifications/        in-app notifications + notify() service
  admin_dashboard/      custom operations panel
  core/                 public pages, error handlers, sitemaps, context processor
templates/              56+ templates (Bootstrap 5.3)
static/css, static/js   design system
frontend/               React + Vite marketing showcase (mock data, standalone)
```

---

## 5. Running the tests

```bash
python manage.py test          # 30+ tests, no external services needed
python manage.py check         # zero issues expected
python manage.py makemigrations --check --dry-run   # no pending model changes
```

Tests cover: authentication and role isolation, password validation, booking creation,
slot-conflict rejection, emergency eligibility, the full booking state machine, work-proof
enforcement, completion sign-off + ledger maths, payment demo flow, POST-only enforcement
on state-changing URLs, open-redirect protection, and API ownership checks.

---

## 6. Security notes

| Control | Implementation |
|---|---|
| Secrets | `.env` only; `.gitignore` excludes it; `SECRET_KEY` has no production fallback |
| Debug | `DEBUG=False` by default; must be opted in |
| CORS | explicit allow-list, credentials still scoped |
| State changes | `@require_POST` + CSRF on every mutating view (cancel, accept, suspend, refund, mark-read…) |
| Redirects | `url_has_allowed_host_and_scheme` on every `next=` / `link_url` |
| Passwords | `validate_password()` runs all four configured validators |
| Payments | server-side order creation + HMAC signature verification; failure never confirms a booking |
| IDOR | every object lookup is scoped to the requesting user or their role |
| Transactions | multi-table writes wrapped in `transaction.atomic()` |
| Uploads | 5 MB cap, MIME allow-list on KYC and complaint evidence |

Before production: rotate `SECRET_KEY`, set `ALLOWED_HOSTS`, serve static files via
WhiteNoise/Nginx, run `collectstatic`, and put TLS in front (secure cookies + HSTS switch
on automatically when `DEBUG=False`).

---

## 7. Known limitations (honest list)

* React frontend under `frontend/` is a **standalone marketing showcase using mock data** —
  it does not consume the Django API. The Django templates are the working application.
* Chat is request/response (no WebSockets), so messages appear on refresh.
* No live GPS tracking; status is technician-declared (`EN_ROUTE`, `ARRIVED`).
* Invoice PDFs are rendered as printable HTML rather than generated PDFs.
* No email/SMS provider is wired up; notifications are in-app and the console email backend
  prints to the terminal.
* Payout settlement records the transfer but does not call a bank/payout API.

---

**Developed by Atul Patel** — TYBSc Computer Science, 2026.
