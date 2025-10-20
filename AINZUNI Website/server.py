from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'ainzuni_db')]

# LLM Configuration
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Models
class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    message: str
    response: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    language: Optional[str] = "en"  # Default to English

class University(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    fields: List[str]
    entry_requirements: dict
    fees: dict
    scholarships: List[str]
    majors_minors: dict
    career_pathways: List[str]
    contact: dict

# System prompt for AINZUNI chatbot
AINZUNI_SYSTEM_PROMPT = """You are AINZUNI, an expert AI assistant helping students and parents choose the best universities in New Zealand for undergraduate studies.

Your expertise covers:
- 8 NZ Universities: University of Auckland (UOA), University of Otago, University of Waikato, Massey University, University of Canterbury, Victoria University of Wellington, Lincoln University, Auckland University of Technology (AUT)
- 7 Key Fields: Engineering, Science, Commerce, Medicine (MBChB - Doctor qualification), Music, Law, and Arts
- Undergraduate programs ONLY (exclude PhD, Postgraduate, Diploma, Certificate)

Key Facts:
- Only UOA and University of Otago offer MBChB (Bachelor of Medicine and Bachelor of Surgery) leading to doctor qualification
- UOA ranks #1 in New Zealand in world university rankings
- Each university has specialized strengths in different fields

You provide:
1. Detailed comparisons of universities based on student preferences
2. Entry requirements (domestic and international)
3. Fee information and scholarship opportunities
4. Programme structures and major/minor subject combinations
5. Career pathways and further study options
6. Personalized recommendations based on student profile

You are helpful, accurate, and focus ONLY on undergraduate options in the 7 specified fields. Be conversational, encouraging, and provide specific, actionable information. If asked about programs outside your scope, politely redirect to your areas of expertise.

Always provide evidence-based information and cite which universities offer specific programs."""

async def get_chat_response(message: str, session_id: str, language: str = "en") -> str:
    """Get AI response using GPT-5"""
    try:
        # Create chat instance
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=session_id,
            system_message=AINZUNI_SYSTEM_PROMPT
        ).with_model("openai", "gpt-5")
        
        # Add language instruction if not English
        language_instruction = ""
        if language != "en":
            language_names = {
                "es": "Spanish",
                "fr": "French",
                "zh": "Chinese",
                "hi": "Hindi",
                "ar": "Arabic",
                "pt": "Portuguese",
                "de": "German",
                "ja": "Japanese",
                "ko": "Korean"
            }
            lang_name = language_names.get(language, language)
            language_instruction = f"Please respond in {lang_name}. "
        
        # Fetch university data from database for context
        universities = await db.universities.find({}, {"_id": 0}).limit(10).to_list(10)
        
        context = "\n\nCurrent University Data Available:\n"
        if universities:
            for uni in universities:
                context += f"- {uni.get('name', 'N/A')}: Fields: {', '.join(uni.get('fields', [])))}\n"
        
        full_message = language_instruction + message + context
        
        user_message = UserMessage(text=full_message)
        response = await chat.send_message(user_message)
        
        return response
    
    except Exception as e:
        logging.error(f"Chat error: {str(e)}")
        return f"I apologize, but I'm having trouble processing your request right now. Please try again. Error: {str(e)}"

# API Routes
@api_router.post("/chat")
async def chat(request: ChatRequest):
    """Handle chat messages"""
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get AI response
        response = await get_chat_response(
            request.message, 
            session_id,
            request.language or "en"
        )
        
        # Save chat history
        chat_msg = ChatMessage(
            session_id=session_id,
            message=request.message,
            response=response
        )
        
        chat_dict = chat_msg.model_dump()
        chat_dict['timestamp'] = chat_dict['timestamp'].isoformat()
        
        await db.chat_history.insert_one(chat_dict)
        
        return {
            "success": True,
            "response": response,
            "session_id": session_id
        }
    
    except Exception as e:
        logging.error(f"Chat endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/universities")
async def get_universities():
    """Get all universities"""
    universities = await db.universities.find({}, {"_id": 0}).to_list(100)
    return {"success": True, "universities": universities}

@api_router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    history = await db.chat_history.find(
        {"session_id": session_id},
        {"_id": 0}
    ).sort("timestamp", 1).to_list(100)
    
    for msg in history:
        if isinstance(msg.get('timestamp'), str):
            msg['timestamp'] = datetime.fromisoformat(msg['timestamp'])
    
    return {"success": True, "history": history}

@api_router.get("/")
async def root():
    return {"message": "AINZUNI API", "status": "online"}

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_db():
    """Initialize database with sample university data"""
    count = await db.universities.count_documents({})
    if count == 0:
        # Add sample data for all 8 universities
        sample_universities = [
            {
                "id": str(uuid.uuid4()),
                "name": "University of Auckland (UOA)",
                "rank": "#1 in New Zealand",
                "fields": ["Engineering", "Science", "Commerce", "Medicine", "Music", "Law", "Arts"],
                "entry_requirements": {
                    "Medicine": "NCEA Level 3 with Excellence in Sciences, Biology, Chemistry required. Highly competitive.",
                    "Engineering": "NCEA Level 3 with strong Mathematics and Physics",
                    "Law": "NCEA Level 3, competitive GPA required"
                },
                "fees": {
                    "domestic": "$6,000 - $9,000 per year",
                    "international": "$30,000 - $45,000 per year (Medicine: $80,000+)"
                },
                "scholarships": ["Vice-Chancellor's Scholarship", "Faculty Scholarships", "Māori and Pacific Scholarships"],
                "majors_minors": {
                    "Engineering": ["Biomedical", "Civil", "Computer Systems", "Electrical", "Mechanical", "Software"],
                    "Science": ["Biology", "Chemistry", "Physics", "Computer Science", "Psychology"],
                    "Commerce": ["Accounting", "Economics", "Finance", "Marketing", "Management"]
                },
                "career_pathways": ["Doctor (MBChB)", "Engineer", "Lawyer", "Business Manager", "Researcher"],
                "contact": {"website": "https://www.auckland.ac.nz", "email": "student.info@auckland.ac.nz"}
            },
            {
                "id": str(uuid.uuid4()),
                "name": "University of Otago",
                "rank": "#2 in New Zealand, Oldest University (1869)",
                "fields": ["Medicine", "Health Sciences", "Science", "Commerce", "Law", "Arts"],
                "entry_requirements": {
                    "Medicine": "First Year Health Sciences (competitive entry), Top academic performance required",
                    "Science": "NCEA Level 3 with University Entrance"
                },
                "fees": {
                    "domestic": "$6,000 - $9,000 per year",
                    "international": "$28,000 - $75,000 per year (Medicine)"
                },
                "scholarships": ["Otago Scholarship", "Māori Entrance Scholarship", "Pacific Scholarship"],
                "majors_minors": {
                    "Medicine": ["MBChB - 6 years"],
                    "Health Sciences": ["Dentistry", "Pharmacy", "Physiotherapy"],
                    "Science": ["Neuroscience", "Genetics", "Marine Science"]
                },
                "career_pathways": ["Doctor", "Dentist", "Pharmacist", "Research Scientist"],
                "contact": {"website": "https://www.otago.ac.nz", "email": "international@otago.ac.nz"}
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Auckland University of Technology (AUT)",
                "rank": "Top 1% worldwide",
                "fields": ["Engineering", "Science", "Commerce", "Arts", "Design"],
                "entry_requirements": {
                    "Engineering": "NCEA Level 3 with Physics and Mathematics",
                    "Commerce": "NCEA Level 3 University Entrance"
                },
                "fees": {
                    "domestic": "$6,500 - $9,000 per year",
                    "international": "$30,000 - $42,000 per year"
                },
                "scholarships": ["Vice-Chancellor's Scholarship", "AUT Excellence Scholarship"],
                "majors_minors": {
                    "Engineering": ["Software", "Mechatronics", "Construction"],
                    "Commerce": ["Business Analytics", "Digital Marketing"]
                },
                "career_pathways": ["Software Developer", "Business Analyst", "Designer"],
                "contact": {"website": "https://www.aut.ac.nz", "email": "international@aut.ac.nz"}
            }
        ]
        
        await db.universities.insert_many(sample_universities)
        logger.info("Initialized database with sample university data")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()