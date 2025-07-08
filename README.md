# El Parlamento Backend

A modern, modular FastAPI backend for the El Parlamento restaurant/café management system. This backend provides APIs for menu management, event booking, user registration, and content management with Google Sheets integration.

## 🏗️ Architecture Overview

The backend follows a **clean, modular architecture** with clear separation of concerns:

```
backend_parlamento/
├── backend_p/
│   ├── main.py           # App initialization (31 lines)
│   ├── api_routes.py     # All API endpoints (163 lines)
│   ├── services.py       # Business logic layer (188 lines)
│   ├── config.py         # Configuration management (69 lines)
│   ├── models.py         # Pydantic data models (26 lines)
│   ├── utils.py          # Utility functions (463 lines)
│   └── main_backup.py    # Original code backup (845 lines)
├── public/               # Static files (images, assets)
├── requirements.txt      # Python dependencies
├── render.yaml          # Deployment configuration
└── .env                 # Environment variables
```

## 🎯 Key Features

- **Google Sheets Integration**: Dynamic menu and events management
- **Email System**: Contact forms and event booking notifications
- **Supabase Database**: User data storage
- **Image Proxy**: CORS-friendly Google Drive image serving
- **Modular Design**: Clean separation of concerns
- **Production Ready**: Deployed on Render with proper error handling

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Virtual environment (recommended)
- Google Sheets API credentials
- Supabase project
- Email service (SMTP) credentials

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd backend_parlamento
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv_bp
   source venv_bp/bin/activate  # On Windows: venv_bp\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the root directory:
   ```env
   # Email Configuration
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   MAIL_FROM=your-email@gmail.com
   MAIL_PORT=587
   MAIL_SERVER=smtp.gmail.com
   MAIL_STARTTLS=True
   MAIL_SSL_TLS=False
   
   # Supabase Configuration
   SUPABASE_URL=your-supabase-url
   SUPABASE_KEY=your-supabase-anon-key
   
   # Google Sheets Configuration
   GOOGLE_SHEET_ID=your-google-sheet-id
   GOOGLE_WORKSHEET_NAME=Events
   MENU_WORKSHEET_NAME=Menu
   BOOKING_SHEET_ID=your-booking-sheet-id
   BOOKING_WORKSHEET_NAME=EventBookings
   
   # Google Service Account (JSON format)
   GOOGLE_CREDENTIALS_JSON={"type": "service_account", ...}
   
   # CORS Configuration
   CORS_ORIGINS=["http://localhost:3000", "https://your-frontend-domain.com"]
   ```

5. **Run the application**
   ```bash
   # Development
   uvicorn backend_p.main:app --reload
   
   # Production
   uvicorn backend_p.main:app --host 0.0.0.0 --port 8000
   ```

## 📁 Code Structure

### `main.py` - Application Entry Point
- FastAPI app initialization
- Middleware configuration (CORS)
- Static file mounting
- Router inclusion

### `api_routes.py` - API Endpoints
All REST API endpoints using FastAPI's APIRouter:
- `GET /` - Health check
- `GET /health` - Detailed health status
- `GET /api/menu` - Menu data from Google Sheets
- `GET /api/events` - Events data from Google Sheets
- `POST /api/contact` - Contact form submission
- `POST /api/book-event-email` - Event booking
- `POST /api/store-user` - User registration
- `GET /api/image/{file_id}` - Google Drive image proxy

### `services.py` - Business Logic
Three main service classes:
- **`GoogleSheetsService`**: Menu/events data fetching and booking logging
- **`SupabaseService`**: User data storage and retrieval
- **`EmailService`**: Contact and booking email handling

### `config.py` - Configuration Management
Centralized configuration with environment variable validation:
- Email settings
- Database credentials
- Google Sheets configuration
- CORS settings

### `models.py` - Data Models
Pydantic models for request/response validation:
- `EventBooking`: Event booking data
- `CaptivePortalUser`: User registration data
- `ContactForm`: Contact form data

### `utils.py` - Utility Functions
Helper functions for:
- Google Drive link conversion
- Date normalization
- Menu data transformation
- Fallback data generation

## 🔧 Development Workflow

### Adding New Endpoints

1. **Define the endpoint** in `api_routes.py`:
   ```python
   @router.get("/api/new-endpoint")
   def new_endpoint():
       return service.method()
   ```

2. **Add business logic** in `services.py`:
   ```python
   def new_method(self):
       # Business logic here
       return result
   ```

3. **Create models** in `models.py` if needed:
   ```python
   class NewModel(BaseModel):
       field: str
   ```

### Testing

Run tests to ensure everything works:
```bash
# Test imports
python -c "from backend_p.main import app; print('✓ Main app imported')"

# Test services
python -c "from backend_p.services import google_sheets_service; print('✓ Services working')"

# Test specific endpoints
curl http://localhost:8000/health
```

### Environment Management

- **Development**: Use `.env` file with local settings
- **Production**: Set environment variables in deployment platform
- **Security**: Never commit credential files or .env to version control

## 🚀 Deployment

### Render.com Deployment

The application is configured for Render deployment:

1. **Build Command**: `pip install -r requirements.txt`
2. **Start Command**: `uvicorn backend_p.main:app --host 0.0.0.0 --port $PORT`
3. **Environment Variables**: Set all required env vars in Render dashboard

### Static Files

Static files are served from the `public/` directory:
- `/team` - Team member images
- `/menu` - Menu item images
- `/events` - Event images

## 🔐 Security Considerations

- **Credentials**: All sensitive data in environment variables
- **CORS**: Configured for specific origins only
- **File Validation**: Image proxy validates file IDs
- **Error Handling**: Proper error responses without exposing internals

## 📊 API Documentation

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Basic health check |
| GET | `/health` | Detailed health status |
| GET | `/api/menu` | Menu items from Google Sheets |
| GET | `/api/events` | Events from Google Sheets |
| GET | `/api/events/{id}` | Specific event details |
| POST | `/api/contact` | Submit contact form |
| POST | `/api/book-event-email` | Book event via email |
| POST | `/api/store-user` | Register captive portal user |
| GET | `/api/image/{file_id}` | Proxy Google Drive images |

### Response Format

All API responses follow consistent format:
```json
{
  "status": "success|error",
  "message": "Description",
  "data": {} // Optional data payload
}
```

## 🛠️ Troubleshooting

### Common Issues

1. **Google Sheets Access**: Ensure service account has proper permissions
2. **Email Delivery**: Check SMTP settings and app passwords
3. **CORS Errors**: Verify frontend domain in CORS_ORIGINS
4. **Database Connection**: Confirm Supabase URL and keys

### Logs

Check application logs for detailed error information:
```bash
# Development
uvicorn backend_p.main:app --reload --log-level debug

# Production
Check Render logs dashboard
```

## 📈 Performance

- **Caching**: Google Drive images cached for 1 hour
- **Background Tasks**: Email sending and logging don't block responses
- **Error Handling**: Graceful fallbacks for external service failures
- **Connection Pooling**: Efficient HTTP client usage

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-feature`
3. **Follow code structure**: Add endpoints to `api_routes.py`, business logic to `services.py`
4. **Test thoroughly**: Ensure all imports and endpoints work
5. **Submit pull request** with detailed description

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
- Check the troubleshooting section
- Review the modularization log for recent changes
- Contact the development team

---

**Note**: This backend was successfully modularized from a single 845-line file to a clean, maintainable architecture with proper separation of concerns. The modularization process is documented in `modularization_log.txt`.
