# 📁 Datei-Übersicht: Böttcher Wiki

## 🏗️ Projektstruktur

```
boettcher-wiki/
├── 📄 README.md              # Haupt-Dokumentation
├── 📄 SETUP-GUIDE.md         # Schritt-für-Schritt Anleitung
├── 📄 .gitignore             # Git-Ignorierdatei
├── 📄 docker-compose.yml     # Docker-Konfiguration
├── 📂 backend/               # FastAPI Python-Backend
├── 📂 frontend/              # React JavaScript-Frontend
└── 📂 docs/                  # Dokumentation
```

---

## 🔧 Backend-Dateien (`/backend/`)

### 📄 `server.py` - Haupt-API-Server (1.180 Zeilen)
**Zweck:** Kern der Anwendung - alle API-Endpunkte und Geschäftslogik

**Wichtige Bereiche:**
```python
# Zeile 1-50: Imports und Konfiguration
from fastapi import FastAPI, HTTPException, status, Depends, File, UploadFile, Form
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
ADMIN_CREDENTIALS = {"admin": "boettcher2024", "manager": "wiki2024"}

# Zeile 51-150: Datenmodelle (Pydantic)
class KnowledgeEntry(BaseModel):
    question: str
    answer: str
    category: str
    tags: List[str] = []
    attachments: List[FileAttachment] = []

# Zeile 151-300: Authentifizierung
def create_access_token(data: dict):
    # JWT-Token erstellen
    
def verify_token(credentials: HTTPAuthorizationCredentials):
    # Token validieren

# Zeile 301-600: Wissenseinträge-API
@app.post("/api/knowledge")           # Eintrag erstellen
@app.get("/api/knowledge")            # Einträge abrufen
@app.put("/api/knowledge/{id}")       # Eintrag bearbeiten
@app.delete("/api/knowledge/{id}")    # Eintrag löschen

# Zeile 601-800: Datei-Upload-API
@app.post("/api/upload")              # Datei hochladen
@app.get("/api/files/{id}/download")  # Datei herunterladen
def create_thumbnail(image_data):      # Thumbnail erstellen
def validate_file(file):              # Datei validieren

# Zeile 801-1000: Kategorien-API
@app.post("/api/categories")          # Kategorie erstellen
@app.get("/api/categories")           # Kategorien abrufen
@app.delete("/api/categories/{id}")   # Kategorie löschen

# Zeile 1001-1180: Initialisierung
@app.on_event("startup")
async def initialize_sample_data():   # Beispieldaten laden
```

**Änderungen vornehmen:**
- **Admin-Passwörter:** Zeile ~47 `ADMIN_CREDENTIALS`
- **Neue API-Endpunkte:** Nach Zeile 1000 hinzufügen
- **Dateitypen:** Zeile ~35 `ALLOWED_EXTENSIONS`
- **Kategorien:** Zeile ~1100 `sample_entries`

### 📄 `requirements.txt` - Python-Abhängigkeiten
**Zweck:** Alle benötigten Python-Pakete definieren

```txt
fastapi==0.104.1          # Web-Framework
uvicorn==0.24.0          # ASGI-Server
pymongo==4.5.0           # MongoDB-Driver
pydantic==2.4.2          # Datenvalidierung
python-multipart==0.0.6  # Datei-Upload
PyJWT==2.8.0             # JWT-Token
Pillow==10.0.1           # Bildverarbeitung
python-magic==0.4.27     # Dateityp-Erkennung
```

**Neue Pakete hinzufügen:**
```bash
# Paket installieren
pip install neues-paket

# requirements.txt aktualisieren
echo "neues-paket==1.0.0" >> requirements.txt
```

### 📄 `.env.example` - Umgebungsvariablen-Vorlage
**Zweck:** Beispiel-Konfiguration für Produktionsumgebung

```env
MONGO_URL=mongodb://localhost:27017/
SECRET_KEY=your-very-secret-key-here
HOST=0.0.0.0
PORT=8001
```

**Anpassen:**
1. Kopieren zu `.env`: `cp .env.example .env`
2. Werte anpassen für Ihre Umgebung

### 📄 `Dockerfile` - Docker-Container-Konfiguration
**Zweck:** Backend als Docker-Container verpacken

```dockerfile
FROM python:3.9-slim     # Basis-Image
WORKDIR /app             # Arbeitsverzeichnis
COPY requirements.txt .  # Abhängigkeiten kopieren
RUN pip install -r requirements.txt  # Abhängigkeiten installieren
COPY . .                 # Code kopieren
EXPOSE 8001              # Port freigeben
CMD ["python", "server.py"]  # Start-Kommando
```

---

## 🎨 Frontend-Dateien (`/frontend/`)

### 📄 `src/App.js` - Haupt-React-Komponente (1.400 Zeilen)
**Zweck:** Komplette Benutzeroberfläche und Frontend-Logik

**Wichtige Bereiche:**
```javascript
// Zeile 1-50: Imports und Konfiguration
import React, { useState, useEffect } from 'react';
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Zeile 51-150: State-Management
const [knowledgeEntries, setKnowledgeEntries] = useState([]);
const [isAdmin, setIsAdmin] = useState(false);
const [uploadedFiles, setUploadedFiles] = useState([]);

// Zeile 151-300: API-Funktionen
const fetchKnowledgeEntries = async () => {
    // Einträge vom Backend laden
};

const handleLogin = async (e) => {
    // Admin-Anmeldung
};

const handleFileUpload = async (files) => {
    // Datei-Upload
};

// Zeile 301-600: Event-Handler
const handleAddEntry = async (e) => {
    // Neuen Eintrag erstellen
};

const handleDeleteEntry = async (entryId) => {
    // Eintrag löschen
};

// Zeile 601-1000: Hilfsfunktionen
const getCategoryIcon = (category) => {
    // Icon für Kategorie
};

const formatFileSize = (bytes) => {
    // Dateigröße formatieren
};

// Zeile 1001-1400: UI-Komponenten
return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        {/* Header */}
        {/* Stats */}
        {/* Category Filter */}
        {/* Search */}
        {/* Knowledge Entries */}
        {/* Modals */}
    </div>
);
```

**Änderungen vornehmen:**
- **Firmenname:** Zeile ~XXX im Header
- **Farben:** CSS-Klassen ändern
- **Icons:** Zeile ~XXX `getCategoryIcon`
- **UI-Elemente:** JSX-Code anpassen

### 📄 `src/App.css` - Styling (400 Zeilen)
**Zweck:** Alle Styles für die Benutzeroberfläche

**Wichtige Bereiche:**
```css
/* Zeile 1-50: Tailwind CSS Import */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Zeile 51-100: Allgemeine Styles */
.line-clamp-3 {
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

/* Zeile 101-200: Komponenten-Styles */
.knowledge-card {
    @apply bg-white rounded-lg shadow-md p-6 border-l-4 transition-all duration-200;
}

.btn-primary {
    @apply px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700;
}

/* Zeile 201-300: Animationen */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Zeile 301-400: Responsive Design */
@media (max-width: 768px) {
    .container { @apply px-4; }
    .knowledge-card { @apply p-4; }
}
```

**Anpassen:**
- **Hauptfarben:** CSS-Variablen definieren
- **Neue Komponenten:** Neue Klassen hinzufügen
- **Animationen:** Neue Keyframes definieren

### 📄 `src/index.js` - React-Einstiegspunkt
**Zweck:** React-App initialisieren und mounten

```javascript
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

### 📄 `package.json` - Node.js-Abhängigkeiten
**Zweck:** Frontend-Abhängigkeiten und Scripts definieren

```json
{
  "name": "boettcher-wiki-frontend",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  }
}
```

**Neue Pakete hinzufügen:**
```bash
npm install neues-paket
# oder
yarn add neues-paket
```

### 📄 `tailwind.config.js` - Tailwind CSS-Konfiguration
**Zweck:** Tailwind CSS anpassen

```javascript
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'boettcher-blue': '#3B82F6',
        'boettcher-green': '#10B981',
      }
    },
  },
  plugins: [],
}
```

### 📄 `public/index.html` - HTML-Template
**Zweck:** Basis-HTML-Struktur

```html
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Böttcher Wiki</title>
</head>
<body>
    <div id="root"></div>
</body>
</html>
```

---

## 📚 Dokumentations-Dateien (`/docs/`)

### 📄 `API.md` - API-Dokumentation
**Zweck:** Alle API-Endpunkte dokumentieren

**Inhalt:**
- Authentifizierung-Endpunkte
- Wissenseinträge-API
- Datei-Upload-API
- Kategorien-API
- Suche-API
- Fehler-Codes

### 📄 `DEPLOYMENT.md` - Deployment-Anleitung
**Zweck:** Verschiedene Deployment-Optionen erklären

**Inhalt:**
- Lokale Entwicklung
- Docker-Deployment
- Cloud-Deployment (Heroku, Vercel)
- Produktions-Konfiguration
- Monitoring und Backup

### 📄 `CUSTOMIZATION.md` - Anpassungs-Guide
**Zweck:** Wie man das System anpasst

**Inhalt:**
- Design-Anpassungen
- Neue Features hinzufügen
- Sicherheits-Konfiguration
- Workflow-Anpassungen

---

## 🐳 Docker-Dateien

### 📄 `docker-compose.yml` - Multi-Container-Setup
**Zweck:** Alle Services zusammen starten

```yaml
version: '3.8'
services:
  mongodb:        # Datenbank
    image: mongo:6.0
    ports: ["27017:27017"]
  
  backend:        # API-Server
    build: ./backend
    ports: ["8001:8001"]
    depends_on: [mongodb]
  
  frontend:       # React-App
    build: ./frontend
    ports: ["3000:3000"]
    depends_on: [backend]
```

### 📄 `backend/Dockerfile` - Backend-Container
**Zweck:** Python-Backend containerisieren

### 📄 `frontend/Dockerfile` - Frontend-Container
**Zweck:** React-App containerisieren

---

## 🔧 Konfigurations-Dateien

### 📄 `README.md` - Haupt-Dokumentation
**Zweck:** Projekt-Übersicht und Quick-Start

**Inhalt:**
- Features-Liste
- Installation-Anleitung
- Konfiguration
- Anpassungs-Tipps

### 📄 `SETUP-GUIDE.md` - Schritt-für-Schritt Anleitung
**Zweck:** Detaillierte Übernahme-Anleitung

**Inhalt:**
- Vorbereitungen
- Lokale Einrichtung
- GitHub-Upload
- Häufige Probleme

### 📄 `.gitignore` - Git-Ignorierdatei
**Zweck:** Dateien von Git ausschließen

```gitignore
# Abhängigkeiten
node_modules/
__pycache__/

# Umgebungsvariablen
.env

# Build-Dateien
build/
dist/

# Logs
*.log
```

---

## 🎯 Wichtige Änderungspunkte

### 🔐 Sicherheit
1. **Admin-Passwörter:** `backend/server.py` Zeile ~47
2. **JWT-Secret:** `backend/server.py` Zeile ~28
3. **Umgebungsvariablen:** `.env`-Dateien

### 🎨 Design
1. **Firmenname:** `frontend/src/App.js` Header-Bereich
2. **Farben:** `frontend/src/App.css` und `tailwind.config.js`
3. **Logo:** `frontend/public/` und `App.js`

### 🔧 Funktionalität
1. **Neue Kategorien:** `frontend/src/App.js` Icons und Farben
2. **Neue Dateitypen:** `backend/server.py` ALLOWED_EXTENSIONS
3. **Neue API-Endpunkte:** `backend/server.py` nach Zeile 1000

---

## 📞 Nächste Schritte

1. **Dateien herunterladen** und lokal einrichten
2. **Anpassungen vornehmen** (Passwörter, Design)
3. **Zu GitHub hochladen**
4. **Testen und verwenden**
5. **Nach Bedarf erweitern**

**Alle Dateien sind vollständig dokumentiert und anpassbar! 🚀**