from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Note Models
class Note(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class NoteCreate(BaseModel):
    title: str
    content: str

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


# Note endpoints
@api_router.get("/notes", response_model=List[Note])
async def get_notes():
    """Get all notes"""
    try:
        notes = await db.notes.find().sort("updated_at", -1).to_list(1000)
        return [Note(**note) for note in notes]
    except Exception as e:
        logging.error(f"Error fetching notes: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.post("/notes", response_model=Note)
async def create_note(note_data: NoteCreate):
    """Create a new note"""
    try:
        note_dict = note_data.dict()
        note_obj = Note(**note_dict)
        await db.notes.insert_one(note_obj.dict())
        return note_obj
    except Exception as e:
        logging.error(f"Error creating note: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.get("/notes/{note_id}", response_model=Note)
async def get_note(note_id: str):
    """Get a specific note by ID"""
    try:
        note = await db.notes.find_one({"id": note_id})
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        return Note(**note)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching note: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.put("/notes/{note_id}", response_model=Note)
async def update_note(note_id: str, note_data: NoteUpdate):
    """Update an existing note"""
    try:
        # Check if note exists
        existing_note = await db.notes.find_one({"id": note_id})
        if not existing_note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        # Update only provided fields
        update_data = {k: v for k, v in note_data.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        await db.notes.update_one({"id": note_id}, {"$set": update_data})
        
        # Return updated note
        updated_note = await db.notes.find_one({"id": note_id})
        return Note(**updated_note)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error updating note: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.delete("/notes/{note_id}")
async def delete_note(note_id: str):
    """Delete a note"""
    try:
        result = await db.notes.delete_one({"id": note_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Note not found")
        return {"message": "Note deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting note: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Health check endpoint
@api_router.get("/")
async def root():
    return {"message": "Notes API is running"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()