# HomeBuddy Task Breakdown & 20-Session Roadmap (TASKS.md)
**Project Owner:** Atul Patel (TYBSc Computer Science)  
**Status Tracker:** Active  

---

### [x] SESSION 01 — Requirements, Scope & Project Planning
- [x] Analyze uploaded reference images (`safsafaiwala.com` layout, color schemes, components).
- [x] Map all 30 synopsis requirements to software modules and database entities.
- [x] Reconcile technology stack (Django + MySQL + React/Vite Dual Architecture).
- [x] Author core documentation files: `PROJECT_MASTER.md`, `SRS.md`, `DECISIONS.md`, `TASKS.md`, `PROGRESS.md`, `HANDOFF.md`.
- [x] Complete Page Inventory and Role-Permission Matrix.
- [x] Document risk register, acceptance criteria, and user confirmations.

---

### [ ] SESSION 02 — Architecture & Database Design
- [ ] Finalize Django apps structure (`accounts`, `customers`, `professionals`, `services`, `bookings`, `payments`, `reviews`, `complaints`, `messaging`, `notifications`, `dashboard`).
- [ ] Create detailed Entity-Relationship (ER) diagram in Mermaid.
- [ ] Author comprehensive Data Dictionary (`DATABASE_DESIGN.md`).
- [ ] Define indexing, foreign key cascade behaviors, and unique constraints.
- [ ] Define Django REST API serialization schema.

---

### [ ] SESSION 03 — Environment Setup & Foundation
- [ ] Initialize Python virtual environment and `requirements.txt`.
- [ ] Initialize Django project (`config`) and modular `apps/` directory.
- [ ] Setup MySQL connection configuration with `.env` management.
- [ ] Configure static and media assets pipeline.
- [ ] Establish initial health-check endpoint and verify DB connectivity.
- [ ] Setup Git repository `.gitignore` and initial commit.

---

### [ ] SESSION 04 — Authentication, Roles & Profiles
- [ ] Create Custom User model with email/phone login capability.
- [ ] Implement Customer & Service Provider registration views.
- [ ] Build Login, Logout, and Password Reset workflows.
- [ ] Establish role-based redirection and view decorators.
- [ ] Write unit tests for user authentication and permission isolation.

---

### [ ] SESSION 05 — Premium Public Website & Design System
- [ ] Build base templates and reusable UI component macros.
- [ ] Implement design system styled after reference images (Emerald Green `#0F4A3C`, Amber Gold `#FBBF24`).
- [ ] Build responsive public homepage with hero banner, location selector, and trust badges.
- [ ] Implement public static pages (About Us, How It Works, FAQ, Terms, Privacy Policy).
- [ ] Test mobile responsiveness across viewports.

---

### [ ] SESSION 06 — Customer Profile & Dashboard
- [ ] Implement customer profile management view (avatar, phone, personal details).
- [ ] Implement saved address book CRUD (Home, Office, Other addresses with pincode).
- [ ] Build customer dashboard shell with active booking summaries.
- [ ] Add customer unit tests.

---

### [ ] SESSION 07 — Service Catalog & Management
- [ ] Implement Service Categories model and views (Cleaning, Electrical, Plumbing, Painting, Carpentry, Cooking).
- [ ] Implement individual Services with base prices, hourly/task rates, and descriptions.
- [ ] Admin management interface for categories and services.
- [ ] Seed standard service catalog data.

---

### [ ] SESSION 08 — Professional Onboarding & Profile
- [ ] Build multi-step technician profile setup (skills, experience, service areas).
- [ ] Implement service selection for technicians (which services they provide).
- [ ] Profile photo upload and bio management.
- [ ] Unit tests for provider profile completion.

---

### [ ] SESSION 09 — Verification System & Badges
- [ ] Implement KYC document upload model (Aadhaar/Govt ID, Police Verification, Skill Certificate).
- [ ] Secure media storage for private documents (prevent public access).
- [ ] Admin verification queue view (Approve / Reject with remarks).
- [ ] Verified badge component rendered on approved technician profiles.

---

### [ ] SESSION 10 — Provider Services, Pricing & Availability
- [ ] Provider service custom pricing management (hourly vs fixed).
- [ ] Availability calendar / working hours configuration.
- [ ] Service area radius / locality selection.
- [ ] Provider dashboard overview.

---

### [ ] SESSION 11 — Search & Location-Based Discovery
- [ ] Search services by keyword and category.
- [ ] Filter by locality/pincode, price range, ratings, and verified badge.
- [ ] Provider comparison view.
- [ ] Search pagination and empty state handling.

---

### [ ] SESSION 12 — Core Booking Engine
- [ ] Multi-step booking form (Service -> Date/Time Slot -> Address -> Special Notes).
- [ ] Conflict prevention logic (prevent double-booking same provider at same time).
- [ ] Provider booking request notification.
- [ ] Provider Accept / Reject action with mandatory reason on rejection.
- [ ] Booking status tracking view for customer and provider.

---

### [ ] SESSION 13 — Emergency Booking & Job Execution
- [ ] Emergency booking toggle with immediate broadcast to nearby verified providers.
- [ ] Technician arrival check-in button ("Mark Arrived").
- [ ] Mandatory work proof submission: Before-work and After-work photo uploads.
- [ ] Customer confirmation & sign-off workflow.
- [ ] Cancellation & rescheduling rules.

---

### [ ] SESSION 14 — Payment Integration (Online & Cash)
- [ ] Razorpay test mode integration: Order creation, checkout modal, webhook/callback signature verification.
- [ ] Cash on Service (COS) workflow with technician receipt acknowledgment.
- [ ] Payment transaction history and failure recovery.
- [ ] Unit and integration tests for payment flows.

---

### [ ] SESSION 15 — Invoices, Commission & Financial Ledger
- [ ] Automated platform commission calculation (configurable percentage).
- [ ] Financial earnings ledger for service providers (Gross, Commission, Net).
- [ ] Provider payout request submission and admin approval.
- [ ] Dynamic PDF / printable digital invoice generation.

---

### [ ] SESSION 16 — Reviews, Ratings & Complaints
- [ ] Post-service review submission (1-5 stars + written feedback).
- [ ] Provider average rating aggregation logic.
- [ ] Customer dispute / complaint ticket submission with file attachment.
- [ ] Admin complaint investigation, remarks, and resolution status.

---

### [ ] SESSION 17 — In-App Chat & Notifications
- [ ] Booking-linked customer-technician direct messaging.
- [ ] In-app notification center (booking updates, arrivals, payouts).
- [ ] Email notification service configuration with development fallback.

---

### [ ] SESSION 18 — Admin Dashboard & Business Intelligence
- [ ] Master admin dashboard with real-time SQL aggregation metrics (users, bookings, revenue, payouts).
- [ ] User and provider management tables with activation/suspension toggles.
- [ ] Booking and complaint moderation tables.
- [ ] Financial report exports (CSV / PDF).

---

### [ ] SESSION 19 — React/Vite Client & Full Integration QA
- [ ] Build React + Vite modern client matching reference design in `/frontend`.
- [ ] Connect React client to Django REST API (or configure standalone showcase).
- [ ] Full end-to-end integration testing across all 4 user roles.
- [ ] Security testing (CSRF, SQL injection, IDOR, permission bypass).
- [ ] Generate comprehensive `TEST_REPORT.md`.

---

### [ ] SESSION 20 — Packaging, Academic Documentation & Viva Preparation
- [ ] Finalize `INSTALLATION.md`, `README.md`, `ARCHITECTURE.md`, `DATABASE_DESIGN.md`.
- [ ] Compile academic viva presentation guide and defense answers.
- [ ] Create clean, verified project ZIP archive.
- [ ] Verify extraction, sample data loading, and startup.
