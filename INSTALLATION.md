# HomeBuddy — Complete Installation & Execution Guide (INSTALLATION.md)
**Project Owner:** Atul Patel  
**Course:** TYBSc Computer Science Mini Project  
**Operating System:** Windows 10 / 11  
**Architecture:** Django 5.x + MySQL 8.0 (Backend) & React 18 + Vite (Frontend)  

---

## 1. Prerequisites & Required Software
Ensure you have the following installed on your Windows machine:
1. **Python 3.10+ / 3.11+ / 3.12+** (From [python.org](https://www.python.org/downloads/) — Make sure to check *"Add python.exe to PATH"* during installation).
2. **Node.js v18+ or v20+** (From [nodejs.org](https://nodejs.org/)).
3. **MySQL Server 8.0+** or **XAMPP / WampServer** (running MySQL on port 3306).
4. **Git** and **VS Code**.

---

## 2. Step-by-Step Setup Guide

### Step 2.1: Clone or Open the Project
Open **PowerShell** or **Command Prompt** (CMD) inside the project folder:
```powershell
cd "c:\Users\Vipin\Documents\HOMEBUDDY —"
```

---

### Step 2.2: Setup Python Virtual Environment (Backend)
```powershell
# 1. Create a virtual environment
python -m venv venv

# 2. Activate the virtual environment
# In PowerShell:
.\venv\Scripts\Activate.ps1
# Or in Command Prompt (CMD):
venv\Scripts\activate.bat

# 3. Upgrade pip and install all backend requirements
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Step 2.3: Configure the Database

#### Option A: Using MySQL 8.0 (Recommended for Final College Evaluation)
1. Open MySQL Workbench, phpMyAdmin, or MySQL Command Line Client.
2. Create the database:
   ```sql
   CREATE DATABASE homebuddy_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
3. Verify your `.env` file settings:
   ```env
   DB_ENGINE=mysql
   DB_NAME=homebuddy_db
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_HOST=127.0.0.1
   DB_PORT=3306
   USE_SQLITE_FALLBACK=False
   ```

#### Option B: Standalone Quick Run (Zero Configuration SQLite)
If MySQL is not installed or running, HomeBuddy automatically falls back to SQLite dialect compatibility without any errors:
```env
USE_SQLITE_FALLBACK=True
```

---

### Step 2.4: Apply Database Migrations
Run the standard Django migration commands:
```powershell
python manage.py makemigrations accounts customers professionals services bookings payments reviews complaints messaging notifications admin_dashboard core
python manage.py migrate
```

---

### Step 2.5: Load Realistic Sample Data (One-Click Seed)
HomeBuddy includes an automated demonstration seed command that populates verified Pune technicians, deep cleaning packages, and realistic workflows:
```powershell
python manage.py seed_homebuddy
```

#### Pre-Configured Test Credentials:
| Account Role | Email Address | Password | Permissions |
|---|---|---|---|
| **Admin** | `admin@homebuddy.local` | `Admin@123` | Full Admin Command Center & Django Admin |
| **Customer** | `rahul.sharma@example.com` | `Customer@123` | Booking, saved addresses in Kothrud, invoices |
| **Technician (Cleaner)** | `suresh.cleaner@example.com` | `Provider@123` | Verified badge, jobs, work proofs, earnings |
| **Technician (Electrician)** | `vikram.electric@example.com` | `Provider@123` | Verified badge, electrical repair |

---

### Step 2.6: Start the Django Development Server
```powershell
python manage.py runserver
```
Visit in your web browser:
- **HomeBuddy Portal:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Admin Command Center:** [http://127.0.0.1:8000/admin-panel/](http://127.0.0.1:8000/admin-panel/)
- **Django Built-in Admin:** [http://127.0.0.1:8000/django-admin/](http://127.0.0.1:8000/django-admin/)

---

## 3. Running the Modern React + Vite Frontend Client

To run the interactive React showcase client:
```powershell
# Open a new terminal tab/window
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
Open [http://localhost:5173/](http://localhost:5173/) or [http://localhost:3000/](http://localhost:3000/) in your browser.

---

## 4. Hosting on GitHub & GitHub Pages

To publish on GitHub and host for free:
1. Initialize git and commit:
   ```powershell
   git init
   git add .
   git commit -m "HomeBuddy V2.0 - Complete Marketplace by Atul Patel"
   ```
2. Create a new repository on your GitHub account (e.g. `HomeBuddy`).
3. Link and push:
   ```powershell
   git remote add origin https://github.com/your-username/HomeBuddy.git
   git branch -M main
   git push -u origin main
   ```
4. The automated GitHub Action in `.github/workflows/deploy.yml` will automatically build the Vite SPA and deploy it to GitHub Pages!

---

## 5. Troubleshooting Common Issues
- **`ModuleNotFoundError: No module named 'django'`:** Make sure your virtual environment is activated (`.\venv\Scripts\activate`).
- **`Access Denied for user 'root'@'localhost'`:** Check your MySQL password in `.env`.
- **`Port 8000 is in use`:** Run `python manage.py runserver 8080` to run on an alternative port.
