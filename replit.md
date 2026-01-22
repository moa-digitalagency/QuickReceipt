# QuickReceipt

## Overview
QuickReceipt is a web application for managing receipts, designed for freelancers and small businesses. It provides an intuitive interface for creating, managing, and sharing professional receipts with user authentication and multi-company support.

## Tech Stack
- **Backend**: Python Flask
- **Frontend**: HTML, JavaScript, Tailwind CSS (via CDN)
- **PDF Generation**: ReportLab
- **Image Processing**: Pillow
- **Data Storage**: PostgreSQL database (SQLAlchemy ORM)
- **Authentication**: Flask session-based with password hashing (Werkzeug)
- **Internationalization**: Custom i18n solution with French, English, and Arabic support

## Project Structure
```
├── app.py                 # Main Flask application entry point
├── init_db.py             # Database initialization with SQLAlchemy models
├── lang/                  # Language translations
│   └── translations.json  # i18n translations (FR, EN, AR)
├── models/                # Data models
│   ├── __init__.py
│   └── db_models.py       # SQLAlchemy model wrappers (User, Company, Client, Receipt, Settings)
├── routes/                # Flask route handlers
│   ├── __init__.py        # Route registration
│   ├── api.py             # API endpoints
│   ├── auth.py            # Authentication routes (login, logout)
│   ├── clients.py         # Client routes
│   ├── dashboard.py       # Dashboard routes
│   ├── receipts.py        # Receipt routes
│   ├── settings.py        # Settings routes (company management)
│   └── users.py           # User management routes (superadmin only)
├── security/              # Security utilities
│   └── __init__.py        # Secret key generation
├── services/              # Business logic services
│   ├── __init__.py
│   ├── pdf.py             # PDF A4 generation service (centered company info)
│   ├── thermal.py         # Thermal receipt image generation (48/57/58/80mm)
│   └── share.py           # WhatsApp/Email sharing service
├── static/
│   ├── favicon.svg        # Application favicon
│   └── uploads/           # Uploaded logos
├── templates/             # Jinja2 HTML templates
│   ├── base.html          # Base layout with navigation (responsive)
│   ├── login.html         # Login page
│   ├── dashboard.html     # Dashboard with stats
│   ├── clients.html       # Client list
│   ├── client_form.html   # Add/Edit client form
│   ├── company_form.html  # Add/Edit company form
│   ├── receipts.html      # Receipt list
│   ├── receipt_form.html  # Create receipt form
│   ├── receipt_saved.html # Post-save popup with download options
│   ├── receipt_view.html  # View receipt details
│   ├── settings.html      # Company management + thermal settings
│   ├── users.html         # User management (superadmin only)
│   └── user_form.html     # Add/Edit user form
└── utils/                 # Utility functions
    ├── __init__.py
    ├── files.py           # File handling utilities
    └── i18n.py            # Internationalization helpers
```

## Features
- **User Authentication**: Login/logout with role-based access control
  - Super Admin: Full access including user management
  - User: Standard access for receipt management
- **Complete Data Isolation**: Each user manages their own companies, clients, and receipts independently
  - user_id foreign key on companies, clients, receipts, and settings tables
  - All queries filtered by logged-in user's ID
- Dashboard with quick receipt creation and recent receipts overview
- Client management (CRUD) with name, WhatsApp, and email
- **Multi-company support**: Configure multiple companies in settings, select one per receipt
- Receipt creation with inline client/company quick-add
- PDF A4 generation with centered company information
- Thermal receipt image generation (48mm/57mm/58mm/80mm configurable with improved readability)
- Receipt history sorted by date
- **Optional ICE/SIRET**: Only displayed in receipts when provided
- **WhatsApp sharing**: Uses wa.me link with client's phone number
- Multilingual support (French, English, Arabic) with RTL support
- Fully responsive mobile design
- Pre-filled WhatsApp and email sharing with company details

## Authentication
- Default super admin account created on first run
- Credentials configured via environment variables:
  - `ADMIN_USERNAME`: Default admin username (default: "admin")
  - `ADMIN_PASSWORD`: Default admin password (default: "admin123")

## Running the Application
```bash
python app.py
```
The application runs on port 5000.

## Key Routes
- `/login` - Login page
- `/logout` - Logout
- `/` - Dashboard
- `/clients` - Client management
- `/receipts` - Receipt management
- `/receipts/add` - Create receipt with company/client selection
- `/receipts/saved/<id>` - Post-save popup with download options
- `/settings` - Company management + thermal paper settings
- `/settings/company/add` - Add new company
- `/settings/company/edit/<id>` - Edit company
- `/users` - User management (superadmin only)
- `/users/add` - Add user
- `/users/edit/<id>` - Edit user
- `/receipts/pdf/<id>` - Download receipt PDF A4
- `/receipts/thermal/<id>` - Download thermal receipt image
- `/set-locale/<locale>` - Change language (fr, en, ar)
- `/api/share/<id>` - Get share data for WhatsApp/Email

## Recent Changes
- Implemented complete data isolation: each user has separate companies, clients, receipts
- Renamed "company" role to "user" for clarity
- Added user_id foreign key to companies, clients, receipts, and settings tables
- All routes filter data by logged-in user's ID for security
- Added user authentication system with roles (superadmin, user)
- Added user management for super admin
- Default superadmin account created via .env variables
- Centered company information on PDF A4 receipts
- Improved thermal receipt readability with dynamic font sizes
- Enhanced WhatsApp sharing with wa.me links
- Made all pages fully responsive for mobile
- Migrated data storage to PostgreSQL database with SQLAlchemy ORM
- Added thermal receipt support for 48mm/57mm/58mm/80mm widths
