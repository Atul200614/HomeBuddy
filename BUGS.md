# HomeBuddy — Known Issues & Limitations

This file lists what is genuinely still open. Anything that was fixed in the last pass is
recorded in `CHANGELOG.md` instead.

## Fixed (previously blocking)

* `get_object_or_401` typo — replaced with Django's `get_object_or_404` in all 42 call sites.
* Missing `migrations/` packages — created for all 11 apps; `migrate` now builds the schema.
* Fabricated test report — replaced with `TEST_REPORT.md` describing only executed checks,
  plus a real `manage.py test` suite.
* Unverified payment callback — replaced with server-side order creation and HMAC-SHA256
  signature verification; a failed verification marks the payment `FAILED` and never
  confirms a booking.
* `CORS_ALLOW_ALL_ORIGINS=True` with credentials — replaced with an explicit allow-list.
* Committed `SECRET_KEY`, `DEBUG=True`, `ALLOWED_HOSTS='*'` defaults — all default to safe
  values; secrets now live only in `.env`.
* State-changing GET links — every mutating view is `@require_POST` with CSRF and a form.
* Open redirect on login — guarded by `url_has_allowed_host_and_scheme`.
* Password validators never invoked — `validate_password()` now runs on registration.
* IDOR in the payments API — object lookups are scoped to the owner.
* No transactions — multi-table writes are wrapped in `transaction.atomic()`.
* Notifications never created — a `notify()` service is called from every domain event.
* Dead search filters (`pincode`, `verified`, `max_price`) — now applied to the queryset.
* No pagination — added to services, bookings, jobs, users, documents, payments, payouts.

## Open (by design or out of scope)

| # | Item | Impact | Notes |
|---|---|---|---|
| 1 | React frontend uses mock data | Medium | `frontend/` is a marketing showcase; it does not call the Django API. Templates are the working app. |
| 2 | Chat is not realtime | Low | No Django Channels/WebSocket; messages appear after refresh. |
| 3 | No live GPS tracking | Low | Status is technician-declared, not device-tracked. |
| 4 | Invoice is printable HTML, not PDF | Low | `reportlab` is a dependency; PDF generation is a natural next step. |
| 5 | No email/SMS delivery | Low | Console email backend; notifications are in-app. |
| 6 | Payout does not call a bank API | Low | Admin records the transfer and settles the ledger manually. |
| 7 | Provider availability model unused in the UI | Low | `ProviderAvailability` exists but the booking form uses the `is_available_today` flag. |
| 8 | Single currency | Low | Razorpay is configured for INR only. |
| 9 | No rate limiting on login | Medium | Django-level throttling exists for the REST API only; add `django-axes` for production. |
| 10 | No automated cross-browser testing | Low | Responsive layout verified manually with Bootstrap breakpoints. |
