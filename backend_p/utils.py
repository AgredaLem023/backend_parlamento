# backend_p/utils.py
import os
import json
import random
from datetime import datetime
from dateutil import parser
import gspread
from google.oauth2.service_account import Credentials

from .config import Config

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
        google_credentials_json = Config.GOOGLE_CREDENTIALS_JSON
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

def transform_menu_data(raw_items):
    """Transform flat Google Sheets data into nested menu structure"""
    try:
        # Initialize menu structure
        menu = {
            "cafes y bebidas": {
                "title": "Cafes y Bebidas",
                "items": []
            },
            "autor": {
                "title": "Cocina de Autor", 
                "items": []
            },
            "pasteleria": {
                "title": "Pastelería",
                "items": []
            }
        }
        
        # Process each item
        for item in raw_items:
            # Skip empty rows
            if not item.get("category_key") or not item.get("item_name"):
                continue
            
            # Get category key
            category_key = item.get("category_key", "").lower().strip()
            
            # Convert tags from comma-separated string to array
            tags_str = item.get("item_tags", "")
            tags = [tag.strip() for tag in tags_str.split(",") if tag.strip()] if tags_str else []
            
            # Convert Google Drive share links to direct image URLs if needed
            image_url = item.get("item_image", "")
            if image_url and "drive.google.com" in image_url:
                image_url = convert_google_drive_link(image_url)
            
            # Create menu item
            menu_item = {
                "id": item.get("item_id", ""),
                "name": item.get("item_name", ""),
                "description": item.get("item_description", ""),
                "price": item.get("item_price", ""),
                "image": image_url,
                "tags": tags,
                "historical": item.get("item_historical", "")
            }
            
            # Add to appropriate category
            if category_key in menu:
                menu[category_key]["items"].append(menu_item)
            else:
                print(f"Warning: Unknown category '{category_key}' for item '{item.get('item_name')}'")
        
        return menu
        
    except Exception as e:
        print(f"Error transforming menu data: {e}")
        raise

def normalize_event_date(date_str):
    """Normalize event date format"""
    try:
        # Parse the date string (e.g., "2024-07-01" or "2024-07-01T00:00:00")
        dt = parser.parse(date_str)
        # Return as ISO 8601 string (e.g., "2024-07-01T00:00:00")
        return dt.isoformat()
    except Exception:
        # If parsing fails, return the original string (or handle as needed)
        return date_str

def log_event_booking_to_sheets(booking_data):
    """Log event booking request to Google Sheets"""
    try:
        if not Config.BOOKING_SHEET_ID:
            print("BOOKING_SHEET_ID not configured, skipping Google Sheets logging")
            return False
        
        # Get credentials from environment variables
        credentials_info = get_google_sheets_credentials()
        if not credentials_info:
            print("Failed to get Google Sheets credentials for booking logging")
            return False
        
        # Create credentials and authorize
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        creds = Credentials.from_service_account_info(credentials_info, scopes=SCOPES)
        gc = gspread.authorize(creds)
        
        # Open the spreadsheet and worksheet
        sh = gc.open_by_key(Config.BOOKING_SHEET_ID)
        worksheet = sh.worksheet(Config.BOOKING_WORKSHEET_NAME)
        
        # Format the date for better readability
        formatted_date = booking_data.get('date', '')
        if formatted_date:
            try:
                date_obj = parser.parse(formatted_date)
                formatted_date = date_obj.strftime('%m/%d/%Y')
            except Exception:
                formatted_date = booking_data.get('date', '')
        
        # Create unique ID (timestamp + random component)
        unique_id = f"EVT_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(100, 999)}"
        
        # Prepare row data according to table structure
        row_data = [
            unique_id,  # A: ID
            datetime.now().strftime('%m/%d/%Y %H:%M:%S'),  # B: Fecha de Solicitud
            booking_data.get('eventName', ''),  # C: Nombre del Evento
            booking_data.get('description', ''),  # D: Descripción
            formatted_date,  # E: Fecha del Evento
            booking_data.get('startTime', ''),  # F: Hora de Inicio
            booking_data.get('endTime', ''),  # G: Hora de Fin
            booking_data.get('attendees', ''),  # H: Número de Asistentes
            booking_data.get('organizer', ''),  # I: Organizador
            booking_data.get('contactEmail', ''),  # J: Correo de Contacto
            booking_data.get('phoneNumber', ''),  # K: Número de Teléfono
            'Pendiente'  # L: Estado
        ]
        
        # Append the row to the worksheet
        worksheet.append_row(row_data)
        
        print(f"Successfully logged booking to Google Sheets with ID: {unique_id}")
        return True
        
    except Exception as e:
        print(f"Error logging booking to Google Sheets: {e}")
        return False

def get_hardcoded_menu():
    """Fallback hardcoded menu (original implementation)"""
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

def get_hardcoded_events():
    """Fallback hardcoded events (original implementation)"""
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