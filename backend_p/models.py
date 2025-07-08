# backend_p/models.py
from pydantic import BaseModel, EmailStr
from typing import Optional

class EventBooking(BaseModel):
    """Model for event booking requests"""
    eventName: str
    description: str
    date: str
    startTime: str
    endTime: str
    attendees: int
    organizer: str
    contactEmail: str

class CaptivePortalUser(BaseModel):
    """Model for captive portal user registration"""
    fullName: str
    email: str

class ContactForm(BaseModel):
    """Model for contact form submissions"""
    name: str
    email: EmailStr
    phone: str
    subject: str
    message: str 