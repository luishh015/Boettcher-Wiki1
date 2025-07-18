from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
from pymongo import MongoClient
import uuid
import re

app = FastAPI(title="Böttcher Wiki API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URL)
db = client.boettcher_wiki
questions_collection = db.questions
answers_collection = db.answers

# Pydantic models
class Question(BaseModel):
    id: Optional[str] = None
    question_text: str
    category: str
    author: str
    created_at: Optional[datetime] = None
    tags: List[str] = []
    answered: bool = False

class Answer(BaseModel):
    id: Optional[str] = None
    question_id: str
    answer_text: str
    author: str
    created_at: Optional[datetime] = None
    helpful_count: int = 0

class QuestionAnswer(BaseModel):
    question: Question
    answer: Optional[Answer] = None

class SearchQuery(BaseModel):
    query: str
    category: Optional[str] = None

# API Routes
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "Böttcher Wiki API"}

@app.post("/api/questions", response_model=Question)
async def create_question(question: Question):
    """Neue Frage hinzufügen"""
    question.id = str(uuid.uuid4())
    question.created_at = datetime.utcnow()
    question.answered = False
    
    # Insert into database
    questions_collection.insert_one(question.dict())
    return question

@app.get("/api/questions", response_model=List[QuestionAnswer])
async def get_all_questions(category: Optional[str] = None, limit: int = 50):
    """Alle Fragen mit Antworten abrufen"""
    query = {}
    if category:
        query["category"] = category
    
    questions = list(questions_collection.find(query).sort("created_at", -1).limit(limit))
    result = []
    
    for q in questions:
        q["_id"] = str(q["_id"])
        question_obj = Question(**q)
        
        # Get answer if exists
        answer_doc = answers_collection.find_one({"question_id": q["id"]})
        answer_obj = None
        if answer_doc:
            answer_doc["_id"] = str(answer_doc["_id"])
            answer_obj = Answer(**answer_doc)
        
        result.append(QuestionAnswer(question=question_obj, answer=answer_obj))
    
    return result

@app.post("/api/questions/{question_id}/answer", response_model=Answer)
async def create_answer(question_id: str, answer: Answer):
    """Antwort zu einer Frage hinzufügen"""
    # Check if question exists
    question = questions_collection.find_one({"id": question_id})
    if not question:
        raise HTTPException(status_code=404, detail="Frage nicht gefunden")
    
    # Check if answer already exists
    existing_answer = answers_collection.find_one({"question_id": question_id})
    if existing_answer:
        raise HTTPException(status_code=400, detail="Antwort bereits vorhanden")
    
    answer.id = str(uuid.uuid4())
    answer.question_id = question_id
    answer.created_at = datetime.utcnow()
    answer.helpful_count = 0
    
    # Insert answer
    answers_collection.insert_one(answer.dict())
    
    # Update question as answered
    questions_collection.update_one(
        {"id": question_id},
        {"$set": {"answered": True}}
    )
    
    return answer

@app.post("/api/search", response_model=List[QuestionAnswer])
async def search_questions(search_query: SearchQuery):
    """Fragen durchsuchen"""
    query = {}
    
    # Text search in question text and tags
    if search_query.query:
        search_pattern = re.compile(search_query.query, re.IGNORECASE)
        query["$or"] = [
            {"question_text": {"$regex": search_pattern}},
            {"tags": {"$regex": search_pattern}}
        ]
    
    # Category filter
    if search_query.category:
        query["category"] = search_query.category
    
    questions = list(questions_collection.find(query).sort("created_at", -1))
    result = []
    
    for q in questions:
        q["_id"] = str(q["_id"])
        question_obj = Question(**q)
        
        # Get answer if exists
        answer_doc = answers_collection.find_one({"question_id": q["id"]})
        answer_obj = None
        if answer_doc:
            answer_doc["_id"] = str(answer_doc["_id"])
            answer_obj = Answer(**answer_doc)
        
        result.append(QuestionAnswer(question=question_obj, answer=answer_obj))
    
    return result

@app.get("/api/categories")
async def get_categories():
    """Verfügbare Kategorien abrufen"""
    categories = questions_collection.distinct("category")
    return {"categories": categories}

@app.get("/api/stats")
async def get_stats():
    """Statistiken abrufen"""
    total_questions = questions_collection.count_documents({})
    answered_questions = questions_collection.count_documents({"answered": True})
    unanswered_questions = total_questions - answered_questions
    
    return {
        "total_questions": total_questions,
        "answered_questions": answered_questions,
        "unanswered_questions": unanswered_questions
    }

@app.delete("/api/questions/{question_id}")
async def delete_question(question_id: str):
    """Frage löschen"""
    result = questions_collection.delete_one({"id": question_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Frage nicht gefunden")
    
    # Also delete associated answer
    answers_collection.delete_one({"question_id": question_id})
    
    return {"message": "Frage erfolgreich gelöscht"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)