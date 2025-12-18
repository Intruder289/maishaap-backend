# Maisha Backend Setup Instructions

## Quick Setup

### 1. Clone/Download the project
```bash
cd your-project-directory
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies

**Option A - All dependencies (recommended):**
```bash
pip install -r requirements.txt
```

**Option B - Minimal dependencies only:**
```bash
pip install -r requirements-minimal.txt
```

### 5. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Admin User (for approving mobile users)
```bash
python manage.py createsuperuser
```

### 7. Run Server
```bash
python manage.py runserver
```

### 8. Test API

**Swagger Documentation:**
- Open: http://127.0.0.1:8000/swagger/
- Alternative: http://127.0.0.1:8000/redoc/

**API Root:**
- Open: http://127.0.0.1:8000/api/v1/

## Project Structure

```
Maisha_backend/
├── manage.py
├── requirements.txt
├── requirements-minimal.txt
├── accounts/
│   ├── models.py           # User, Profile, Role models
│   ├── serializers.py      # API serializers
│   ├── api_views.py        # API endpoints
│   ├── api_urls.py         # API URL routing
│   └── templates/          # Web templates
├── Maisha_backend/
│   ├── settings.py         # Django configuration
│   └── urls.py            # Main URL routing
└── API_DOCUMENTATION.md    # Detailed API docs
```

## Key Features

✅ Role-based authentication (Tenant/Owner)
✅ Admin approval workflow
✅ JWT token authentication
✅ Swagger API documentation
✅ Firebase integration
✅ CORS support for Flutter
✅ User profile management
✅ Image upload support

## Environment Setup

1. **Python Version:** 3.13+ recommended
2. **Database:** SQLite (default) or PostgreSQL
3. **Firebase:** Configure in settings.py
4. **CORS:** Configured for localhost (update for production)

## Testing

1. **Signup:** POST /api/v1/auth/signup/
2. **Login:** POST /api/v1/auth/login/ (after admin approval)
3. **Admin:** Approve users via web interface or API
4. **Documentation:** View all endpoints in Swagger

## Production Deployment

For production, uncomment and install additional packages:
```bash
pip install python-decouple gunicorn whitenoise
```

Update settings for production environment variables and security.