# HomeBuddy
HomeBuddy: End-to-end local home services platform with dedicated Customer, Service Provider, and Admin panels, emergency bookings, work-proof verification, and automated payouts.
# 🏠 HomeBuddy — On-Demand Home Services Platform

**HomeBuddy** is a full-stack web application that connects customers with verified local professionals for residential and commercial home services. Built with a modular **Django** backend and a **React (Vite)** frontend, it manages the entire service lifecycle—from browsing service packages and live booking tracking to work-proof verification, Razorpay checkout, and automated provider payouts.

---

## ✨ Key Features

### 👤 Customer Portal
* **Service Discovery & Packages:** Browse service categories, view detailed service pages, and book curated home or commercial space packages.
* **Standard & Emergency Bookings:** Schedule standard appointments or request urgent assistance via a dedicated emergency booking flow.
* **Live Tracking & Completion:** Track active booking statuses in real time and confirm job completion[cite: 1].
* **Secure Payments & Invoicing:** Integrated **Razorpay** checkout with downloadable digital invoices[cite: 1].
* **Communication & Support:** Direct in-app messaging with service professionals, push/in-app notifications, reviews, and a formal complaint resolution system[cite: 1].

### 🛠️ Service Provider (Professional) Portal
* **Verification & Public Profile:** Onboarding workflow with document verification and public-facing professional profiles[cite: 1].
* **Job Management & Work Proof:** Accept/manage assigned jobs and upload before/after work proof upon completion[cite: 1].
* **Earnings Dashboard:** Track completed jobs, revenue history, and payout statuses[cite: 1].

### 🛡️ Admin Dashboard
* **Platform Oversight:** Centralized control panel to manage users, bookings, and platform analytics[cite: 1].
* **Provider Verification:** Review and approve service professional credentials[cite: 1].
* **Financial Operations:** Monitor incoming payments and manage provider payouts[cite: 1].
* **Dispute Resolution:** Investigate and resolve customer complaints[cite: 1].

---

## 🏗️ Tech Stack & Architecture

* **Backend:** Python, Django (Modular Multi-App Architecture + REST API endpoints)[cite: 1]
* **Frontend:** React, Vite, JavaScript (ES6+), HTML5, CSS3[cite: 1]
* **Payments:** Razorpay Payment Gateway[cite: 1]
* **CI/CD:** GitHub Actions (`deploy.yml`)[cite: 1]

### Project Structure
```text
├── .github/workflows/   # CI/CD deployment pipeline[cite: 1]
├── apps/                # Modular Django applications[cite: 1]
│   ├── accounts/        # Role-based authentication (Customer, Provider, Admin)[cite: 1]
│   ├── admin_dashboard/ # Platform administration & analytics[cite: 1]
│   ├── bookings/        # Standard/emergency bookings & tracking[cite: 1]
│   ├── complaints/      # Dispute & ticket management[cite: 1]
│   ├── core/            # Shared utilities, sitemaps & DB seeders[cite: 1]
│   ├── customers/       # Customer profiles & address book[cite: 1]
│   ├── messaging/       # Real-time customer-provider chat[cite: 1]
│   ├── notifications/   # Alert & notification service[cite: 1]
│   ├── payments/        # Razorpay integration & invoicing[cite: 1]
│   ├── professionals/   # Provider profiles, earnings & work proof[cite: 1]
│   ├── reviews/         # Service ratings & feedback[cite: 1]
│   └── services/        # Service catalog & categories[cite: 1]
├── config/              # Django project settings, ASGI/WSGI & URL routing[cite: 1]
├── frontend/            # React + Vite frontend application[cite: 1]
├── static/              # Global static assets (CSS/JS)[cite: 1]
└── templates/           # Django server-rendered templates[cite: 1]
