# HomeBuddy Project ZIP Manifest & Packaging Specification (ZIP_MANIFEST.md)
**Project:** HomeBuddy – Smart Home Service Booking Marketplace  
**Owner:** Atul Patel (TYBSc Computer Science)  
**Package Version:** 2.0.0 (Full Master Delivery)  

---

## 1. Archive Contents
The project package contains:

### Root Documentation & Configuration
- `manage.py` — Django CLI controller
- `requirements.txt` — Python dependencies
- `.env.example` & `.env` — Environment configuration
- `README.md` — Project overview & quickstart
- `INSTALLATION.md` — Complete Windows setup guide
- `PROJECT_MASTER.md` — Master blueprint
- `SRS.md` — Software Requirements Specification & Traceability Matrix
- `DATABASE_DESIGN.md` — ER Diagram & Data dictionary
- `ARCHITECTURE.md` — System architecture & API contracts
- `DECISIONS.md` — Technical decisions log
- `TASKS.md` — 20-session task checklist
- `PROGRESS.md` — Quality Gate and progress tracker
- `TEST_REPORT.md` — Comprehensive test report
- `BUGS.md` — Bug tracker & limitations
- `CHANGELOG.md` — Version history
- `HANDOFF.md` — Session continuation document

### Core Django Project (`config/`)
- `__init__.py` (with PyMySQL hook)
- `settings.py` (multi-mode settings)
- `urls.py` (root URL dispatcher)
- `wsgi.py` & `asgi.py`

### Domain Applications (`apps/`)
- `apps/core/` — Public views, home, about, FAQ, context processors, error handlers, seed command
- `apps/accounts/` — Custom User model, registration, login, RBAC decorators, API views
- `apps/customers/` — CustomerProfile, Address book CRUD, dashboard, booking history
- `apps/professionals/` — ProviderProfile, skills, KYC VerificationDocument, jobs, earnings
- `apps/services/` — Category, Service, ProviderService, catalog filtering, API views
- `apps/bookings/` — Booking engine, state machine, WorkProof before/after photos, tracking
- `apps/payments/` — Payment, Razorpay checkout, Cash on service, EarningsLedger, Invoice
- `apps/reviews/` — Review model, rating calculation, feedback forms
- `apps/complaints/` — Complaint ticket model, dispute investigation, resolution
- `apps/messaging/` — Booking-linked chat threads, messages
- `apps/notifications/` — In-app notification center, read tracking
- `apps/admin_dashboard/` — Aggregated SQL metrics dashboard, user/worker/complaint moderation

### Presentation Templates (`templates/`)
- `base.html` — Master responsive layout with location selector (`Pune`), search bar, alerts, footer
- `public/` — `index.html` (matching `safsafaiwala.com` reference), `about.html`, `faq.html`, `contact.html`, `terms.html`, `privacy.html`
- `accounts/` — `login.html`, `register.html`, `provider_register.html`
- `customer/` — `dashboard.html`, `profile.html`, `addresses.html`, `bookings.html`
- `professional/` — `dashboard.html`, `profile.html`, `verification.html`, `jobs.html`, `work_proof.html`, `earnings.html`, `public_profile.html`
- `services/` — `list.html`, `category_detail.html`, `service_detail.html`
- `bookings/` — `book.html`, `tracking.html`, `confirm_completion.html`, `emergency.html`
- `payments/` — `checkout.html`, `invoice.html`
- `reviews/` — `create.html`
- `complaints/` — `create.html`, `list.html`, `detail.html`
- `messaging/` — `chat.html`
- `notifications/` — `list.html`
- `admin_dashboard/` — `index.html`, `users.html`, `verifications.html`, `bookings.html`, `complaints.html`, `resolve_complaint.html`
- `errors/` — `400.html`, `403.html`, `404.html`, `500.html`

### Static Assets (`static/`)
- `css/style.css` — Custom design system (Forest green `#0F4A3C`, Amber gold `#FBBF24`)
- `js/main.js` — Interactive location selector, dynamic price calculator, toast dismissals

### React 18 + Vite SPA Showcase (`frontend/`)
- `package.json`, `vite.config.js`, `index.html`
- `src/main.jsx`, `src/App.jsx`, `src/index.css`
- `src/data/mockData.js`
- `src/components/` (Navbar, HeroBanner, TrustRibbon, EmergencyBanner, CategoryGrid, PackageCards, CommercialSpaces, WhyChooseUs, HowItWorks, LeadCaptureBanner, BookingModal, WorkProofModal, Footer)
- `.github/workflows/deploy.yml` — Automated GitHub Pages deployment pipeline

---

## 2. Excluded Files
- Virtual environment (`venv/`)
- Cache directories (`__pycache__/`, `*.pyc`)
- Node modules (`frontend/node_modules/`)
- Real secret production API keys
