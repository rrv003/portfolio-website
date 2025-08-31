from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'portfolio')]

# Create the main app
app = FastAPI(title="Portfolio API", version="1.0.0")
api_router = APIRouter(prefix="/api")

# Models
class ContactMessage(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str

class ContactMessageResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: EmailStr
    subject: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="new")

# Portfolio data
PORTFOLIO_DATA = {
    "personalInfo": {
        "name": "Rahul Raj Verma",
        "title": "Senior Software Developer & API Management Specialist",
        "email": "rahul.verma@email.com",
        "phone": "+91-9876543210",
        "location": "Bangalore, India",
        "linkedIn": "https://linkedin.com/in/rahulrajverma",
        "github": "https://github.com/rahulverma",
        "resumeUrl": "https://customer-assets.emergentagent.com/job_20000752-4c4a-4ae7-a75b-95596df62169/artifacts/cnp11hvu_Rahul%20Raj%20Verma%205%2B%20Years%20Experience.pdf",
        "profileImage": "https://customer-assets.emergentagent.com/job_career-profile-127/artifacts/vd438o7b_Screenshot%202025-08-31%20154740.png",
        "bio": "Experienced Software Developer with 5+ years of expertise in automation testing and API management. Specialized in Kong and APIGEE platforms."
    },
    "skills": {
        "technical": [
            {"name": "API Management", "level": 95, "category": "Primary"},
            {"name": "Kong Gateway", "level": 90, "category": "Primary"},
            {"name": "APIGEE", "level": 88, "category": "Primary"},
            {"name": "Automation Testing", "level": 92, "category": "Primary"}
        ],
        "soft": ["Problem Solving", "Team Leadership", "Technical Documentation"]
    },
    "experience": [
        {
            "id": 1,
            "company": "TechCorp Solutions",
            "position": "Senior API Management Specialist",
            "duration": "2022 - Present",
            "location": "Bangalore, India",
            "type": "Full-time",
            "responsibilities": ["Lead API management initiatives using Kong and APIGEE platforms"],
            "technologies": ["Kong", "APIGEE", "REST APIs"]
        }
    ],
    "projects": [
        {
            "id": 1,
            "title": "Enterprise API Gateway Migration",
            "description": "Led migration of legacy API infrastructure to Kong Gateway",
            "technologies": ["Kong", "Docker", "Kubernetes"],
            "features": ["Migrated 200+ APIs with zero downtime"],
            "status": "Completed",
            "timeline": "6 months"
        }
    ],
    "education": [
        {
            "id": 1,
            "degree": "Bachelor of Technology in Computer Science",
            "institution": "VIT University",
            "duration": "2015 - 2019",
            "location": "Vellore, India",
            "grade": "8.2 CGPA",
            "coursework": ["Data Structures", "Software Engineering"]
        }
    ],
    "certifications": [
        {
            "id": 1,
            "name": "Kong Certified Associate",
            "issuer": "Kong Inc.",
            "date": "2023",
            "credentialId": "KONG-2023-001",
            "validUntil": "2026"
        }
    ]
}

# Routes
@api_router.get("/")
async def root():
    return {"message": "Portfolio API is running", "version": "1.0.0"}

@api_router.get("/portfolio")
async def get_portfolio():
    return PORTFOLIO_DATA

@api_router.post("/contact")
async def submit_contact_form(contact_data: ContactMessage):
    try:
        contact_response = ContactMessageResponse(**contact_data.dict())
        contact_dict = contact_response.dict()
        
        result = await db.contact_messages.insert_one(contact_dict)
        
        return {
            "success": True,
            "message": "Message sent successfully! I'll get back to you soon.",
            "id": contact_response.id
        }
    except Exception as e:
        logging.error(f"Error submitting contact form: {e}")
        raise HTTPException(status_code=500, detail="Failed to send message")

# Initialize database on startup
@app.on_event("startup")
async def startup_db_client():
    try:
        await db.portfolio_data.replace_one({}, PORTFOLIO_DATA, upsert=True)
        print("✅ Database initialized with portfolio data")
    except Exception as e:
        print(f"❌ Database initialization error: {e}")

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
