# HomeBuddy — Test Report

**Date:** 2026
**Environment:** Django 5.0.14, Python 3.12, SQLite (dev) / MySQL 8.0 (target)
**Status:** All checks below were actually executed and passed.

---

## 1. Static verification

| Command | Result |
|---|---|
| `python manage.py check` | `System check identified no issues (0 silenced).` |
| `python manage.py makemigrations --check --dry-run` | `No changes detected` (all migrations committed) |
| `python manage.py migrate` | All 11 app migrations + Django built-ins applied cleanly |
| `python manage.py seed_homebuddy` | Database seeded with demo data, 4 accounts |
| `python manage.py test` | Full suite passes (see §2) |

## 2. Automated test coverage

Run with `python manage.py test`. Test modules live in `apps/*/tests.py`.

| Area | What is asserted |
|---|---|
| Accounts | Customer + provider registration succeeds; weak/numeric password rejected; duplicate email rejected; invalid 10-digit phone rejected; login works; logout is POST-only; `next=` to an external host is ignored |
| Access control | Guest is redirected from customer/provider/admin portals; customer cannot open the provider portal and vice-versa; admin panel rejects non-staff |
| Services | Catalogue page renders; search filters the queryset; `max_price` filter narrows results; pincode + verified filters apply |
| Bookings | Booking is created with the correct total; past date rejected; date beyond 90 days rejected; emergency surcharge applied only for eligible services; emergency rejected for ineligible service; slot conflict prevents a duplicate booking |
| Booking state machine | Only legal transitions are accepted (`ACCEPTED → EN_ROUTE → ARRIVED → IN_PROGRESS`); an illegal jump is refused; cancellation via GET does not mutate the booking |
| Work proof | Completion is impossible without a work proof; both photos plus notes are mandatory to submit |
| Completion | Sign-off sets `COMPLETED`, creates the earnings ledger with the correct 10% commission, and generates an invoice exactly once |
| Payments | Demo checkout records `is_demo=True`; a callback without explicit demo confirmation does not mark a payment successful; signature verification is refused in demo mode; cash choice keeps the payment pending |
| Notifications | Booking creation, acceptance, work proof and completion each create a notification for the right user |
| API | `/api/v1/payments/my/` and `/api/v1/bookings/my/` return only the caller's records; anonymous access is rejected |

## 3. Manual smoke test (browser-equivalent HTTP)

Every route below was requested as guest, customer, technician and admin, then also
curl'd against a real `runserver` process.

| Role | Routes exercised | Result |
|---|---|---|
| Guest | `/`, `/services/`, category + service detail, `/about/`, `/faq/`, `/contact/`, `/terms/`, `/privacy/`, login, both registration pages, `/bookings/emergency/`, `/sitemap.xml`, 404 page | 200 (404 page returns 404 as designed) |
| Guest (blocked) | `/customer/dashboard/`, `/provider/dashboard/`, `/admin-panel/`, `/notifications/` | 302 → login |
| Customer | dashboard, profile, addresses, booking history, notifications, complaints, booking detail, checkout | 200 |
| Customer | demo payment callback → invoice → status JSON | Payment `SUCCESS`, `is_demo=True`, invoice created |
| Technician | dashboard, jobs, earnings, profile, KYC page | 200 |
| Admin (custom panel) | index, users, verifications, bookings, payments, payouts, complaints | 200 |
| Admin (Django admin) | index, user, payment, booking, provider profile, service, review changelists | 200 |
| Security | `GET /bookings/<id>/cancel/` | Booking status unchanged (POST-only enforced) |
| Security | `POST /payments/callback/999999/` | 404, no state written |
| Security | `POST /payments/order/1/` unauthenticated | Redirected to login (not executed) |

## 4. Template compilation

All 57 templates were compiled through Django's template loader:
`templates OK=57 BAD=0`.

## 5. Not covered (stated plainly)

* No load, performance or concurrency testing.
* No cross-browser visual regression testing.
* No penetration test — the security table in `README.md` reflects code review plus the
  specific assertions listed above.
* Live Razorpay mode requires real test keys; it was reviewed against the official SDK API
  and exercised by unit-level mocking, not against the live gateway.
