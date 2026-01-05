# Asset Manager - Secure Asset Management Application

A minimal, secure, fully functional asset management application built with Django and PostgreSQL, featuring persistent login sessions and a Shadcn-inspired UI.

## Features

- **Authentication**: Secure signup, login, logout with persistent sessions (30 days)
- **Dashboard**: Overview of total portfolio value with interactive charts
- **Asset Categories**: Mutual Funds, Stocks, Lands, Flats, Fixed Deposit, Medical Insurance, Life Insurance, Gold
- **Document Management**: Multiple file uploads per asset with validation
- **Activity Logging**: Track all asset changes for auditing
- **Responsive Design**: Shadcn-inspired minimal UI

## Tech Stack

- **Backend**: Django 4.2+
- **Database**: PostgreSQL
- **Frontend**: Shadcn-inspired CSS, Chart.js
- **Security**: CSRF protection, session security, file validation

## Quick Start

### 1. Prerequisites

- Python 3.10+
- PostgreSQL 14+
- pip

### 2. Clone and Setup

```bash
cd fin3

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Configuration

1. Create a PostgreSQL database:

```sql
CREATE DATABASE assetmanager;
CREATE USER assetuser WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE assetmanager TO assetuser;
```

2. Create `.env` file from example:

```bash
copy .env.example .env
```

3. Edit `.env` with your database credentials:

```env
DB_NAME=assetmanager
DB_USER=assetuser
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=your-secure-secret-key-here
DEBUG=True
```

### 4. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 6. Run Development Server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000

## Project Structure

```
fin3/
├── assetmanager/           # Django project settings
│   ├── settings.py         # Main configuration
│   ├── urls.py             # Root URL configuration
│   └── wsgi.py
├── assets/                 # Main application
│   ├── models.py           # Asset, AssetDocument, ActivityLog
│   ├── views.py            # Dashboard, CRUD views
│   ├── forms.py            # ModelForms with validation
│   ├── urls.py             # App URL patterns
│   └── admin.py            # Admin configuration
├── templates/              # HTML templates
│   ├── base.html           # Base template
│   ├── dashboard.html      # Dashboard
│   ├── activity_log.html   # Activity log
│   ├── registration/       # Auth templates
│   └── assets/             # Asset CRUD templates
├── static/
│   └── css/
│       └── styles.css      # Shadcn-inspired styles
├── media/                  # Uploaded files (created automatically)
├── manage.py
├── requirements.txt
└── .env.example
```

## Key Configuration

### Persistent Sessions (settings.py)

```python
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30  # 30 days
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True
```

### File Upload Limits

- Max file size: 10MB
- Allowed types: PDF, JPG, PNG, GIF, DOC, DOCX, XLS, XLSX

### Security Features

- CSRF protection enabled
- Ownership checks on all asset operations
- File type and size validation
- Session security settings for production

## Models

### Asset
- name, category, value, description
- start_date, end_date
- latitude, longitude (for lands)
- policy_number, institution
- owner (ForeignKey to User)

### AssetDocument
- file (with validation)
- name
- asset (ForeignKey to Asset)

### ActivityLog
- user, action, asset_name
- details, ip_address, timestamp

## API Endpoints

| URL | View | Description |
|-----|------|-------------|
| `/` | Dashboard | Main dashboard |
| `/login/` | Login | User login |
| `/logout/` | Logout | User logout |
| `/signup/` | Signup | User registration |
| `/assets/` | AssetList | List all assets |
| `/assets/create/` | AssetCreate | Create new asset |
| `/assets/<pk>/` | AssetDetail | View asset details |
| `/assets/<pk>/edit/` | AssetUpdate | Edit asset |
| `/assets/<pk>/delete/` | AssetDelete | Delete asset |
| `/activity/` | ActivityLog | View activity log |
| `/api/chart-data/` | ChartDataAPI | Chart data endpoint |

## Production Deployment

1. Set environment variables:
```env
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com
```

2. Collect static files:
```bash
python manage.py collectstatic
```

3. Use a production server (Gunicorn, uWSGI)

4. Enable HTTPS (required for secure cookies)

## License

MIT License
