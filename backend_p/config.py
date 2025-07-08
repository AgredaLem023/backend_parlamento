# backend_p/config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for centralizing all environment variables"""
    
    # Email Configuration
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_FROM = os.environ.get("MAIL_FROM")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 465))
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_STARTTLS = os.environ.get("MAIL_STARTTLS", "False") == "True"
    MAIL_SSL_TLS = os.environ.get("MAIL_SSL_TLS", "True") == "True"
    USE_CREDENTIALS = os.environ.get("USE_CREDENTIALS", "True") == "True"
    
    # Supabase Configuration
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
    
    # Google Sheets Configuration
    GOOGLE_CREDENTIALS_JSON = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    GOOGLE_SHEET_ID = os.environ.get("GOOGLE_SHEET_ID")
    GOOGLE_WORKSHEET_NAME = os.environ.get("GOOGLE_WORKSHEET_NAME", "events_data")
    MENU_WORKSHEET_NAME = os.environ.get("MENU_WORKSHEET_NAME", "menu_data")
    
    # Event Booking Configuration
    BOOKING_SHEET_ID = os.environ.get("BOOKING_SHEET_ID")
    BOOKING_WORKSHEET_NAME = os.environ.get("BOOKING_WORKSHEET_NAME", "solicitudes_de_reserva_eventos")
    
    # CORS Configuration
    CORS_ORIGINS = [
        "http://localhost:3000",
        "https://parlamento-frontend.onrender.com",
        "https://*.onrender.com",
        "https://www.parlamento.com.bo",
        "https://11dias.visitbolivia.travel"
    ]
    
    @classmethod
    def validate_config(cls):
        """Validate that all required configuration is present"""
        required_vars = [
            "MAIL_USERNAME", "MAIL_PASSWORD", "MAIL_FROM",
            "SUPABASE_URL", "SUPABASE_KEY",
            "GOOGLE_CREDENTIALS_JSON", "GOOGLE_SHEET_ID"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True
    
    @classmethod
    def get_mail_config(cls):
        """Get email configuration as a dictionary"""
        return {
            "MAIL_USERNAME": cls.MAIL_USERNAME,
            "MAIL_PASSWORD": cls.MAIL_PASSWORD,
            "MAIL_FROM": cls.MAIL_FROM,
            "MAIL_PORT": cls.MAIL_PORT,
            "MAIL_SERVER": cls.MAIL_SERVER,
            "MAIL_STARTTLS": cls.MAIL_STARTTLS,
            "MAIL_SSL_TLS": cls.MAIL_SSL_TLS,
            "USE_CREDENTIALS": cls.USE_CREDENTIALS
        } 