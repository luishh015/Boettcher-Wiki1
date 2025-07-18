# Anpassungs-Guide

## 🎨 Design anpassen

### Farben ändern
```css
/* frontend/src/App.css */

/* Hauptfarben */
:root {
  --primary-color: #3B82F6;    /* Blau */
  --secondary-color: #10B981;  /* Grün */
  --accent-color: #8B5CF6;     /* Lila */
  --danger-color: #EF4444;     /* Rot */
}

/* Gradient-Hintergründe */
.bg-gradient-primary {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
}
```

### Logo/Branding ändern
```javascript
// frontend/src/App.js
// Zeile ~XXX - Header-Bereich

<div className="flex items-center space-x-4">
  <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-3 rounded-full">
    {/* Hier Ihr Logo einfügen */}
    <img src="/logo.svg" alt="Ihr Logo" className="w-8 h-8" />
  </div>
  <div>
    <h1 className="text-3xl font-bold text-gray-800">Ihr Firmenname</h1>
    <p className="text-blue-600 font-medium">Ihre Beschreibung</p>
  </div>
</div>
```

## 🔧 Funktionalität erweitern

### Neue Kategorie-Icons hinzufügen
```javascript
// frontend/src/App.js
// Zeile ~XXX - commonIcons Array

const commonIcons = [
  '📘', '🔧', '💻', '📋', '⚙️', '🛡️', '🎓', '🔍', 
  '📊', '🏭', '🔬', '📞', '🎨', '🌟',
  // Ihre neuen Icons hier hinzufügen
  '🚴', '🔩', '🛠️', '📐', '🎯'
];
```

### Neue Dateitypen unterstützen
```python
# backend/server.py
# Zeile ~XXX - ALLOWED_EXTENSIONS

ALLOWED_EXTENSIONS = {
    'images': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'],
    'documents': ['pdf', 'doc', 'docx', 'txt', 'rtf'],
    'spreadsheets': ['xls', 'xlsx', 'csv'],
    'presentations': ['ppt', 'pptx'],
    'cad': ['dwg', 'dxf'],  # CAD-Dateien hinzufügen
    'other': ['zip', 'rar', '7z']
}
```

## 🔐 Sicherheit anpassen

### Admin-Zugangsdaten ändern
```python
# backend/server.py
# Zeile ~XXX - ADMIN_CREDENTIALS

ADMIN_CREDENTIALS = {
    "ihr_admin": "ihr_sicheres_passwort",
    "ihr_manager": "ihr_manager_passwort"
}
```

### JWT-Token-Laufzeit ändern
```python
# backend/server.py
# Zeile ~XXX - ACCESS_TOKEN_EXPIRE_MINUTES

ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 Stunden
# Oder für kürzere Sitzungen:
ACCESS_TOKEN_EXPIRE_MINUTES = 60   # 1 Stunde
```

## 📊 Datenbank-Anpassungen

### Neue Felder zu Einträgen hinzufügen
```python
# backend/server.py
# KnowledgeEntry-Modell erweitern

class KnowledgeEntry(BaseModel):
    id: Optional[str] = None
    question: str
    answer: str
    category: str
    tags: List[str] = []
    attachments: List[FileAttachment] = []
    # Neue Felder hinzufügen
    priority: str = "normal"  # low, normal, high, urgent
    author: str = "Admin"
    last_updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
```

### Neue API-Endpunkte hinzufügen
```python
# backend/server.py
# Neuen Endpunkt hinzufügen

@app.get("/api/knowledge/priority/{priority}")
async def get_knowledge_by_priority(priority: str):
    """Einträge nach Priorität filtern"""
    entries = list(knowledge_base.find({"priority": priority}))
    result = []
    for entry in entries:
        entry["_id"] = str(entry["_id"])
        result.append(KnowledgeEntry(**entry))
    return result
```

## 🎯 UI-Komponenten erweitern

### Neue Kategorie-Farben hinzufügen
```javascript
// frontend/src/App.js
// predefinedColors Array erweitern

const predefinedColors = [
  { name: 'Blau', value: 'bg-blue-100 text-blue-800 border-blue-500' },
  { name: 'Grün', value: 'bg-green-100 text-green-800 border-green-500' },
  // Neue Farben hinzufügen
  { name: 'Türkis', value: 'bg-teal-100 text-teal-800 border-teal-500' },
  { name: 'Cyan', value: 'bg-cyan-100 text-cyan-800 border-cyan-500' },
];
```

### Neue Statistik-Karten hinzufügen
```javascript
// frontend/src/App.js
// Stats-Bereich erweitern

<div className="bg-white rounded-lg p-6 shadow-md border-l-4 border-yellow-500">
  <div className="flex items-center">
    <div className="bg-gradient-to-r from-yellow-500 to-yellow-600 text-white p-3 rounded-full mr-4">
      <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
        {/* Ihr Icon hier */}
      </svg>
    </div>
    <div>
      <p className="text-sm font-medium text-gray-600">Ihre Statistik</p>
      <p className="text-2xl font-bold text-gray-900">{stats.your_stat || 0}</p>
    </div>
  </div>
</div>
```

## 🔄 Workflow-Anpassungen

### Automatische Kategorien
```python
# backend/server.py
# Funktion hinzufügen

def auto_categorize_entry(question: str, answer: str) -> str:
    """Automatische Kategorisierung basierend auf Inhalt"""
    text = f"{question} {answer}".lower()
    
    if any(word in text for word in ['computer', 'software', 'scanner', 'pc']):
        return 'IT-Support'
    elif any(word in text for word in ['maschine', 'schweißen', 'produktion']):
        return 'Produktion'
    elif any(word in text for word in ['qualität', 'prüfung', 'kontrolle']):
        return 'Qualitätskontrolle'
    else:
        return 'Allgemein'
```

### E-Mail-Benachrichtigungen
```python
# backend/server.py
# E-Mail-Funktion hinzufügen

import smtplib
from email.mime.text import MIMEText

def send_notification(subject: str, body: str, to_email: str):
    """E-Mail-Benachrichtigung senden"""
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'wiki@boettcher.com'
    msg['To'] = to_email
    
    with smtplib.SMTP('localhost') as server:
        server.send_message(msg)
```

## 📱 Mobile Optimierung

### Touch-Gesten hinzufügen
```javascript
// frontend/src/App.js
// Touch-Event-Handler hinzufügen

const handleTouchStart = (e) => {
  setTouchStart(e.touches[0].clientX);
};

const handleTouchMove = (e) => {
  if (!touchStart) return;
  
  const touchEnd = e.touches[0].clientX;
  const diff = touchStart - touchEnd;
  
  if (diff > 50) {
    // Swipe left - nächster Eintrag
    nextEntry();
  } else if (diff < -50) {
    // Swipe right - vorheriger Eintrag
    previousEntry();
  }
};
```

## 🔍 Erweiterte Suche

### Fuzzy-Suche implementieren
```python
# backend/server.py
# Fuzzy-Suche hinzufügen

from fuzzywuzzy import fuzz

def fuzzy_search(query: str, entries: List[dict]) -> List[dict]:
    """Fuzzy-Suche für ähnliche Begriffe"""
    results = []
    for entry in entries:
        score = fuzz.ratio(query.lower(), entry['question'].lower())
        if score > 60:  # Mindest-Ähnlichkeit
            entry['similarity_score'] = score
            results.append(entry)
    
    return sorted(results, key=lambda x: x['similarity_score'], reverse=True)
```

## 🛡️ Erweiterte Sicherheit

### Rollen-basierte Zugriffskontrolle
```python
# backend/server.py
# Rollen-System hinzufügen

class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    VIEWER = "viewer"

def check_permission(required_role: UserRole):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            user_role = get_user_role(current_user)
            
            if user_role != required_role:
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

## 📈 Performance-Optimierung

### Caching hinzufügen
```python
# backend/server.py
# Redis-Caching hinzufügen

import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_get(key: str):
    """Cache-Wert abrufen"""
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)
    return None

def cache_set(key: str, value: dict, expire: int = 3600):
    """Cache-Wert setzen"""
    redis_client.setex(key, expire, json.dumps(value))
```

---

## 🚀 Häufige Anpassungen

### 1. Firmenbranding
- Logo in `frontend/public/logo.svg`
- Firmenname in `App.js`
- Farben in `App.css`

### 2. Neue Kategorien
- Icons in `commonIcons` Array
- Farben in `predefinedColors` Array

### 3. Zusätzliche Statistiken
- Backend: Neue Statistik-Berechnung
- Frontend: Neue Statistik-Karte

### 4. Erweiterte Dateitypen
- `ALLOWED_EXTENSIONS` im Backend
- Icon-Zuordnung im Frontend

### 5. Zusätzliche Sicherheit
- Passwort-Komplexität
- Zwei-Faktor-Authentifizierung
- Audit-Logging