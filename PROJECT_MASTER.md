# HomeBuddy — Project Master Document
**Project:** HomeBuddy – Smart Home Service Booking Web Application  
**Project Owner:** Atul Patel  
**Academic Level:** TYBSc Computer Science Mini Project  
**Author / Team:** Complete Full-Stack Engineering & Architectural Team  
**Date:** November 2026  
**Version:** 2.0  

---

## 1. Executive Summary & Project Overview
HomeBuddy is an on-demand, multi-sided home service booking marketplace engineered to bridge the gap between urban households (customers) seeking reliable, skilled domestic services and independent skilled professionals (technicians/service providers) seeking livelihood opportunities and market reach. 

Unlike simple service directories or corporate job boards, HomeBuddy provides end-to-end lifecycle management:
1. **Discovery & Matching:** Location-based and category-based filtering for verified domestic workers (Electricians, Plumbers, Deep Cleaners, Carpenters, Painters, Cooks, Appliance Technicians).
2. **Transparent Booking Engine:** Real-time slot booking, task-based & hourly pricing, and emergency request dispatching.
3. **Trust & Quality Assurance:** Mandatory multi-step professional onboarding, admin document verification, tamper-evident badge system, and before-and-after photographic work proof.
4. **Financial Settlement:** Cash-on-service and secure online payment gateway (Razorpay test mode) with automated platform commission deduction, financial ledger, and digital PDF invoice generation.
5. **Accountability:** Customer reviews, rating aggregations, dispute and complaint redressal system, and customer-provider chat communication.

---

## 2. Core Stakeholders & Academic Context
- **Candidate:** Atul Patel (TYBSc Computer Science)
- **Course Module:** Final Year Mini Project / Capstone Project
- **Key Objectives:** Demonstrate mastery in full-stack web architecture, relational schema normalization (MySQL), secure role-based access control (RBAC), state machine workflows, payment integration, responsive UI/UX design, and software engineering rigor (SRS, traceability, testing, and documentation).

---

## 3. Technology Stack & Architectural Decision

### 3.1 Primary Academic Specification (Prompt V2.0 Section 3)
- **Backend:** Python 3.10+ / 3.11+, Django 5.x Web Framework, Django ORM, Django Authentication & RBAC, Django Forms & Validation Services.
- **Database:** MySQL Server 8.0+ (InnoDB storage engine, normalized schema, foreign key constraints, indexes, decimal precision for monetary fields).
- **Frontend Core:** HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3+, Bootstrap Icons / FontAwesome.

### 3.2 Stack Reconciliation & Hosting Clarification (Client Request vs Academic Stack)
- The user expressed interest in React + Vite for seamless GitHub deployment and hosting, while Master Prompt V2.0 strictly enforces Python + Django + MySQL for TYBSc academic validity.
- **Architectural Solution:**
  1. **Dual-Ready Clean Architecture:** The Django backend is structured with modular apps and clean service layers, serving both Django server-rendered views (with Bootstrap 5 design matching the `safsafaiwala.com` reference) AND RESTful API endpoints.
  2. **React + Vite Frontend Client:** A standalone modern React + Vite application (styled with Tailwind CSS or Bootstrap 5 matching the design reference) can be built in a dedicated `/frontend` workspace, consuming the Django REST API or deploying as a static showcase/client on GitHub Pages/Vercel.
  3. This ensures 100% compliance with university examiners evaluating Django + MySQL source code, while providing Atul with a live hosted React + Vite portfolio on GitHub.

---

## 4. UI/UX Reference Analysis (`safsafaiwala.com`)
Based on the visual assets provided in the project reference screenshots:
- **Primary Color:** Deep Forest Green (`#0F4A3C` / `#166534`) conveying cleanliness, hygiene, trust, and professionalism.
- **Secondary / Accent Color:** Vibrant Gold / Warm Amber (`#FBBF24` / `#EAB308`) for Call-to-Action (CTA) buttons, discount tags, and ratings.
- **Neutral Palette:** Crisp White (`#FFFFFF`), Soft Slate Gray (`#F8FAFC`, `#F1F5F9`), and Dark Charcoal text (`#0F172A`).
- **Key Layout Elements:**
  - Sticky Top Navigation Bar: Brand logo, location dropdown selector with "Home / Office" pill toggles, dynamic search bar, support hotline badge, prominent "Book A Service" button, user profile avatar, and cart/booking count.
  - Hero Showcase: Rounded green container showcasing festival offers, promotional copy, verified badge, and quick booking triggers.
  - Value Proposition Ribbon: ISO 9001:2015 certification badge, 100% background-checked staff, dedicated teams, and eco-friendly products.
  - Service Category Selector: Card grid with 3D/flat icons for deep cleaning, plumbing, carpentry, electrical, painting, and maintenance.
  - Tiered Package Cards: BHK-based pricing (1 BHK, 2 BHK, 3 BHK, 4 BHK) and hourly pricing with "Starts at ₹..." badges.
  - Multi-Step Workflow Showcase: 1) Select Service, 2) Verified Provider Arrives, 3) Job Completed with Satisfaction Guarantee.
  - Footer: Multi-column navigation, mobile app download prompts, supported cities list, copyright, and legal policies.

---

## 5. Security & Engineering Standards
1. **Password Security:** PBKDF2 with SHA256 password hashing.
2. **Access Control:** Server-side RBAC decorators and object-level authorization (preventing Insecure Direct Object References - IDOR).
3. **Data Integrity:** Database transactions (`transaction.atomic`) for booking status transitions and financial ledger updates.
4. **Monetary Precision:** `DecimalField(max_digits=10, decimal_places=2)` for all monetary values (never floating-point).
5. **Private Media Handling:** Verification documents and sensitive customer work proofs stored in non-public protected media paths.
