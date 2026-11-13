# Architectural & Technical Decisions Log (DECISIONS.md)
## Project: HomeBuddy – Smart Home Service Booking Marketplace
**Owner:** Atul Patel (TYBSc Computer Science)  
**Session:** 01 — Requirements & Planning Baseline  

---

## Decision 01: Dual-Stack Reconciliation (Django + MySQL Academic Core + React/Vite Hosted Client)
- **Context:** The Master Prompt V2.0 specifies a Python + Django + MySQL + Bootstrap 5 stack as mandatory for academic validity and evaluation by university examiners. At the same time, the user requested: *"Use react and vite js so i can upload on GitHub and publish and host Use this image as reference to create my website"*.
- **Options Evaluated:**
  1. *React-only SPA:* Violates university academic synopsis requirements which require Django backend, Django ORM, and MySQL schema migrations.
  2. *Django-only monolith:* Does not fulfill the user's desire to push a modern Vite + React build to GitHub Pages or cloud hosting.
  3. *Dual-Ready Hybrid Architecture (Selected):*
     - Build the Django + MySQL core platform with full REST API endpoints and native Django views (using Bootstrap 5 styled identically to the reference design).
     - Build a high-performance React + Vite Single Page Application (SPA) in a `/frontend` directory configured with GitHub Pages / Vercel deployment scripts.
     - Both clients interface with the identical business logic, models, and workflows.
- **Consequences:** 100% compliance with college viva examiners inspecting Django + MySQL, while giving Atul a live modern React + Vite website hosted on GitHub.

---

## Decision 02: Database Engine Strategy & Testability
- **Context:** Master Prompt mandates MySQL 8.0+ for final evaluation and documentation, while development and automated testing environments on developer machines may require zero-friction execution.
- **Decision:**
  - Standard database configuration points to MySQL (`django.db.backends.mysql`) with PyMySQL / mysqlclient.
  - Environment variable `DJANGO_DB_ENGINE` defaults to MySQL in `.env.example`, with seamless test execution fallback to SQLite in memory when running automated test suites (`manage.py test`).
  - Strict typing (`DecimalField` for currency, `DateTimeField` with timezone support) ensures 100% dialect compatibility between MySQL and test runners.

---

## Decision 03: UI Design System & Component Library (Derived from Reference Images)
- **Context:** The user provided 11 photos of `safsafaiwala.com` showing a clean, high-conversion green-and-gold aesthetic.
- **Design Tokens Adopted:**
  - **Primary Brand Color:** Emerald / Forest Green (`#0F4A3C` / `#166534`)
  - **Secondary Brand Color:** Sunlight Gold (`#FBBF24` / `#EAB308`)
  - **Background Neutral:** Soft Slate (`#F8FAFC`)
  - **Surface Neutral:** Pure White (`#FFFFFF`) with 1px border (`#E2E8F0`) and `box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.05)`
  - **Corner Radius:** `12px` to `16px` for cards, `50rem` (pill) for action badges and location chips.
  - **Typography:** Inter / system-ui for high legibility on mobile and desktop.
  - **Key Components:**
    1. Top navigation with sticky location selector (`Pune, Maharashtra`) and Home/Office pill selector.
    2. Hero banner with promotional countdown badge and direct CTA.
    3. Trust verification bar (ISO 9001 certified, 100% background checked staff).
    4. 3D / Flat category icons for domestic services.
    5. Service pricing cards with "Starts at ₹..." badges.

---

## Decision 04: Booking State Machine & Work Proof Verification
- **Context:** Synopsis requirements 8, 16, and 17 mandate service booking, before-and-after photos, and written completion confirmation.
- **Decision:**
  - Work proof is enforced as a discrete intermediate state (`WORK_PROOF_SUBMITTED`).
  - Technicians cannot mark a job completed without uploading both a `before_photo` and an `after_photo`.
  - Customers inspect the uploaded proofs in their booking tracking view before granting final sign-off (`confirm_completion`).
  - This prevents fraud and provides an unalterable audit trail for disputes.

---

## Decision 05: Payment Lifecycle & Security
- **Context:** Requirements 13 and 14 demand Online Payment (Razorpay test mode) and Cash on Service (COS).
- **Decision:**
  - Online payments initiate a server-side order with Razorpay API; callback generates HMAC-SHA256 signature verification before marking payment as `SUCCESS`.
  - Cash on Service bookings create a pending payment record that is updated to `PAID` upon customer sign-off and technician receipt confirmation.
  - Platform commission (e.g. 10%) is automatically deducted from gross booking amount and credited to platform account while net amount is credited to technician's `EarningsLedger`.
