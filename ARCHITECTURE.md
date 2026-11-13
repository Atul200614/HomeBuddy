# System Architecture & Technical Specifications (ARCHITECTURE.md)
## Project: HomeBuddy – Smart Home Service Booking Marketplace
**Owner:** Atul Patel (TYBSc Computer Science)  
**Architecture:** Modular Layered Django 5.x Web Application + RESTful API Services + React/Vite Client Showcase  

---

## 1. High-Level Architecture Diagram

```
+-----------------------------------------------------------------------------------+
|                                  CLIENT LAYER                                     |
|  +------------------------------------+   +------------------------------------+  |
|  |     Django Server-Rendered UI      |   |        React 18 + Vite SPA         |  |
|  |   (Bootstrap 5.3 + Custom CSS)     |   |    (Tailwind CSS + Lucide Icons)   |  |
|  |   Styled to safsafaiwala.com       |   |      Hosted on GitHub / Vercel     |  |
|  +-----------------+------------------+   +-----------------+------------------+  |
+--------------------|----------------------------------------|---------------------+
                     | Form Posts / HTML Pages                | JSON Fetch / REST API
                     v                                        v
+--------------------+----------------------------------------+---------------------+
|                              DJANGO APPLICATION LAYER                             |
|  +-----------------------------------------------------------------------------+  |
|  |                              URL Routing & Middlewares                      |  |
|  |        (SecurityMiddleware, SessionMiddleware, CSRF, RoleRedirect)          |  |
|  +-----------------------------------------------------------------------------+  |
|                                         |                                         |
|  +--------------------+-----------------+--------------------+------------------+  |
|  | View Layer         | Service Layer (Business Logic)       | DRF / API Views  |  |
|  | - accounts         | - BookingStateMachine                | - /api/v1/auth   |  |
|  | - customers        | - RazorpaySignatureService           | - /api/v1/services| |
|  | - professionals    | - CommissionEarningsCalculator       | - /api/v1/bookings||
|  | - services         | - WorkProofValidator                 | - /api/v1/reviews|  |
|  | - bookings         | - NotificationDispatcher             +------------------+  |
|  | - payments         | - KYCVerificationPipeline                                  |
|  | - reviews/complaints                                                            |
|  +--------------------+---------------------------------------------------------+  |
+-----------------------------------------|-----------------------------------------+
                                          v
+-----------------------------------------------------------------------------------+
|                                DATA ACCESS LAYER                                  |
|  +-----------------------------------------------------------------------------+  |
|  |                          Django ORM (Object-Relational)                     |  |
|  |   - Model Queries & Managers (Atomic Transactions, Select Related, Indexing)|  |
|  +-----------------------------------------------------------------------------+  |
|                                         |                                         |
|                                         v                                         |
|  +-----------------------------------------------------------------------------+  |
|  |                       MySQL 8.0+ Database (InnoDB)                          |  |
|  |            (Accounts, Services, Bookings, Payments, Proofs, Reviews)        |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

---

## 2. Directory Layout & Modular Structure

```text
HomeBuddy/
├── manage.py                       # Django CLI controller
├── requirements.txt                # Python dependencies
├── .env.example                    # Sample environment configurations
├── README.md                       # Comprehensive setup and repository guide
├── PROJECT_MASTER.md               # Master blueprint
├── SRS.md                          # Software Requirements Specification
├── DATABASE_DESIGN.md              # ER diagram & Data dictionary
├── ARCHITECTURE.md                 # System architecture (this file)
├── TASKS.md                        # 20-session tasks and tracking
├── PROGRESS.md                     # Quality gate and milestone status
├── DECISIONS.md                    # Technical decisions log
├── TEST_REPORT.md                  # Test execution logs
├── HANDOFF.md                      # Session continuation file
│
├── config/                         # Core Django project configuration
│   ├── __init__.py
│   ├── settings.py                 # Multi-mode settings (MySQL, Static, Auth)
│   ├── urls.py                     # Root URL dispatcher
│   ├── asgi.py
│   └── wsgi.py
│
├── apps/                           # Domain-driven modular applications
│   ├── core/                       # Public pages, home, about, FAQ, error views
│   ├── accounts/                   # Custom User model, login, register, RBAC
│   ├── customers/                  # Customer profile, saved addresses
│   ├── professionals/              # Provider profile, skills, KYC docs, verification
│   ├── services/                   # Categories, services, search, pricing models
│   ├── bookings/                   # Booking engine, state machine, work proof photos
│   ├── payments/                   # Razorpay integration, cash, ledger, invoices
│   ├── reviews/                    # Rating calculations, customer reviews
│   ├── complaints/                 # Customer complaints, admin dispute management
│   ├── messaging/                  # Booking-linked messaging between user & provider
│   ├── notifications/              # In-app notifications & email dispatching
│   └── admin_dashboard/            # Custom admin management interface & metrics
│
├── static/                         # Static assets (CSS, JS, images, icons)
│   ├── css/
│   │   ├── custom.css              # Custom styling (Emerald Green, Amber Gold tokens)
│   │   └── bootstrap.min.css       # Bootstrap 5.3 distribution
│   ├── js/
│   │   ├── main.js                 # Global interactions, toasts, location selector
│   │   └── booking.js              # Real-time pricing calculations & date picker
│   └── images/
│       ├── logo.svg                # HomeBuddy brand badge
│       ├── hero-banner.png         # Green hero banner graphic
│       └── categories/             # 3D category icons (cleaning, plumbing, etc.)
│
├── media/                          # User-uploaded content (avatars, work proof)
│   ├── avatars/
│   ├── work_proofs/                # Before/After work photos
│   └── kyc_documents/              # Private, protected KYC files
│
├── templates/                      # Clean semantic HTML5 Django templates
│   ├── base.html                   # Master layout with navbar & footer
│   ├── public/                     # Landing page, categories, static pages
│   ├── accounts/                   # Register, login, role choice
│   ├── customer/                   # Customer dashboard, address book, bookings
│   ├── professional/               # Provider dashboard, incoming jobs, proof upload
│   ├── admin_dashboard/            # Metrics overview, KYC review, dispute resolution
│   ├── bookings/                   # Booking form, tracking, work proof review
│   ├── payments/                   # Checkout page, cash receipt, digital invoice
│   └── errors/                     # 400, 403, 404, 500 pages
│
└── frontend/                       # React 18 + Vite SPA client
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── components/             # Reusable UI components
        ├── pages/                  # Landing, Search, Booking, Dashboards
        └── services/               # API client
```

---

## 3. Django REST API Contracts

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/v1/auth/register/` | Register customer or professional | None |
| `POST` | `/api/v1/auth/login/` | Authenticate and obtain session/token | None |
| `GET` | `/api/v1/services/categories/` | List all active categories | None (Public) |
| `GET` | `/api/v1/services/` | Search services with category/pincode filters | None (Public) |
| `GET` | `/api/v1/services/<slug>/` | Get detailed service info & base pricing | None (Public) |
| `POST` | `/api/v1/bookings/` | Create a new service booking | Customer |
| `GET` | `/api/v1/bookings/my-bookings/`| List bookings for authenticated user | Customer / Provider |
| `GET` | `/api/v1/bookings/<id>/` | Detailed booking tracking & status history | Customer / Provider / Admin |
| `POST` | `/api/v1/bookings/<id>/accept/`| Provider accepts incoming booking | Assigned Provider |
| `POST` | `/api/v1/bookings/<id>/reject/`| Provider declines incoming booking | Assigned Provider |
| `POST` | `/api/v1/bookings/<id>/proof/` | Provider uploads before/after photos | Assigned Provider |
| `POST` | `/api/v1/bookings/<id>/confirm/`| Customer confirms completion | Customer |
| `POST` | `/api/v1/payments/create-order/`| Initialize Razorpay payment order | Customer |
| `POST` | `/api/v1/payments/verify/` | Verify Razorpay payment signature | Customer |
| `POST` | `/api/v1/reviews/` | Submit review and rating for completed job | Customer |
| `POST` | `/api/v1/complaints/` | Submit complaint ticket with evidence | Customer / Provider |
| `GET` | `/api/v1/notifications/` | Fetch unread notifications | Authenticated |
| `POST` | `/api/v1/notifications/<id>/read/` | Mark notification as read | Authenticated |

---

## 4. Role-Based Access Control (RBAC) Architecture

Django decorators enforce permission boundaries at the view level:
- `@login_required`: Authenticated users only.
- `@customer_required`: Ensures `request.user.role == 'CUSTOMER'`.
- `@provider_required`: Ensures `request.user.role == 'PROVIDER'`.
- `@admin_required`: Ensures `request.user.role == 'ADMIN'` or `is_staff`.
- **Object-Level Guard:** When accessing a booking, invoice, or conversation, the view explicitly checks:
  ```python
  if booking.customer.user != request.user and booking.provider.user != request.user and not request.user.is_staff:
      raise PermissionDenied("You do not have permission to view this booking.")
  ```
  This systematically prevents Insecure Direct Object Reference (IDOR) vulnerabilities.
