# QuickReceipt

## Overview
QuickReceipt is a web application for managing receipts, designed for freelancers and small businesses. It provides an intuitive interface for creating, managing, and sharing professional receipts.

## Tech Stack
- **Backend**: Python Flask
- **Frontend**: HTML, JavaScript, Tailwind CSS (via CDN)
- **PDF Generation**: ReportLab
- **Image Processing**: Pillow
- **Data Storage**: JSON files (in `data/` directory)
- **Internationalization**: Custom i18n solution with French, English, and Arabic support

## Project Structure
```
├── app.py                 # Main Flask application entry point
├── docs/                  # Documentation
│   └── README.md
├── lang/                  # Language translations
│   └── translations.json  # i18n translations (FR, EN, AR)
├── models/                # Data models
│   ├── __init__.py
│   ├── base.py           # Base data loading/saving functions
│   ├── client.py         # Client model
│   ├── company.py        # Company model (multi-company support)
│   ├── receipt.py        # Receipt model
│   └── settings.py       # Settings model
├── routes/                # Flask route handlers
│   ├── __init__.py       # Route registration
│   ├── api.py            # API endpoints
│   ├── clients.py        # Client routes
│   ├── dashboard.py      # Dashboard routes
│   ├── receipts.py       # Receipt routes
│   └── settings.py       # Settings routes (company management)
├── scripts/               # Utility scripts
│   └── __init__.py
├── security/              # Security utilities
│   └── __init__.py       # Secret key generation
├── services/              # Business logic services
│   ├── __init__.py
│   ├── pdf.py            # PDF A4 generation service
│   ├── thermal.py        # Thermal receipt image generation
│   └── share.py          # WhatsApp/Email sharing service
├── static/
│   ├── favicon.svg       # Application favicon
│   └── uploads/          # Uploaded logos
├── templates/             # Jinja2 HTML templates
│   ├── base.html         # Base layout with navigation
│   ├── dashboard.html    # Dashboard with stats
│   ├── clients.html      # Client list
│   ├── client_form.html  # Add/Edit client form
│   ├── company_form.html # Add/Edit company form
│   ├── receipts.html     # Receipt list
│   ├── receipt_form.html # Create receipt form (with company/client selection)
│   ├── receipt_saved.html # Post-save popup with download options
│   ├── receipt_view.html # View receipt details
│   └── settings.html     # Company management + thermal settings
├── utils/                 # Utility functions
│   ├── __init__.py
│   ├── files.py          # File handling utilities
│   └── i18n.py           # Internationalization helpers
└── data/                  # JSON data storage
    ├── clients.json
    ├── companies.json    # Multi-company data
    ├── receipts.json
    └── settings.json
```

## Features
- Dashboard with quick receipt creation and recent receipts overview
- Client management (CRUD) with name, WhatsApp, and email
- **Multi-company support**: Configure multiple companies in settings, select one per receipt
- Receipt creation with inline client/company quick-add
- PDF A4 generation for professional receipts
- Thermal receipt image generation (58mm/80mm configurable)
- Receipt history sorted by date
- **Optional ICE/SIRET**: Only displayed in receipts when provided
- **WhatsApp sharing to client's number**: Uses client's WhatsApp from their data
- Multilingual support (French, English, Arabic) with RTL support
- Pre-filled WhatsApp and email sharing with company details
- Fully responsive design

## Running the Application
```bash
python app.py
```
The application runs on port 5000.

## Key Routes
- `/` - Dashboard
- `/clients` - Client management
- `/receipts` - Receipt management
- `/receipts/add` - Create receipt with company/client selection
- `/receipts/saved/<id>` - Post-save popup with download options
- `/settings` - Company management + thermal paper settings
- `/settings/company/add` - Add new company
- `/settings/company/edit/<id>` - Edit company
- `/receipts/pdf/<id>` - Download receipt PDF A4
- `/receipts/thermal/<id>` - Download thermal receipt image
- `/set-locale/<locale>` - Change language (fr, en, ar)
- `/api/share/<id>` - Get share data for WhatsApp/Email

## Recent Changes
- Added multi-company support with CRUD operations
- Added thermal receipt image generation (58mm/80mm)
- Added post-save popup with download/share options
- Added inline client and company creation in receipt form
- Made ICE/SIRET optional, displayed only when provided
- WhatsApp sharing now uses client's phone number
- Added favicon
