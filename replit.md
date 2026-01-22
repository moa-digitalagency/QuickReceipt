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
├── app.py                 # Main Flask application
├── translations.json      # i18n translations (FR, EN, AR)
├── templates/            # Jinja2 HTML templates
│   ├── base.html         # Base layout with navigation
│   ├── dashboard.html    # Dashboard with stats and quick actions
│   ├── clients.html      # Client list
│   ├── client_form.html  # Add/Edit client form
│   ├── receipts.html     # Receipt list
│   ├── receipt_form.html # Create receipt form
│   ├── receipt_view.html # View receipt details with share options
│   └── settings.html     # Company settings
├── static/uploads/       # Uploaded logos
└── data/                 # JSON data storage
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
