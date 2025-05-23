# backend_p/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


app = FastAPI()

app.mount("/team", StaticFiles(directory="public/team"), name="team")
app.mount("/menu", StaticFiles(directory="public/menu"), name="menu")
app.mount("/events", StaticFiles(directory="public/events"), name="events")

# Allow requests from your frontend (adjust the origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://parlamento-frontend.onrender.com", "https://*.onrender.com"],
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
                    "price": "35 Bs",
                    "image": "/menu/cafes_bebidas/chuflay_arandanos.jpg",
                    "tags": ["Coctelería"],
                    "historical": "",
                },
                {
                    "id": "b2",
                    "name": "DS 21060",
                    "description":
                    "Vermouth, vodka y singani, con almíbar y limón fresco, completada con agua tónica para un toque burbujeante y equilibrado.",
                    "price": "39 Bs",
                    "image": "/menu/cafes_bebidas/ds_21060.jpg",
                    "tags": ["Cocteleria", "De la Casa"],
                    "historical": "",
                },
                {
                    "id": "b3",
                    "name": "Illimani Cold Brew",
                    "description": "Slow-steeped for 24 hours, our cold brew is named after La Paz's iconic mountain peak.",
                    "price": "22 Bs",
                    "image": "/menu/menu_placeholder.png",
                    "tags": ["Cold"],
                    "historical": "Named after the mountain that watches over La Paz",
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
                    "name": "Tiwanaku Tea",
                    "description": "A blend of local herbs and flowers from the Altiplano region, served hot or cold.",
                    "price": "16 Bs",
                    "image": "/menu/menu_placeholder.png",
                    "tags": ["Hot/Cold"],
                    "historical": "Named after the ancient pre-Columbian archaeological site",
                },
                {
                    "id": "b6",
                    "name": "Sucre Smoothie",
                    "description": "A refreshing blend of Bolivian fruits including cherimoya and tumbo.",
                    "price": "25 Bs",
                    "image": "/menu/menu_placeholder.png",
                    "tags": ["Cold", "Vegan"],
                    "historical": "Named after Bolivia's constitutional capital",
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
                    "price": "59 Bs",
                    "image": "/menu/cocina_de_autor/domitila.jpg",
                    "tags": "[Auténtico]",
                    "historical": "Inspirado en la fuerza y el carácter de Domitila Barrios de Chungara, figura emblemáticas de la resistencia obrera y femenina en Bolivia.",
                },
                {
                    "id": "c2",
                    "name": "Incahuasi",
                    "description":
                    "Bife ancho con queso criollo gratinado, rúcula, cebolla y pimiento caramelizados, mayonesa de ají de padilla.",
                    "price": "59 Bs",
                    "image": "/menu/menu_placeholder.png",
                    "tags": "",
                    "historical": "Incahuasi, que en quechua significa 'la casa del Inca'",
                },
                {
                    "id": "c3",
                    "name": "Gran Poder",
                    "description": "Anticucho salteado, lechuga suiza, pimiento morrón, choclo y salsa de maní ahumada",
                    "price": "59 Bs",
                    "image": "/menu/cocina_de_autor/gran_poder.jpg",
                    "tags": "",
                    "historical": "Inspirado en la fiesta mayor de los Andes, una explosión de identidad, devoción y cultura popular que cada año transforma las calles de La Paz.",
                },
                {
                    "id": "c4",
                    "name": "Crispy Colonial",
                    "description": "Pollo frito bañado en salsa barbacoa, coleslaw, brotes y semillas de sésamo.",
                    "price": "59 Bs",
                    "image": "/menu/menu_placeholder.png",
                    "tags": "",
                    "historical": "Inspirado en la Colonia, una época de imposiciones, contrastes y resistencias en Bolivia.",
                },
                {
                    "id": "c5",
                    "name": "Neo Liberal",
                    "description": "Desayuno clásico con pan baguette, mantequilla y mermelada, huevos revueltos cubiertos con miel, bowl de yogurt con frutillas y granola. Incluye una bebida fria y caliente",
                    "price": "65 Bs",
                    "image": "/menu/cocina_de_autor/neo_liberal.png",
                    "tags": "",
                    "historical": "El neoliberalismo es una corriente de pensamiento económico y político que enfatiza la importancia del libre mercado y la minimización de la intervención estatal en la economía.",
                },
                {
                    "id": "c6",
                    "name": "Pachacuti",
                    "description": "Salsa de tomate casera con notas ahumadas, huevo pochado, chorizo chuquisaqueño, tocino y bocconcinos de queso criollo acompañado con tostadas.",
                    "price": "55 Bs",
                    "image": "/menu/menu_placeholder.png",
                    "tags": "",
                    "historical": "Noveno gobernante del Estado inca, y quien lo gobernó en su expansión desde un curacazgo regional hasta convertirse en un imperio.",
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
                    "image": "/menu/pasteleria/cake_choc.jpg",
                    "tags": ["Dulce"],
                    "historical": "",
                },
            ]
        }
    }

@app.get("/api/events")
def get_events():
    return [
        {
            "id": "e1",
            "title": "Bolivian Coffee Tasting Workshop",
            "date": "May 15, 2025",
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
            "date": "May 20, 2025",
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
            "date": "May 25, 2025",
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
            "date": "June 1-15, 2025",
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
            "date": "June 10, 2025",
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
            "date": "June 18, 2025",
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