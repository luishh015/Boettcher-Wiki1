# 🚀 Schritt-für-Schritt: Böttcher Wiki zu GitHub übertragen

## 📋 Vorbereitungen

### 1. Erforderliche Tools installieren
```bash
# Git installieren (falls nicht vorhanden)
# Windows: https://git-scm.com/download/win
# macOS: brew install git
# Linux: sudo apt install git

# Node.js installieren (Version 16+)
# https://nodejs.org/en/download/

# Python installieren (Version 3.8+)
# https://www.python.org/downloads/

# MongoDB installieren
# https://www.mongodb.com/try/download/community
```

### 2. GitHub-Account erstellen
- Gehen Sie zu https://github.com
- Erstellen Sie einen Account (falls noch nicht vorhanden)
- Erstellen Sie ein neues Repository namens "boettcher-wiki"

## 📦 Dateien herunterladen

### Option A: ZIP-Download (Einfachster Weg)
1. Erstellen Sie einen Ordner `boettcher-wiki` auf Ihrem Computer
2. Kopieren Sie alle Dateien aus diesem System in den Ordner

### Option B: Dateien manuell erstellen
Erstellen Sie die folgende Ordnerstruktur:

```
boettcher-wiki/
├── README.md
├── .gitignore
├── docker-compose.yml
├── backend/
│   ├── server.py
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.js
│   │   ├── App.css
│   │   └── index.js
│   ├── public/
│   │   └── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── .env.example
│   └── Dockerfile
└── docs/
    ├── API.md
    ├── DEPLOYMENT.md
    └── CUSTOMIZATION.md
```

## 🔧 Lokale Einrichtung

### 1. Backend konfigurieren
```bash
cd boettcher-wiki/backend

# Virtuelle Umgebung erstellen (empfohlen)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate     # Windows

# Abhängigkeiten installieren
pip install -r requirements.txt

# Umgebungsvariablen konfigurieren
cp .env.example .env
# Bearbeiten Sie die .env-Datei mit Ihren Werten
```

### 2. Frontend konfigurieren
```bash
cd ../frontend

# Abhängigkeiten installieren
npm install

# Umgebungsvariablen konfigurieren
cp .env.example .env
# Bearbeiten Sie die .env-Datei
```

### 3. MongoDB starten
```bash
# MongoDB-Service starten
# Windows: MongoDB Service starten
# macOS/Linux: 
sudo systemctl start mongod
# oder
mongod
```

## 🚀 Anwendung testen

### 1. Backend starten
```bash
cd backend
python server.py
```
➡️ Backend läuft auf http://localhost:8001

### 2. Frontend starten (neues Terminal)
```bash
cd frontend
npm start
```
➡️ Frontend läuft auf http://localhost:3000

### 3. Testen
- Öffnen Sie http://localhost:3000
- Klicken Sie auf "Admin Login"
- Melden Sie sich mit `admin` / `boettcher2024` an
- Testen Sie das Hinzufügen von Einträgen

## 📤 Zu GitHub hochladen

### 1. Git-Repository initialisieren
```bash
cd boettcher-wiki
git init
git add .
git commit -m "Initial commit - Böttcher Wiki"
```

### 2. Mit GitHub verbinden
```bash
# Remote-Repository hinzufügen (ersetzen Sie USERNAME)
git remote add origin https://github.com/USERNAME/boettcher-wiki.git

# Zum GitHub hochladen
git branch -M main
git push -u origin main
```

## 🔒 Sicherheit konfigurieren

### 1. Passwörter ändern
```python
# backend/server.py - Zeile ~47
ADMIN_CREDENTIALS = {
    "ihr_admin": "ihr_sicheres_passwort",
    "ihr_manager": "ihr_manager_passwort"
}
```

### 2. Secret Key ändern
```python
# backend/server.py - Zeile ~28
SECRET_KEY = "ihr-super-geheimer-schlüssel-hier"
```

### 3. .env-Dateien konfigurieren
```bash
# backend/.env
MONGO_URL=mongodb://localhost:27017/
SECRET_KEY=ihr-production-secret-key

# frontend/.env
REACT_APP_BACKEND_URL=http://localhost:8001
```

## 🎨 Anpassungen vornehmen

### 1. Firmenname ändern
```javascript
// frontend/src/App.js - Zeile ~XXX
<h1 className="text-3xl font-bold text-gray-800">Ihr Firmenname</h1>
<p className="text-blue-600 font-medium">Ihre Beschreibung</p>
```

### 2. Farben anpassen
```css
/* frontend/src/App.css */
/* Suchen Sie nach Farbdefinitionen und passen Sie sie an */
```

### 3. Logo hinzufügen
```javascript
// frontend/src/App.js - Header-Bereich
<img src="/logo.svg" alt="Ihr Logo" className="w-8 h-8" />
```

## 🐳 Docker-Deployment (Optional)

### 1. Mit Docker Compose
```bash
# Alle Services starten
docker-compose up -d

# Logs anschauen
docker-compose logs -f

# Services stoppen
docker-compose down
```

## 📝 Änderungen vornehmen

### 1. Neue Features hinzufügen
```bash
# Neue Branch erstellen
git checkout -b neue-feature

# Änderungen vornehmen
# ...

# Änderungen committen
git add .
git commit -m "Neue Feature hinzugefügt"

# Zu GitHub pushen
git push origin neue-feature
```

### 2. Änderungen in main branch übernehmen
```bash
git checkout main
git merge neue-feature
git push origin main
```

## 🔧 Häufige Probleme lösen

### Problem: MongoDB-Verbindung fehlschlägt
**Lösung:**
```bash
# MongoDB-Status prüfen
sudo systemctl status mongod

# MongoDB starten
sudo systemctl start mongod

# Oder manuell starten
mongod --dbpath /data/db
```

### Problem: Port bereits in Verwendung
**Lösung:**
```bash
# Port 8001 prüfen
lsof -i :8001

# Prozess beenden
kill -9 <PID>
```

### Problem: npm install schlägt fehl
**Lösung:**
```bash
# Cache leeren
npm cache clean --force

# node_modules löschen
rm -rf node_modules package-lock.json

# Neu installieren
npm install
```

## 📊 Erweiterte Konfiguration

### 1. Produktionsumgebung
```bash
# Backend für Produktion
export NODE_ENV=production
export MONGO_URL=mongodb://production-server:27017/

# Frontend für Produktion
npm run build
```

### 2. SSL-Zertifikate
```bash
# Let's Encrypt installieren
sudo apt install certbot

# Zertifikat erstellen
sudo certbot certonly --standalone -d ihre-domain.com
```

### 3. Reverse Proxy (Nginx)
```nginx
# /etc/nginx/sites-available/boettcher-wiki
server {
    listen 80;
    server_name ihre-domain.com;
    
    location / {
        proxy_pass http://localhost:3000;
    }
    
    location /api {
        proxy_pass http://localhost:8001;
    }
}
```

## ✅ Checkliste

- [ ] Repository auf GitHub erstellt
- [ ] Alle Dateien hochgeladen
- [ ] Lokale Entwicklung funktioniert
- [ ] Admin-Zugangsdaten geändert
- [ ] .env-Dateien konfiguriert
- [ ] Erste Einträge erstellt
- [ ] Datei-Upload getestet
- [ ] Kategorien hinzugefügt
- [ ] Design angepasst
- [ ] Dokumentation gelesen

## 🎯 Nächste Schritte

1. **Inhalte hinzufügen**: Erstellen Sie Ihre ersten Wissenseinträge
2. **Team schulen**: Zeigen Sie Kollegen die Nutzung
3. **Backups einrichten**: Regelmäßige Datensicherung
4. **Monitoring**: Logs und Performance überwachen
5. **Weiterentwicklung**: Neue Features nach Bedarf hinzufügen

---

## 🆘 Hilfe benötigt?

- **GitHub Issues**: Erstellen Sie ein Issue in Ihrem Repository
- **Dokumentation**: Lesen Sie die Dateien im `docs/` Ordner
- **Community**: Fragen Sie in Developer-Foren

**Viel Erfolg mit Ihrem Böttcher Wiki! 🚴‍♂️**