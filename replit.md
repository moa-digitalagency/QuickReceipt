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
│   ├── receipt.py        # Receipt model
│   └── settings.py       # Settings model
├── routes/                # Flask route handlers
│   ├── __init__.py       # Route registration
│   ├── api.py            # API endpoints
│   ├── clients.py        # Client routes
│   ├── dashboard.py      # Dashboard routes
│   ├── receipts.py       # Receipt routes
│   └── settings.py       # Settings routes
├── scripts/               # Utility scripts
│   └── __init__.py
├── security/              # Security utilities
│   └── __init__.py       # Secret key generation
├── services/              # Business logic services
│   ├── __init__.py
│   ├── pdf.py            # PDF generation service
│   └── share.py          # Sharing service
├── static/uploads/        # Uploaded logos
├── templates/             # Jinja2 HTML templates
│   ├── base.html         # Base layout with navigation
│   ├── dashboard.html    # Dashboard with stats
│   ├── clients.html      # Client list
│   ├── client_form.html  # Add/Edit client form
│   ├── receipts.html     # Receipt list
│   ├── receipt_form.html # Create receipt form
│   ├── receipt_view.html # View receipt details
│   └── settings.html     # Company settings
├── utils/                 # Utility functions
│   ├── __init__.py
│   ├── files.py          # File handling utilities
│   └── i18n.py           # Internationalization helpers
└── data/                  # JSON data storage
    ├── clients.json
    ├── receipts.json
    └── settings.json
```

## Features
- Dashboard with quick receipt creation and recent receipts overview
- Client management (CRUD) with name, WhatsApp, and email
- Receipt creation with service description, amount, and payment method
- PDF generation for professional receipts
- Receipt history sorted by date
- Company settings with logo upload
- Multilingual support (French, English, Arabic) with RTL support
- Pre-filled WhatsApp and email sharing
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
- `/settings` - Company settings
- `/receipts/pdf/<id>` - Download receipt PDF
- `/set-locale/<locale>` - Change language (fr, en, ar)
- `/api/share/<id>` - Get share data for a receipt
