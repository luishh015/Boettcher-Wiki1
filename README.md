# Böttcher Wiki - Fahrradmanufaktur Wissensdatenbank

Eine moderne, benutzerfreundliche Wissensdatenbank für Fahrradmanufakturen mit Admin-Verwaltung, Kategorien-System und Datei-Anhängen.

## 🎯 Features

- **Admin-Authentifizierung** - Sichere Anmeldung für Verwaltung
- **Kategorien-System** - Organisierte Wissensstruktur
- **Datei-Anhänge** - Bilder, PDFs, Dokumente zu Einträgen
- **Intelligente Suche** - Durchsuchung von Fragen, Antworten und Tags
- **Drag & Drop Upload** - Einfaches Hochladen von Dateien
- **Responsive Design** - Funktioniert auf Desktop und Mobile
- **Thumbnail-Generierung** - Automatische Bildvorschau

## 🚀 Quick Start

### Voraussetzungen
- Python 3.8+
- Node.js 16+
- MongoDB
- Git

### Installation

1. **Repository klonen:**
```bash
git clone https://github.com/IhrUsername/boettcher-wiki.git
cd boettcher-wiki
```

2. **Backend Setup:**
```bash
cd backend
pip install -r requirements.txt
```

3. **Frontend Setup:**
```bash
cd ../frontend
npm install
```

4. **Umgebungsvariablen konfigurieren:**
```bash
# Backend .env
cp backend/.env.example backend/.env

# Frontend .env
cp frontend/.env.example frontend/.env
```

5. **MongoDB starten:**
```bash
mongod
```

6. **Anwendung starten:**
```bash
# Backend (Terminal 1)
cd backend
python server.py

# Frontend (Terminal 2)
cd frontend
npm start
```

## 📁 Projektstruktur

```
boettcher-wiki/
├── README.md                 # Diese Datei
├── .gitignore               # Git-Ignorierdatei
├── docker-compose.yml       # Docker-Konfiguration
├── backend/                 # FastAPI Backend
│   ├── server.py           # Haupt-API-Server
│   ├── requirements.txt    # Python-Abhängigkeiten
│   ├── .env               # Umgebungsvariablen
│   └── .env.example       # Beispiel-Umgebungsvariablen
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── App.js         # Haupt-React-Komponente
│   │   ├── App.css        # Styling
│   │   └── index.js       # React-Einstiegspunkt
│   ├── public/
│   │   └── index.html     # HTML-Template
│   ├── package.json       # Node.js-Abhängigkeiten
│   ├── tailwind.config.js # Tailwind CSS-Konfiguration
│   ├── .env              # Frontend-Umgebungsvariablen
│   └── .env.example      # Beispiel-Umgebungsvariablen
└── docs/                  # Dokumentation
    ├── API.md            # API-Dokumentation
    ├── DEPLOYMENT.md     # Deployment-Anleitung
    └── CUSTOMIZATION.md  # Anpassungs-Guide
```

## 🔧 Konfiguration

### Backend (.env)
```env
MONGO_URL=mongodb://localhost:27017/
SECRET_KEY=your-secret-key-here
```

### Frontend (.env)
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

## 👨‍💼 Admin-Zugangsdaten

**Standard-Admin-Accounts:**
- Username: `admin`, Passwort: `boettcher2024`
- Username: `manager`, Passwort: `wiki2024`

> ⚠️ **Sicherheitshinweis:** Ändern Sie diese Zugangsdaten in der Produktion!

## 🎨 Anpassung

### Neue Kategorien hinzufügen
1. Als Admin anmelden
2. "Neue Kategorie hinzufügen" klicken
3. Name, Icon und Farbe wählen

### Styling anpassen
- Hauptstyles in `frontend/src/App.css`
- Tailwind-Konfiguration in `frontend/tailwind.config.js`

### API erweitern
- Neue Endpunkte in `backend/server.py` hinzufügen
- Pydantic-Modelle für Datenvalidierung verwenden

## 🔒 Sicherheit

- JWT-Token für Authentifizierung
- Datei-Upload-Validierung
- Admin-only Endpunkte
- CORS-Konfiguration

## 📚 Unterstützte Dateiformate

- **Bilder:** JPG, PNG, GIF, BMP, WebP
- **Dokumente:** PDF, DOC, DOCX, TXT, RTF
- **Tabellen:** XLS, XLSX, CSV
- **Präsentationen:** PPT, PPTX
- **Archive:** ZIP, RAR, 7Z

## 🛠️ Entwicklung

### Backend erweitern
```python
# Neue API-Route hinzufügen
@app.get("/api/my-new-endpoint")
async def my_new_endpoint():
    return {"message": "Hello World"}
```

### Frontend erweitern
```javascript
// Neue Komponente hinzufügen
const MyNewComponent = () => {
    return <div>Meine neue Komponente</div>;
};
```

## 🐛 Fehlerbehebung

### Häufige Probleme:
1. **MongoDB-Verbindungsfehler:** Überprüfen Sie, ob MongoDB läuft
2. **CORS-Fehler:** Prüfen Sie die Backend-URL im Frontend
3. **Upload-Fehler:** Überprüfen Sie Dateigröße und -format

### Logs überprüfen:
```bash
# Backend-Logs
tail -f backend/app.log

# Frontend-Logs
# Siehe Browser-Konsole
```

## 🤝 Beitragen

1. Fork das Repository
2. Erstellen Sie einen Feature-Branch
3. Commiten Sie Ihre Änderungen
4. Pushen Sie zum Branch
5. Erstellen Sie eine Pull Request

## 📝 Lizenz

MIT License - Siehe LICENSE-Datei für Details

## 📞 Support

Bei Fragen oder Problemen:
- Erstellen Sie ein Issue auf GitHub
- Kontaktieren Sie den Entwickler

---

**Entwickelt für Böttcher Fahrradmanufaktur** 🚴‍♂️