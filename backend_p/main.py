# backend_p/main.py
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from fastapi import FastAPI
import gspread
from google.oauth2.service_account import Credentials
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
import os
from supabase import create_client, Client
from dateutil import parser
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

app.mount("/team", StaticFiles(directory="public/team"), name="team")
app.mount("/menu", StaticFiles(directory="public/menu"), name="menu")
app.mount("/events", StaticFiles(directory="public/events"), name="events")

# Allow requests from your frontend (adjust the origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://parlamento-frontend.onrender.com", "https://*.onrender.com","https://www.parlamento.com.bo"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Event booking model
class EventBooking(BaseModel):
    eventName: str
    description: str
    date: str
    startTime: str
    endTime: str
    attendees: int
    organizer: str
    contactEmail: str

class CaptivePortalUser(BaseModel):
    fullName: str
    email: str

class ContactForm(BaseModel):
    name: str
    email: EmailStr
    phone: str
    subject: str
    message: str

conf = ConnectionConfig(
    MAIL_USERNAME=os.environ.get("MAIL_USERNAME"),
    MAIL_PASSWORD=os.environ.get("MAIL_PASSWORD"),
    MAIL_FROM=os.environ.get("MAIL_FROM"),
    MAIL_PORT=int(os.environ.get("MAIL_PORT", 465)),
    MAIL_SERVER=os.environ.get("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_STARTTLS=os.environ.get("MAIL_STARTTLS", "False") == "True",
    MAIL_SSL_TLS=os.environ.get("MAIL_SSL_TLS", "True") == "True",
    USE_CREDENTIALS=os.environ.get("USE_CREDENTIALS", "True") == "True"
)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/")
def read_root():
    return {"message": "Backend is running!"}

@app.post("/api/book-event")
def book_event(booking: EventBooking):
    # Here you would store the booking in a database
    # For now, let's just return a success response
    return {
        "status": "success",
        "message": "Event booked successfully",
        "booking_id": "booking_" + datetime.now().strftime("%Y%m%d%H%M%S")
    }

@app.get("/api/available-slots")
def get_available_slots(date: Optional[str] = None):
    # In a real implementation, this would check your database for existing bookings
    # and return available time slots
    return {
        "available_slots": [
            {"date": date or "2024-07-01", "slots": ["09:00", "10:00", "11:00", "14:00", "15:00"]}
        ]
    }

@app.get("/team")
def get_team():
    return [
        {
            "name": "Claudia Quispe",
            "role": "Manager",
            "image": "/team/member-1.png",
            "bio": "A culinary expert specializing in traditional Bolivian cuisine with a modern twist.",
        },
        {
            "name": "Mateo Flores",
            "role": "Co-Founder & Historian",
            "image": "/team/team-2.jpg",
            "bio": "A professor of Bolivian history who curates our cultural events and historical displays.",
        },
        {
            "name": "Camila Rojas",
            "role": "Head Barista",
            "image": "/team/team-3.jpg",
            "bio": "An award-winning coffee specialist with a passion for highlighting Bolivian coffee beans.",
        },
        {
            "name": "Diego Vargas",
            "role": "Events Coordinator",
            "image": "/team/team-4.jpg",
            "bio": "A community organizer who manages our diverse calendar of cultural and educational events.",
        },
    ]

@app.get("/api/testimonials")
def get_testimonials():
    return [
        {
            "id": 1,
            "name": "Maria Rodriguez",
            "role": "Local Artist",
            "content": "...",
            "rating": 5,
        },
        {
            "id": 2,
            "name": "Carlos Mendoza",
            "role": "University Professor",
            "content":
            "I bring my students here regularly for discussions. The combination of excellent coffee, thoughtful space design, and cultural significance makes it the perfect place for academic dialogue.",
            "rating": 5,
        },
        {
            "id": 3,
            "name": "Sofia Vargas",
            "role": "Food Blogger",
            "content":
            "The menu at El Parlamento beautifully represents Bolivia's culinary heritage with modern execution. Their 'Huayño Cappuccino' is a must-try for any coffee enthusiast visiting La Paz.",
            "rating": 5,
        },
        {
            "id": 4,
            "name": "Javier Morales",
            "role": "Tourist from Argentina",
            "content":
            "Stumbled upon this gem during my trip to Bolivia. The staff took time to explain the historical significance behind each dish and drink. A truly immersive cultural experience!",
            "rating": 4,
        },
    ]

@app.get("/api/menu")
def get_menu():
    return {
        "cafes y bebidas": {
            "title": "Cafes y Bebidas",
            "items": [
                {
                    "id": "b1",
                    "name": "Chuflay de arándanos",
                    "description":
                    " Versión frutal del clásico Chuflay, con singani, ginger ale y toque de arándanos, aportando dulzura y color vibrante.",
                    "price": "39 Bs",
                    "image": "/menu/cafes_bebidas/chuflay_arandanos.jpg",
                    "tags": ["Coctelería"],
                    "historical": "",
                },
                {
                    "id": "b2",
                    "name": "DS 21060",
                    "description":
                    "Vermouth, vodka y singani, con almíbar y limón fresco, completada con agua tónica para un toque burbujeante y equilibrado.",
                    "price": "42 Bs",
                    "image": "/menu/cafes_bebidas/ds_21060.jpg",
                    "tags": ["Cocteleria", "De la Casa"],
                    "historical": "",
                },
                {
                    "id": "b3",
                    "name": "Chuflay",
                    "description": "Tradicional boliviano con singani y ginger ale, servido con hielo y rodaja de limón.",
                    "price": "39 Bs",
                    "image": "/menu/menu_placeholder.png",
                    "tags": ["Coctelería", "Frio"],
                    "historical": "",
                },
                {
                    "id": "b4",
                    "name": "Chola Latte",
                    "description": "A rich latte with hints of chocolate and chuño (freeze-dried potato), a unique Bolivian twist.",
                    "price": "18 Bs",
                    "image": "/menu/menu_placeholder.png",
                    "tags": ["Hot"],
                    "historical": "Honors the iconic Cholitas, indigenous Bolivian women",
                },
                {
                    "id": "b5",
                    "name": "Singani sour",
                    "description": "Singani, zumo de limón, jarabe de azúcar, clara de huevo y angostura.",
                    "price": "39 Bs",
                    "image": "/menu/menu_placeholder.png",
                    "tags": ["Coctelería", "Frio"],
                    "historical": "",
                },
                {
                    "id": "b6",
                    "name": "Golpe de estado",
                    "description": "Shot de tequila con triple sec, acompañado de un gajo de limón encostrado en azúcar y ajíes nativos",
                    "price": "33 Bs",
                    "image": "/menu/menu_placeholder.png",
                    "tags": ["Coctelería", "Frio"],
                    "historical": "",
                },
            ]
        },
        "autor": {
            "title": "Cocina de Autor",
            "items": [
                {
                    "id": "c1",
                    "name": "Domitila",
                    "description":
                    "Cerdo bañado en velouté de ají amarillo con encurtidos de zanahoria, cebolla y tomate.",
                    "price": "66 Bs",
                    "image": "/menu/cocina_de_autor/domitila.jpg",
                    "tags": ["Auténtico", "Sandwich"],
                    "historical": "Inspirado en la fuerza y el carácter de Domitila Barrios de Chungara, figura emblemáticas de la resistencia obrera y femenina en Bolivia.",
                },
                {
                    "id": "c2",
                    "name": "Incahuasi",
                    "description":
                    "Bife ancho con queso criollo gratinado, rúcula, cebolla y pimiento caramelizados, mayonesa de ají de padilla.",
                    "price": "66 Bs",
                    "image": "/menu/menu_placeholder.png",
                    "tags": ["Sandwich"],
                    "historical": "Incahuasi, que en quechua significa 'la casa del Inca'",
                },
                {
                    "id": "c3",
                    "name": "Gran Poder",
                    "description": "Anticucho salteado, lechuga suiza, pimiento morrón, choclo y salsa de maní ahumada",
                    "price": "66 Bs",
                    "image": "/menu/cocina_de_autor/gran_poder.jpg",
                    "tags": ["Sandwich"],
                    "historical": "Inspirado en la fiesta mayor de los Andes, una explosión de identidad, devoción y cultura popular que cada año transforma las calles de La Paz.",
                },
                {
                    "id": "c4",
                    "name": "Crispy Colonial",
                    "description": "Pollo frito bañado en salsa barbacoa, coleslaw, brotes y semillas de sésamo.",
                    "price": "66 Bs",
                    "image": "/menu/cocina_de_autor/crispy_colonial.jpg",
                    "tags": ["Sandwich"],
                    "historical": "Inspirado en la Colonia, una época de imposiciones, contrastes y resistencias en Bolivia.",
                },
                {
                    "id": "c5",
                    "name": "Neo Liberal",
                    "description": "Desayuno clásico con pan baguette, mantequilla y mermelada, huevos revueltos cubiertos con miel, bowl de yogurt con frutillas y granola. Incluye una bebida fria y caliente",
                    "price": "70 Bs",
                    "image": "/menu/cocina_de_autor/neo_liberal.png",
                    "tags": ["Desayuno"],
                    "historical": "El neoliberalismo es una corriente de pensamiento económico y político que enfatiza la importancia del libre mercado y la minimización de la intervención estatal en la economía.",
                },
                {
                    "id": "c6",
                    "name": "Pachacuti",
                    "description": "Salsa de tomate casera con notas ahumadas, huevo pochado, chorizo chuquisaqueño, tocino y bocconcinos de queso criollo acompañado con tostadas.",
                    "price": "60 Bs",
                    "image": "/menu/cocina_de_autor/pachacuti.jpg",
                    "tags": ["Desayuno"],
                    "historical": "Noveno gobernante del Estado inca, y quien lo gobernó en su expansión desde un curacazgo regional hasta convertirse en un imperio.",
                },
                {
                    "id": "c7",
                    "name": "Compadre",
                    "description": "Pan campesino con queso crema de paprika, rodajas de palta, huevos benedictinos con salsa holandesa, bowl de yogurt con frutas y granola",
                    "price": "68 Bs",
                    "image": "/menu/cocina_de_autor/compadre.jpg",
                    "tags": ["Desayuno"],
                    "historical": "Persona con quien se ha establecido un lazo de compadrazgo, generalmente a través de un bautizo, primera comunión o, en algunos casos, una boda",
                },
                {
                    "id": "c8",
                    "name": "El Fundido Del Libertador",
                    "description": "Dos tostadas de pan campesino, tres tipos de queso, jamón ahumado y cubierto con huevo frito.",
                    "price": "55 Bs",
                    "image": "/menu/cocina_de_autor/el_fundido_del_lib.jpg",
                    "tags": ["Desayuno"],
                    "historical": "Estatua ecuestre de Simón Bolívar, una escultura de bronce fundido ubicada en la Plaza Bolívar de Caracas.",
                },
                {
                    "id": "c9",
                    "name": "Reforma Agraria",
                    "description": "Mix de quinuas, porotos, garbanzos, mango, cebolla, pimiento morrón, palta, cilantro y bañado en un alioli de ajíes nativos.",
                    "price": "66 Bs",
                    "image": "/menu/cocina_de_autor/reforma_agraria.webp",
                    "tags": ["Rebowlucion", "Auténtico"],
                    "historical": "Inspirado en el histórico Decreto de Reforma Agraria de 1953, que transformó el acceso a la tierra en Bolivia, rinde homenaje a las raíces campesinas y diversidad de ingredientes que nacen de nuestra tierra.",
                },
                {
                    "id": "c10",
                    "name": "Revolución",
                    "description": "Bife angosto, base de lechuga crespa, rúcula, tomates frescos, cebolla, requesón, pepino, frutillas con aceto balsámico.",
                    "price": "66 Bs",
                    "image": "/menu/cocina_de_autor/revolucion.webp",
                    "tags": ["Rebowlucion"],
                    "historical": "Movimiento social y político que marcó un cambio fundamental en la historia de Bolivia",
                },
                {
                    "id": "c11",
                    "name": "Urus",
                    "description": "Trucha encostrada en quinua, una base de rúcula y espinaca morada, pepino, palta, semillas de girasol, requesón y alioli de cilantro con crujientes de camote.",
                    "price": "73 Bs",
                    "image": "/menu/cocina_de_autor/urus.webp",
                    "tags": ["Rebowlucion"],
                    "historical": "Pueblo indígena que se distribuye en la meseta del Collao en territorios de Bolivia",
                },
                {
                    "id": "c12",
                    "name": "Obrera",
                    "description": "Mix de lechugas, tomates frescos, requesón, pollo frito, tocino, piña asada y aderezo de miel y mostaza.",
                    "price": "66 Bs",
                    "image": "/menu/menu_placeholder.png",
                    "tags": ["Rebowlucion"],
                    "historical": "",
                },
            ]
        },
        "pasteleria": {
            "title": "Pastelería",
            "items": [
                {
                    "id": "d1",
                    "name": "Torta de chocolate",
                    "description": "Húmeda rellena de dulce de leche con cobertura de ganache de chocolate semiamargo",
                    "price": "25 Bs",
                    "image": "/menu/pasteleria/cake_choc.webp",
                    "tags": ["Dulce"],
                    "historical": "",
                },
            ]
        }
    }

# --- Google Sheets Events Implementation ---
def normalize_event_date(date_str):
    try:
        # Parse the date string (e.g., "2024-07-01" or "2024-07-01T00:00:00")
        dt = parser.parse(date_str)
        # Return as ISO 8601 string (e.g., "2024-07-01T00:00:00")
        return dt.isoformat()
    except Exception:
        # If parsing fails, return the original string (or handle as needed)
        return date_str

def convert_google_drive_link(drive_url):
    """Convert Google Drive share link to direct image URL"""
    try:
        # Extract file ID from various Google Drive URL formats
        if "/file/d/" in drive_url:
            file_id = drive_url.split("/file/d/")[1].split("/")[0]
        elif "id=" in drive_url:
            file_id = drive_url.split("id=")[1].split("&")[0]
        else:
            return drive_url  # If we can't parse it, return original
        
        # Return direct image URL
        return f"https://drive.google.com/uc?export=view&id={file_id}"
    except Exception:
        return drive_url  # If conversion fails, return original

def get_google_sheets_credentials():
    """Create credentials from environment variables"""
    try:
        # First, try to get credentials from a single JSON environment variable
        google_credentials_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
        if google_credentials_json:
            try:
                credentials_info = json.loads(google_credentials_json)
                print("Successfully loaded Google Sheets credentials from JSON environment variable")
                return credentials_info
            except json.JSONDecodeError as e:
                print(f"Error parsing GOOGLE_CREDENTIALS_JSON: {e}")
                print("Falling back to individual environment variables...")
        
        # Fallback to individual environment variables (backwards compatibility)
        credentials_info = {
            "type": os.environ.get("GOOGLE_ACCOUNT_TYPE", "service_account"),
            "project_id": os.environ.get("GOOGLE_PROJECT_ID"),
            "private_key_id": os.environ.get("GOOGLE_PRIVATE_KEY_ID"),
            "private_key": os.environ.get("GOOGLE_PRIVATE_KEY").replace('\\n', '\n') if os.environ.get("GOOGLE_PRIVATE_KEY") else None,
            "client_email": os.environ.get("GOOGLE_CLIENT_EMAIL"),
            "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
            "auth_uri": os.environ.get("GOOGLE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"),
            "token_uri": os.environ.get("GOOGLE_TOKEN_URI", "https://oauth2.googleapis.com/token"),
            "auth_provider_x509_cert_url": os.environ.get("GOOGLE_AUTH_PROVIDER_X509_CERT_URL", "https://www.googleapis.com/oauth2/v1/certs"),
            "client_x509_cert_url": os.environ.get("GOOGLE_CLIENT_X509_CERT_URL"),
            "universe_domain": os.environ.get("GOOGLE_UNIVERSE_DOMAIN", "googleapis.com")
        }
        
        # Check if all required fields are present
        required_fields = ["project_id", "private_key", "client_email"]
        for field in required_fields:
            if not credentials_info.get(field):
                raise ValueError(f"Missing required Google Sheets credential: {field}")
        
        return credentials_info
    except Exception as e:
        print(f"Error creating Google Sheets credentials: {e}")
        return None

@app.get("/api/events")
def get_events():
    # Try to get events from Google Sheets, fallback to hardcoded if it fails
    try:
        # Google Sheets setup
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        SHEET_ID = os.environ.get("GOOGLE_SHEET_ID")
        WORKSHEET_NAME = os.environ.get("GOOGLE_WORKSHEET_NAME", "events_data")
        
        # Get credentials from environment variables
        credentials_info = get_google_sheets_credentials()
        if not credentials_info:
            raise Exception("Failed to get Google Sheets credentials")
        
        # Create credentials from the info dict
        creds = Credentials.from_service_account_info(credentials_info, scopes=SCOPES)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(SHEET_ID)
        worksheet = sh.worksheet(WORKSHEET_NAME)
        
        # Fetch all records as a list of dicts
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
        print(f"Error fetching from Google Sheets: {e}")
        print("Falling back to hardcoded events...")
        # Return hardcoded events as fallback
        return get_hardcoded_events()

def get_hardcoded_events():
    """Fallback hardcoded events (your current implementation)"""

def get_hardcoded_events():
    """Fallback hardcoded events (your current implementation)"""
    return [
        {
            "id": "e1",
            "title": "Bolivian Coffee Tasting Workshop",
            "date": "2025-05-15T00:00:00",
            "time": "4:00 PM - 6:00 PM",
            "location": "Main Hall",
            "description": "Learn to make Bolivia's famous salteñas from scratch with our head chef. Ingredients and recipes provided.",
            "image": "/events/event-1.jpg",
            "category": "workshop",
            "capacity": 20,
        },
        {
            "id": "e2",
            "title": "Andean Music Performance",
            "date": "2025-05-20T00:00:00",
            "time": "7:00 PM - 9:00 PM",
            "location": "Outdoor Patio",
            "description": "Experience the rich sounds of traditional Andean music with a live performance featuring panpipes, charango, and other indigenous instruments.",
            "image": "/events/event-2.jpg",
            "category": "performance",
            "capacity": 50,
        },
        {
            "id": "e3",
            "title": "Bolivian History Book Club",
            "date": "2025-05-25T00:00:00",
            "time": "6:00 PM - 8:00 PM",
            "location": "Library Corner",
            "description": "This month we're discussing 'The Bolivian Revolution: A Contemporary History' by James Dunkerley. New members welcome!",
            "image": "/events/event-3.jpg",
            "category": "meeting",
            "capacity": 15,
        },
        {
            "id": "e4",
            "title": "Traditional Weaving Exhibition",
            "date": "2025-06-01T00:00:00",
            "time": "10:00 AM - 8:00 PM",
            "location": "Gallery Space",
            "description": "A two-week exhibition showcasing the intricate textile traditions of Bolivia's indigenous communities, featuring works from artisans across the country.",
            "image": "/events/event-4.jpg",
            "category": "exhibition",
            "capacity": 100,
        },
        {
            "id": "e5",
            "title": "Bolivian Cooking Class: Salteñas",
            "date": "2025-06-10T00:00:00",
            "time": "2:00 PM - 5:00 PM",
            "location": "Kitchen",
            "description": "Learn to make Bolivia's famous salteñas from scratch with our head chef. Ingredients and recipes provided.",
            "image": "/events/event-5.jpg",
            "category": "workshop",
            "capacity": 12,
        },
        {
            "id": "e6",
            "title": "Political Discussion: Bolivia's Future",
            "date": "2025-06-18T00:00:00",
            "time": "6:30 PM - 8:30 PM",
            "location": "Main Hall",
            "description": "A moderated panel discussion with political scientists and community leaders about Bolivia's current challenges and future prospects.",
            "image": "/events/event-6.jpg",
            "category": "meeting",
            "capacity": 40,
        },
    ]

@app.get("/api/events/{event_id}")
def get_event(event_id: str):
    events = get_events()  # reuse your existing function
    for event in events:
        if event["id"] == event_id:
            return event
    return {"detail": "Event not found"}, 404

@app.post("/api/store-user")
def store_user(user: CaptivePortalUser):
    data = {
        "full_name": user.fullName,
        "email": user.email
    }
    try:
        response = supabase.table("captive_portal_users").insert(data).execute()
        return {"status": "success", "message": "User stored in Supabase", "data": response.data}
    except Exception as e:
        return {"status": "error", "message": "Failed to store user", "details": str(e)}

@app.post("/api/contact")
async def contact(form: ContactForm):
    message = MessageSchema(
        subject=f"Nuevo mensaje de contacto: {form.subject}",
        recipients=["claudia@parlamento.com.bo"],  # Your email
        body=f"""
        Nombre: {form.name}
        Email: {form.email}
        Teléfono: {form.phone}
        Asunto: {form.subject}
        Mensaje: {form.message}
        """,
        subtype="plain"
    )
    fm = FastMail(conf)
    await fm.send_message(message)
    return {"status": "success", "message": "Email sent"}

@app.post("/api/book-event-email")
async def book_event_email(data: dict, background_tasks: BackgroundTasks):
    # Compose the email body
    body = f"""
    Nueva solicitud de reserva de evento:

    Nombre del evento: {data.get('eventName')}
    Descripción: {data.get('description')}
    Fecha: {data.get('date')}
    Hora de inicio: {data.get('startTime')}
    Hora de finalización: {data.get('endTime')}
    Número de asistentes: {data.get('attendees')}
    Organizador: {data.get('organizer')}
    Correo de contacto: {data.get('contactEmail')}
    """

    message = MessageSchema(
        subject="Nueva reserva de evento desde la web",
        recipients=["claudia@parlamento.com.bo"],  # Change to manager's email
        body=body,
        subtype="plain"
    )
    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message)
    return {"status": "success", "message": "Solicitud enviada por correo"}