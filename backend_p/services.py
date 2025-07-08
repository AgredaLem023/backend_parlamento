# backend_p/services.py
import gspread
from google.oauth2.service_account import Credentials
from fastapi_mail import FastMail, MessageSchema
from supabase import create_client, Client
from dateutil import parser
from typing import Dict, List, Any, Optional
from .config import Config
from .utils import (
    get_google_sheets_credentials,
    transform_menu_data,
    normalize_event_date,
    convert_google_drive_link,
    get_hardcoded_menu,
    get_hardcoded_events,
    log_event_booking_to_sheets
)
from .models import ContactForm, CaptivePortalUser

class GoogleSheetsService:
    """Service for handling Google Sheets operations"""
    
    def __init__(self):
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        self.sheet_id = Config.GOOGLE_SHEET_ID
        self.menu_worksheet_name = Config.MENU_WORKSHEET_NAME
        self.events_worksheet_name = Config.GOOGLE_WORKSHEET_NAME
        self.booking_sheet_id = Config.BOOKING_SHEET_ID
        self.booking_worksheet_name = Config.BOOKING_WORKSHEET_NAME
    
    def _get_credentials(self) -> Optional[Credentials]:
        """Get Google Sheets credentials"""
        try:
            credentials_info = get_google_sheets_credentials()
            if not credentials_info:
                return None
            return Credentials.from_service_account_info(credentials_info, scopes=self.scopes)
        except Exception as e:
            print(f"Error getting Google Sheets credentials: {e}")
            return None
    
    def _get_worksheet(self, sheet_id: str, worksheet_name: str):
        """Get a specific worksheet from Google Sheets"""
        creds = self._get_credentials()
        if not creds:
            raise Exception("Failed to get Google Sheets credentials")
        
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(sheet_id)
        return sh.worksheet(worksheet_name)
    
    def get_menu_data(self) -> List[Dict[str, Any]]:
        """Fetch menu data from Google Sheets with fallback to hardcoded data"""
        try:
            worksheet = self._get_worksheet(self.sheet_id, self.menu_worksheet_name)
            raw_menu_items = worksheet.get_all_records()
            menu = transform_menu_data(raw_menu_items)
            
            print(f"Successfully fetched {len(raw_menu_items)} menu items from Google Sheets")
            return menu
            
        except Exception as e:
            print(f"Error fetching menu from Google Sheets: {e}")
            print("Falling back to hardcoded menu...")
            return get_hardcoded_menu()
    
    def get_events_data(self) -> List[Dict[str, Any]]:
        """Fetch events data from Google Sheets with fallback to hardcoded data"""
        try:
            worksheet = self._get_worksheet(self.sheet_id, self.events_worksheet_name)
            raw_events = worksheet.get_all_records()
            
            # Normalize all event dates to ISO 8601 and ensure proper data types
            events = []
            for event in raw_events:
                event = event.copy()
                event["date"] = normalize_event_date(str(event["date"])) if event.get("date") else ""
                
                # Ensure capacity is an integer
                if event.get("capacity"):
                    try:
                        event["capacity"] = int(event["capacity"])
                    except (ValueError, TypeError):
                        event["capacity"] = 0
                
                # Convert Google Drive share links to direct image URLs
                if event.get("image") and "drive.google.com" in str(event["image"]):
                    event["image"] = convert_google_drive_link(str(event["image"]))
                
                events.append(event)
            
            print(f"Successfully fetched {len(events)} events from Google Sheets")
            return events
            
        except Exception as e:
            print(f"Error fetching events from Google Sheets: {e}")
            print("Falling back to hardcoded events...")
            return get_hardcoded_events()
    
    def log_event_booking(self, data: Dict[str, Any]) -> None:
        """Log event booking to Google Sheets"""
        try:
            log_event_booking_to_sheets(data)
        except Exception as e:
            print(f"Error logging event booking to Google Sheets: {e}")


class SupabaseService:
    """Service for handling Supabase database operations"""
    
    def __init__(self):
        self.client: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    def store_user(self, user: CaptivePortalUser) -> Dict[str, Any]:
        """Store captive portal user in Supabase"""
        data = {
            "full_name": user.fullName,
            "email": user.email
        }
        try:
            response = self.client.table("captive_portal_users").insert(data).execute()
            return {
                "status": "success", 
                "message": "User stored in Supabase", 
                "data": response.data
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": "Failed to store user", 
                "details": str(e)
            }


class EmailService:
    """Service for handling email operations"""
    
    def __init__(self):
        from fastapi_mail import ConnectionConfig
        self.conf = ConnectionConfig(**Config.get_mail_config())
        self.fastmail = FastMail(self.conf)
    
    async def send_contact_email(self, form: ContactForm) -> Dict[str, str]:
        """Send contact form email"""
        try:
            message = MessageSchema(
                subject=f"Nuevo mensaje de contacto: {form.subject}",
                recipients=["claudia@parlamento.com.bo"],
                body=f"""
                Nombre: {form.name}
                Email: {form.email}
                Teléfono: {form.phone}
                Asunto: {form.subject}
                Mensaje: {form.message}
                """,
                subtype="plain"
            )
            await self.fastmail.send_message(message)
            return {"status": "success", "message": "Email sent"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to send email: {str(e)}"}
    
    async def send_booking_email(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Send event booking email"""
        try:
            # Format the date for better readability
            formatted_date = data.get('date', '')
            if formatted_date:
                try:
                    # Parse the ISO date string and format it as MM/DD/YYYY
                    date_obj = parser.parse(formatted_date)
                    formatted_date = date_obj.strftime('%m/%d/%Y')
                except Exception:
                    # If parsing fails, keep the original date
                    formatted_date = data.get('date', '')
            
            # Compose the email body
            body = f"""
            Nueva solicitud de reserva de evento:

            Nombre del evento: {data.get('eventName')}
            Descripción: {data.get('description')}
            Fecha del evento: {formatted_date}
            Hora de inicio: {data.get('startTime')}
            Hora de finalización: {data.get('endTime')}
            Número de asistentes: {data.get('attendees')}
            Organizador: {data.get('organizer')}
            Correo de contacto: {data.get('contactEmail')}
            Número de teléfono: {data.get('phoneNumber')}
            """

            message = MessageSchema(
                subject="Nueva reserva de evento desde la web",
                recipients=["claudia@parlamento.com.bo"],
                body=body,
                subtype="plain"
            )
            await self.fastmail.send_message(message)
            return {"status": "success", "message": "Solicitud enviada por correo"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to send booking email: {str(e)}"}


# Service instances (singletons)
google_sheets_service = GoogleSheetsService()
supabase_service = SupabaseService()
email_service = EmailService() 