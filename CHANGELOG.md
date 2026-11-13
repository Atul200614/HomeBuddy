# HomeBuddy Project Changelog (CHANGELOG.md)
**Project Owner:** Atul Patel (TYBSc Computer Science)  

---

### [v2.0.0] - November 2026 (Complete Release)
- **Sessions 01 & 02:**
  - Authored comprehensive Software Requirements Specification (`SRS.md`) with 30-requirement Traceability Matrix (RTM).
  - Designed normalized relational schema and data dictionary in `DATABASE_DESIGN.md`.
  - Architected dual-ready system (Django + MySQL Backend with REST API + React/Vite SPA Client in `frontend/`).
- **Sessions 03 & 04:**
  - Initialized Django project configuration (`config/settings.py`, `config/urls.py`, `manage.py`, `.env`).
  - Implemented custom User model, CustomerProfile, and ProviderProfile.
  - Built authentication controllers, registration views, and role-based access decorators (`@customer_required`, `@provider_required`, `@admin_required`).
- **Sessions 05, 06 & 07:**
  - Designed full UI system matching reference screenshots from `safsafaiwala.com` (Deep Forest Green `#0F4A3C`, Sunlight Amber `#FBBF24`).
  - Built base layout with location dropdown selector (`Pune, Maharashtra`), search bar, and contact hotline.
  - Implemented public landing page, category grid, BHK package cards, trust ribbon, and customer dashboard.
  - Created address book management CRUD for customers.
- **Sessions 08, 09 & 10:**
  - Implemented professional onboarding, skills management, and service area configuration.
  - Built KYC verification document upload model and admin approval workflow for verified badges.
  - Developed provider service pricing and availability configuration.
- **Sessions 11, 12 & 13:**
  - Built multi-criteria service search and discovery with pincode/locality filtering.
  - Engineered booking state machine engine (`REQUESTED`, `ACCEPTED`, `EN_ROUTE`, `ARRIVED`, `IN_PROGRESS`, `WORK_PROOF_SUBMITTED`, `COMPLETED`, `CANCELLED`).
  - Built Emergency Express Dispatch workflow for urgent repairs.
  - Created mandatory work proof verification system (before-and-after photo upload + customer sign-off).
- **Sessions 14 & 15:**
  - Implemented Razorpay test mode online payment with callback signature verification and Cash on Service (COS) workflow.
  - Built platform commission engine (10% deduction) and technician earnings ledger.
  - Built digital printable tax invoice generation system.
- **Sessions 16, 17 & 18:**
  - Implemented customer reviews, 1-5 star ratings, and automatic provider score recalculation.
  - Built dispute redressal and complaint ticketing module with evidence attachment.
  - Built booking-linked customer-provider chat and in-app notification center.
  - Built Admin Command Center with real-time SQL aggregated metrics.
- **Sessions 19 & 20:**
  - Built modern React 18 + Vite frontend Single Page Application in `/frontend` matching reference designs.
  - Configured GitHub Actions deployment workflow for GitHub Pages.
  - Created database seed command (`python manage.py seed_homebuddy`) with realistic Pune demo data.
  - Compiled complete `INSTALLATION.md`, `README.md`, `TEST_REPORT.md`, `ZIP_MANIFEST.md`, and academic viva presentation guide.
