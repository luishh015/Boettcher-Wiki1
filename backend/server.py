from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import os
from pymongo import MongoClient
import uuid
import re
import hashlib
import jwt

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
knowledge_base = db.knowledge_base

# JWT Configuration
SECRET_KEY = "boettcher-wiki-secret-key-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours

# Security
security = HTTPBearer()

# Admin credentials (in production, use environment variables)
ADMIN_CREDENTIALS = {
    "admin": "boettcher2024",
    "manager": "wiki2024"
}

# Pydantic models
class KnowledgeEntry(BaseModel):
    id: Optional[str] = None
    question: str
    answer: str
    category: str
    tags: List[str] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class SearchQuery(BaseModel):
    query: str
    category: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str

# Authentication functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return username
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# API Routes
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "Böttcher Wiki API"}

@app.post("/api/admin/login", response_model=LoginResponse)
async def admin_login(login_request: LoginRequest):
    """Admin-Anmeldung"""
    username = login_request.username
    password = login_request.password
    
    # Verify credentials
    if username not in ADMIN_CREDENTIALS or ADMIN_CREDENTIALS[username] != password:
        raise HTTPException(
            status_code=401,
            detail="Ungültige Anmeldedaten"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": username})
    
    return LoginResponse(
        access_token=access_token,
        username=username
    )

@app.get("/api/admin/verify")
async def verify_admin(current_user: str = Depends(verify_token)):
    """Token verifizieren"""
    return {"valid": True, "username": current_user}

@app.post("/api/knowledge", response_model=KnowledgeEntry)
async def create_knowledge_entry(entry: KnowledgeEntry, current_user: str = Depends(verify_token)):
    """Neue Frage/Antwort hinzufügen - nur für Admins"""
    entry.id = str(uuid.uuid4())
    entry.created_at = datetime.utcnow()
    entry.updated_at = datetime.utcnow()
    
    # Insert into database
    knowledge_base.insert_one(entry.dict())
    return entry

@app.get("/api/knowledge", response_model=List[KnowledgeEntry])
async def get_all_knowledge(category: Optional[str] = None, limit: int = 100):
    """Alle Wissenseinträge abrufen - öffentlich"""
    query = {}
    if category:
        query["category"] = category
    
    entries = list(knowledge_base.find(query).sort("created_at", -1).limit(limit))
    result = []
    
    for entry in entries:
        entry["_id"] = str(entry["_id"])
        result.append(KnowledgeEntry(**entry))
    
    return result

@app.post("/api/search", response_model=List[KnowledgeEntry])
async def search_knowledge(search_query: SearchQuery):
    """Wissensdatenbank durchsuchen - öffentlich"""
    query = {}
    
    # Text search in question, answer and tags
    if search_query.query:
        search_pattern = re.compile(search_query.query, re.IGNORECASE)
        query["$or"] = [
            {"question": {"$regex": search_pattern}},
            {"answer": {"$regex": search_pattern}},
            {"tags": {"$regex": search_pattern}}
        ]
    
    # Category filter
    if search_query.category:
        query["category"] = search_query.category
    
    entries = list(knowledge_base.find(query).sort("created_at", -1))
    result = []
    
    for entry in entries:
        entry["_id"] = str(entry["_id"])
        result.append(KnowledgeEntry(**entry))
    
    return result

@app.get("/api/categories")
async def get_categories():
    """Verfügbare Kategorien abrufen - öffentlich"""
    categories = knowledge_base.distinct("category")
    return {"categories": categories}

@app.get("/api/stats")
async def get_stats():
    """Statistiken abrufen - öffentlich"""
    total_entries = knowledge_base.count_documents({})
    categories_count = len(knowledge_base.distinct("category"))
    
    return {
        "total_entries": total_entries,
        "categories_count": categories_count
    }

@app.put("/api/knowledge/{entry_id}", response_model=KnowledgeEntry)
async def update_knowledge_entry(entry_id: str, entry: KnowledgeEntry, current_user: str = Depends(verify_token)):
    """Wissenseintrag aktualisieren - nur für Admins"""
    # Check if entry exists
    existing_entry = knowledge_base.find_one({"id": entry_id})
    if not existing_entry:
        raise HTTPException(status_code=404, detail="Eintrag nicht gefunden")
    
    entry.id = entry_id
    entry.updated_at = datetime.utcnow()
    
    # Update in database
    knowledge_base.replace_one({"id": entry_id}, entry.dict())
    return entry

@app.delete("/api/knowledge/{entry_id}")
async def delete_knowledge_entry(entry_id: str, current_user: str = Depends(verify_token)):
    """Wissenseintrag löschen - nur für Admins"""
    result = knowledge_base.delete_one({"id": entry_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Eintrag nicht gefunden")
    
    return {"message": "Eintrag erfolgreich gelöscht"}

# Initialize with sample data if database is empty
@app.on_event("startup")
async def initialize_sample_data():
    """Beispieldaten hinzufügen falls Datenbank leer ist"""
    if knowledge_base.count_documents({}) == 0:
        sample_entries = [
            {
                "id": str(uuid.uuid4()),
                "question": "Was tun wenn der Scanner nicht funktioniert?",
                "answer": "1. Überprüfen Sie alle Kabelverbindungen\n2. Starten Sie den Scanner neu\n3. Prüfen Sie ob die Scanner-Software geöffnet ist\n4. Kontrollieren Sie die Stromversorgung\n5. Bei weiteren Problemen IT-Support kontaktieren",
                "category": "IT-Support",
                "tags": ["scanner", "hardware", "fehlerbehebung"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "question": "Wie führe ich eine Qualitätsprüfung durch?",
                "answer": "1. Prüfliste aus dem Ordner 'Qualitätskontrolle' nehmen\n2. Fahrrad visuell auf Kratzer und Dellen prüfen\n3. Alle Schraubverbindungen auf festen Sitz kontrollieren\n4. Bremsen testen (vorne und hinten)\n5. Schaltung durchschalten und justieren falls nötig\n6. Laufräder auf Rundlauf prüfen\n7. Prüfprotokoll ausfüllen und in Akte ablegen",
                "category": "Qualitätskontrolle",
                "tags": ["qualität", "prüfung", "fahrrad", "kontrolle"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "question": "Wo finde ich die Bestellformulare?",
                "answer": "Alle Bestellformulare befinden sich:\n1. Digital: Im Netzwerk unter 'N:\\Verwaltung\\Bestellungen'\n2. Physisch: Im blauen Ordner am Verwaltungsplatz\n3. Für Eilbestellungen: Rotes Formular direkt beim Geschäftsführer\n4. Online-Bestellsystem: https://bestellungen.boettcher-bikes.de\n\nWichtig: Bestellungen über 500€ müssen genehmigt werden!",
                "category": "Verwaltung",
                "tags": ["bestellung", "formular", "verwaltung", "prozess"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "question": "Wie kalibriere ich die Schweißmaschine?",
                "answer": "ACHTUNG: Nur geschultes Personal!\n\n1. Maschine ausschalten und abkühlen lassen\n2. Kalibrierungshandbuch aus dem Maschinenordner holen\n3. Testmaterial (Stahlproben) bereitlegen\n4. Schweißparameter auf Standardwerte setzen:\n   - Spannung: 24V\n   - Stromstärke: 120A\n   - Geschwindigkeit: 15cm/min\n5. Testschweißung durchführen\n6. Naht begutachten und bei Bedarf nachjustieren\n7. Kalibrierung in Wartungsprotokoll eintragen",
                "category": "Produktion",
                "tags": ["schweißen", "kalibrierung", "maschine", "produktion"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "question": "Wartungsintervalle für Maschinen",
                "answer": "Tägliche Wartung:\n- Maschinen reinigen\n- Öl-/Schmierstoffstand prüfen\n- Sichtprüfung auf Verschleiß\n\nWöchentliche Wartung:\n- Schmierung aller beweglichen Teile\n- Spänebehälter leeren\n- Kühlflüssigkeit prüfen\n\nMonatliche Wartung:\n- Vollständige Inspektion\n- Verschleißteile prüfen\n- Wartungsprotokoll führen\n- Bei Bedarf Fachfirma beauftragen\n\nWartungsplan hängt an jeder Maschine aus!",
                "category": "Wartung",
                "tags": ["wartung", "maschine", "intervall", "pflege"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        knowledge_base.insert_many(sample_entries)
        print("Beispieldaten zur Wissensdatenbank hinzugefügt")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)