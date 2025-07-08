# backend_p/api_routes.py
from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
from datetime import datetime
from typing import Optional
import httpx
import re

# Import our models
from .models import EventBooking, CaptivePortalUser, ContactForm
# Import our services
from .services import google_sheets_service, supabase_service, email_service

# Create the main router
router = APIRouter()

@router.get("/")
def read_root():
    return {"message": "Backend is running!"}

@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "Backend is active",
        "timestamp": datetime.now().isoformat()
    }

@router.post("/api/book-event")
def book_event(booking: EventBooking):
    # Here you would store the booking in a database
    # For now, let's just return a success response
    return {
        "status": "success",
        "message": "Event booked successfully",
        "booking_id": "booking_" + datetime.now().strftime("%Y%m%d%H%M%S")
    }

@router.get("/api/available-slots")
def get_available_slots(date: Optional[str] = None):
    # In a real implementation, this would check your database for existing bookings
    # and return available time slots
    return {
        "available_slots": [
            {"date": date or "2024-07-01", "slots": ["09:00", "10:00", "11:00", "14:00", "15:00"]}
        ]
    }

@router.get("/team")
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

@router.get("/api/testimonials")
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

@router.get("/api/menu")
def get_menu():
    return google_sheets_service.get_menu_data()

@router.get("/api/events")
def get_events():
    return google_sheets_service.get_events_data()

@router.get("/api/events/{event_id}")
def get_event(event_id: str):
    events = get_events()  # reuse your existing function
    for event in events:
        if event["id"] == event_id:
            return event
    return {"detail": "Event not found"}, 404

@router.post("/api/store-user")
def store_user(user: CaptivePortalUser):
    return supabase_service.store_user(user)

@router.post("/api/contact")
async def contact(form: ContactForm):
    return await email_service.send_contact_email(form)

@router.post("/api/book-event-email")
async def book_event_email(data: dict, background_tasks: BackgroundTasks):
    # Send email through service
    result = await email_service.send_booking_email(data)
    
    # Log to Google Sheets in the background
    background_tasks.add_task(google_sheets_service.log_event_booking, data)
    
    return result

@router.get("/api/image/{file_id}")
async def get_drive_image(file_id: str):
    """Proxy endpoint to serve Google Drive images, bypassing CORS restrictions"""
    try:
        # Validate file_id format (basic security check)
        if not re.match(r'^[a-zA-Z0-9_-]+$', file_id):
            raise HTTPException(status_code=400, detail="Invalid file ID format")
        
        # Construct Google Drive direct download URL
        drive_url = f"https://drive.google.com/uc?export=view&id={file_id}"
        
        # Make request to Google Drive with proper headers
        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            response = await client.get(
                drive_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=404, detail="Image not found")
            
            # Get content type from response, default to image/jpeg if not specified
            content_type = response.headers.get("content-type", "image/jpeg")
            
            # Ensure it's an image content type
            if not content_type.startswith("image/"):
                content_type = "image/jpeg"
            
            # Return the image data as a streaming response
            return StreamingResponse(
                iter([response.content]),
                media_type=content_type,
                headers={
                    "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
                    "Access-Control-Allow-Origin": "*",
                }
            )
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Timeout fetching image")
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Error fetching image")
    except Exception as e:
        print(f"Error proxying image {file_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") 