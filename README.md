# Billing System — Phase 1
### BCA 5th Semester Final Project | Shoolini Online

**Stack:** Python Flask + MySQL + Tailwind CSS

---

## 📁 Project Structure

```
billing_system/
├── app/
│   ├── __init__.py       # App factory
│   ├── models.py         # User model (Flask-Login)
│   ├── auth.py           # Login / Logout / Change Password
│   ├── dashboard.py      # Dashboard stats & view
│   └── main.py           # Root redirect + error handlers
├── templates/
│   ├── base.html         # Sidebar layout (all pages extend this)
│   ├── auth/
│   │   ├── login.html
│   │   └── change_password.html
│   ├── dashboard/
│   │   └── index.html
│   └── errors/
│       ├── 404.html
│       ├── 403.html
│       └── 500.html
├── static/               # CSS, JS, images (add custom assets here)
├── instance/             # Flask instance folder (auto-created)
├── .env                  # Environment config (edit this first!)
├── schema.sql            # MySQL database schema
├── seed_db.py            # Creates default users
├── run.py                # Dev server entry point
└── requirements.txt      # Python dependencies
```

---

## ⚡ Setup (Step by Step)

### Step 1 — Install Python packages
```bash
pip install -r requirements.txt
```

### Step 2 — Setup MySQL database
Open MySQL Workbench (or XAMPP phpMyAdmin) and run:
```sql
SOURCE /path/to/billing_system/schema.sql;
```
Or paste the contents of `schema.sql` into the SQL editor and run.

### Step 3 — Configure `.env`
Edit `.env` and set your MySQL password:
```
MYSQL_PASSWORD=your_mysql_password_here
```
Change the `SECRET_KEY` to something random for security.

### Step 4 — Seed default users
```bash
python seed_db.py
```
This creates 3 users:
| Username | Password     | Role    |
|----------|-------------|---------|
| admin    | admin@123   | Admin   |
| manager  | manager@123 | Manager |
| cashier  | cashier@123 | Cashier |

### Step 5 — Run the app
```bash
python run.py
```
Open browser → **http://localhost:5000**

---

## 🔐 Login
- Go to `http://localhost:5000`
- Login with `admin` / `admin@123`
- **Change your password immediately** via "Change Password" in sidebar

---

## 📦 Phase Roadmap

| Phase | Status | Modules |
|-------|--------|---------|
| **Phase 1** | ✅ Complete | Login, Auth, Dashboard |
| **Phase 2** | 🔜 Next | Inventory, Billing, Cart, GST, Payment |
| **Phase 3** | ⏳ Later | Invoices, Stock Update, Returns, Reports, Admin Settings |

---

## 🛠 Troubleshooting

**`ModuleNotFoundError: No module named 'MySQLdb'`**
```bash
pip install mysqlclient
# On Ubuntu/Debian: sudo apt-get install libmysqlclient-dev python3-dev
```

**`OperationalError: (2002) Can't connect to MySQL server`**
- Make sure XAMPP/WAMP MySQL service is running
- Check `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD` in `.env`

**`Table 'billing_system.users' doesn't exist`**
- Run `schema.sql` in MySQL first, then `seed_db.py`

---

Built with ❤️ for Shoolini Online BCA Final Project
