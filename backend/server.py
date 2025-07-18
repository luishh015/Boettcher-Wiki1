from fastapi import FastAPI, HTTPException, status, Depends, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import os
from pymongo import MongoClient
import uuid
import re
import hashlib
import jwt
import base64
import io
from PIL import Image
import magic

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
categories_collection = db.categories
files_collection = db.files

# JWT Configuration
SECRET_KEY = "boettcher-wiki-secret-key-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours

# Security
security = HTTPBearer()

# File upload configuration
ALLOWED_EXTENSIONS = {
    'images': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'],
    'documents': ['pdf', 'doc', 'docx', 'txt', 'rtf'],
    'spreadsheets': ['xls', 'xlsx', 'csv'],
    'presentations': ['ppt', 'pptx'],
    'other': ['zip', 'rar', '7z']
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Admin credentials
ADMIN_CREDENTIALS = {
    "admin": "boettcher2024",
    "manager": "wiki2024"
}

# Pydantic models
class FileAttachment(BaseModel):
    id: Optional[str] = None
    filename: str
    file_type: str
    file_size: int
    content_type: str
    file_data: str  # Base64 encoded
    thumbnail: Optional[str] = None  # Base64 encoded thumbnail for images
    uploaded_at: Optional[datetime] = None

class KnowledgeEntry(BaseModel):
    id: Optional[str] = None
    question: str
    answer: str
    category: str
    tags: List[str] = []
    attachments: List[FileAttachment] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class Category(BaseModel):
    id: Optional[str] = None
    name: str
    icon: str
    color: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None

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

class DeleteResponse(BaseModel):
    message: str
    deleted_id: str

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

# File handling functions
def get_file_type(filename: str) -> str:
    """Determine file type based on extension"""
    extension = filename.lower().split('.')[-1]
    
    for file_type, extensions in ALLOWED_EXTENSIONS.items():
        if extension in extensions:
            return file_type
    
    return 'other'

def create_thumbnail(image_data: bytes, max_size: tuple = (200, 200)) -> str:
    """Create thumbnail for image files"""
    try:
        image = Image.open(io.BytesIO(image_data))
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'LA', 'P'):
            image = image.convert('RGB')
        
        # Save as JPEG
        thumb_io = io.BytesIO()
        image.save(thumb_io, format='JPEG', quality=85)
        thumb_io.seek(0)
        
        return base64.b64encode(thumb_io.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"Error creating thumbnail: {e}")
        return None

def validate_file(file: UploadFile) -> bool:
    """Validate uploaded file"""
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Datei zu groß (max. 10MB)")
    
    extension = file.filename.lower().split('.')[-1]
    all_allowed = [ext for extensions in ALLOWED_EXTENSIONS.values() for ext in extensions]
    
    if extension not in all_allowed:
        raise HTTPException(status_code=400, detail="Dateityp nicht unterstützt")
    
    return True

# API Routes
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "Böttcher Wiki API"}

@app.post("/api/admin/login", response_model=LoginResponse)
async def admin_login(login_request: LoginRequest):
    """Admin-Anmeldung"""
    username = login_request.username
    password = login_request.password
    
    if username not in ADMIN_CREDENTIALS or ADMIN_CREDENTIALS[username] != password:
        raise HTTPException(status_code=401, detail="Ungültige Anmeldedaten")
    
    access_token = create_access_token(data={"sub": username})
    return LoginResponse(access_token=access_token, username=username)

@app.get("/api/admin/verify")
async def verify_admin(current_user: str = Depends(verify_token)):
    """Token verifizieren"""
    return {"valid": True, "username": current_user}

@app.post("/api/upload", response_model=FileAttachment)
async def upload_file(file: UploadFile = File(...), current_user: str = Depends(verify_token)):
    """Datei hochladen - nur für Admins"""
    validate_file(file)
    
    # Read file content
    file_content = await file.read()
    file_data = base64.b64encode(file_content).decode('utf-8')
    
    # Create thumbnail for images
    thumbnail = None
    file_type = get_file_type(file.filename)
    if file_type == 'images':
        thumbnail = create_thumbnail(file_content)
    
    # Create file attachment
    attachment = FileAttachment(
        id=str(uuid.uuid4()),
        filename=file.filename,
        file_type=file_type,
        file_size=len(file_content),
        content_type=file.content_type,
        file_data=file_data,
        thumbnail=thumbnail,
        uploaded_at=datetime.utcnow()
    )
    
    return attachment

@app.get("/api/files/{file_id}/download")
async def download_file(file_id: str):
    """Datei herunterladen"""
    # Find file in knowledge entries
    entry = knowledge_base.find_one({"attachments.id": file_id})
    if not entry:
        raise HTTPException(status_code=404, detail="Datei nicht gefunden")
    
    # Find specific attachment
    attachment = None
    for att in entry.get("attachments", []):
        if att.get("id") == file_id:
            attachment = att
            break
    
    if not attachment:
        raise HTTPException(status_code=404, detail="Datei nicht gefunden")
    
    # Decode file data
    file_data = base64.b64decode(attachment["file_data"])
    
    # Create response
    return StreamingResponse(
        io.BytesIO(file_data),
        media_type=attachment["content_type"],
        headers={"Content-Disposition": f"attachment; filename={attachment['filename']}"}
    )

@app.post("/api/knowledge", response_model=KnowledgeEntry)
async def create_knowledge_entry(entry: KnowledgeEntry, current_user: str = Depends(verify_token)):
    """Neue Frage/Antwort hinzufügen - nur für Admins"""
    entry.id = str(uuid.uuid4())
    entry.created_at = datetime.utcnow()
    entry.updated_at = datetime.utcnow()
    
    # Ensure all attachments have proper timestamps
    for attachment in entry.attachments:
        if not attachment.uploaded_at:
            attachment.uploaded_at = datetime.utcnow()
    
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
    
    if search_query.query:
        search_pattern = re.compile(search_query.query, re.IGNORECASE)
        query["$or"] = [
            {"question": {"$regex": search_pattern}},
            {"answer": {"$regex": search_pattern}},
            {"tags": {"$regex": search_pattern}}
        ]
    
    if search_query.category:
        query["category"] = search_query.category
    
    entries = list(knowledge_base.find(query).sort("created_at", -1))
    result = []
    
    for entry in entries:
        entry["_id"] = str(entry["_id"])
        result.append(KnowledgeEntry(**entry))
    
    return result

@app.post("/api/categories", response_model=Category)
async def create_category(category: Category, current_user: str = Depends(verify_token)):
    """Neue Kategorie hinzufügen - nur für Admins"""
    existing_category = categories_collection.find_one({"name": category.name})
    if existing_category:
        raise HTTPException(status_code=400, detail="Kategorie existiert bereits")
    
    category.id = str(uuid.uuid4())
    category.created_at = datetime.utcnow()
    
    categories_collection.insert_one(category.dict())
    return category

@app.get("/api/categories")
async def get_categories():
    """Verfügbare Kategorien abrufen - öffentlich"""
    knowledge_categories = knowledge_base.distinct("category")
    custom_categories = list(categories_collection.find({}))
    
    all_categories = set(knowledge_categories)
    for cat in custom_categories:
        all_categories.add(cat["name"])
    
    return {"categories": list(all_categories)}

@app.get("/api/categories/detailed", response_model=List[Category])
async def get_detailed_categories(current_user: str = Depends(verify_token)):
    """Detaillierte Kategorien für Admin-Interface"""
    categories = list(categories_collection.find({}))
    result = []
    
    for cat in categories:
        cat["_id"] = str(cat["_id"])
        result.append(Category(**cat))
    
    return result

@app.delete("/api/categories/{category_id}", response_model=DeleteResponse)
async def delete_category(category_id: str, current_user: str = Depends(verify_token)):
    """Kategorie löschen - nur für Admins"""
    category = categories_collection.find_one({"id": category_id})
    if not category:
        raise HTTPException(status_code=404, detail="Kategorie nicht gefunden")
    
    entries_using_category = knowledge_base.count_documents({"category": category["name"]})
    if entries_using_category > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Kategorie kann nicht gelöscht werden. {entries_using_category} Einträge verwenden diese Kategorie."
        )
    
    result = categories_collection.delete_one({"id": category_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Kategorie nicht gefunden")
    
    return DeleteResponse(message="Kategorie erfolgreich gelöscht", deleted_id=category_id)

@app.get("/api/stats")
async def get_stats():
    """Statistiken abrufen - öffentlich"""
    total_entries = knowledge_base.count_documents({})
    categories_count = len(knowledge_base.distinct("category"))
    
    # Count total attachments
    total_attachments = 0
    for entry in knowledge_base.find({}, {"attachments": 1}):
        total_attachments += len(entry.get("attachments", []))
    
    return {
        "total_entries": total_entries,
        "categories_count": categories_count,
        "total_attachments": total_attachments
    }

@app.put("/api/knowledge/{entry_id}", response_model=KnowledgeEntry)
async def update_knowledge_entry(entry_id: str, entry: KnowledgeEntry, current_user: str = Depends(verify_token)):
    """Wissenseintrag aktualisieren - nur für Admins"""
    existing_entry = knowledge_base.find_one({"id": entry_id})
    if not existing_entry:
        raise HTTPException(status_code=404, detail="Eintrag nicht gefunden")
    
    entry.id = entry_id
    entry.updated_at = datetime.utcnow()
    
    knowledge_base.replace_one({"id": entry_id}, entry.dict())
    return entry

@app.delete("/api/knowledge/{entry_id}", response_model=DeleteResponse)
async def delete_knowledge_entry(entry_id: str, current_user: str = Depends(verify_token)):
    """Wissenseintrag löschen - nur für Admins"""
    entry = knowledge_base.find_one({"id": entry_id})
    if not entry:
        raise HTTPException(status_code=404, detail="Eintrag nicht gefunden")
    
    result = knowledge_base.delete_one({"id": entry_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Eintrag nicht gefunden")
    
    return DeleteResponse(message="Eintrag erfolgreich gelöscht", deleted_id=entry_id)

# Initialize with sample data
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
                "attachments": [],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "question": "Wie führe ich eine Qualitätsprüfung durch?",
                "answer": "1. Prüfliste aus dem Ordner 'Qualitätskontrolle' nehmen\n2. Fahrrad visuell auf Kratzer und Dellen prüfen\n3. Alle Schraubverbindungen auf festen Sitz kontrollieren\n4. Bremsen testen (vorne und hinten)\n5. Schaltung durchschalten und justieren falls nötig\n6. Laufräder auf Rundlauf prüfen\n7. Prüfprotokoll ausfüllen und in Akte ablegen",
                "category": "Qualitätskontrolle",
                "tags": ["qualität", "prüfung", "fahrrad", "kontrolle"],
                "attachments": [],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "question": "Wo finde ich die Bestellformulare?",
                "answer": "Alle Bestellformulare befinden sich:\n1. Digital: Im Netzwerk unter 'N:\\Verwaltung\\Bestellungen'\n2. Physisch: Im blauen Ordner am Verwaltungsplatz\n3. Für Eilbestellungen: Rotes Formular direkt beim Geschäftsführer\n4. Online-Bestellsystem: https://bestellungen.boettcher-bikes.de\n\nWichtig: Bestellungen über 500€ müssen genehmigt werden!",
                "category": "Verwaltung",
                "tags": ["bestellung", "formular", "verwaltung", "prozess"],
                "attachments": [],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "question": "Wie kalibriere ich die Schweißmaschine?",
                "answer": "ACHTUNG: Nur geschultes Personal!\n\n1. Maschine ausschalten und abkühlen lassen\n2. Kalibrierungshandbuch aus dem Maschinenordner holen\n3. Testmaterial (Stahlproben) bereitlegen\n4. Schweißparameter auf Standardwerte setzen:\n   - Spannung: 24V\n   - Stromstärke: 120A\n   - Geschwindigkeit: 15cm/min\n5. Testschweißung durchführen\n6. Naht begutachten und bei Bedarf nachjustieren\n7. Kalibrierung in Wartungsprotokoll eintragen",
                "category": "Produktion",
                "tags": ["schweißen", "kalibrierung", "maschine", "produktion"],
                "attachments": [],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "question": "Wartungsintervalle für Maschinen",
                "answer": "Tägliche Wartung:\n- Maschinen reinigen\n- Öl-/Schmierstoffstand prüfen\n- Sichtprüfung auf Verschleiß\n\nWöchentliche Wartung:\n- Schmierung aller beweglichen Teile\n- Spänebehälter leeren\n- Kühlflüssigkeit prüfen\n\nMonatliche Wartung:\n- Vollständige Inspektion\n- Verschleißteile prüfen\n- Wartungsprotokoll führen\n- Bei Bedarf Fachfirma beauftragen\n\nWartungsplan hängt an jeder Maschine aus!",
                "category": "Wartung",
                "tags": ["wartung", "maschine", "intervall", "pflege"],
                "attachments": [],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        knowledge_base.insert_many(sample_entries)
        print("Beispieldaten zur Wissensdatenbank hinzugefügt")
    
    if categories_collection.count_documents({}) == 0:
        default_categories = [
            {
                "id": str(uuid.uuid4()),
                "name": "Sicherheit",
                "icon": "🛡️",
                "color": "bg-red-100 text-red-800 border-red-500",
                "description": "Sicherheitsrichtlinien und -verfahren",
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Schulung",
                "icon": "🎓",
                "color": "bg-indigo-100 text-indigo-800 border-indigo-500",
                "description": "Schulungsmaterialien und -prozesse",
                "created_at": datetime.utcnow()
            }
        ]
        
        categories_collection.insert_many(default_categories)
        print("Standard-Kategorien hinzugefügt")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)