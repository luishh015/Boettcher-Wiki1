# Deployment-Anleitung

## 🚀 Lokale Entwicklung

### 1. Repository klonen
```bash
git clone https://github.com/IhrUsername/boettcher-wiki.git
cd boettcher-wiki
```

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# .env-Datei bearbeiten
python server.py
```

### 3. Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env
# .env-Datei bearbeiten
npm start
```

## 🐳 Docker Deployment

### 1. Mit Docker Compose
```bash
# Alle Services starten
docker-compose up -d

# Logs anzeigen
docker-compose logs -f

# Services stoppen
docker-compose down
```

### 2. Einzelne Container
```bash
# Backend
docker build -t boettcher-wiki-backend ./backend
docker run -p 8001:8001 boettcher-wiki-backend

# Frontend
docker build -t boettcher-wiki-frontend ./frontend
docker run -p 3000:3000 boettcher-wiki-frontend
```

## ☁️ Cloud Deployment

### Heroku
```bash
# Heroku CLI installieren
heroku create boettcher-wiki
heroku addons:create mongolab:sandbox
heroku config:set SECRET_KEY=your-secret-key
git push heroku main
```

### Vercel (Frontend)
```bash
# Vercel CLI installieren
vercel --prod
```

### Railway
```bash
# Railway CLI installieren
railway login
railway init
railway up
```

## 🔧 Produktions-Konfiguration

### Backend (.env)
```env
MONGO_URL=mongodb://production-db:27017/
SECRET_KEY=super-secret-production-key
HOST=0.0.0.0
PORT=8001
```

### Frontend (.env)
```env
REACT_APP_BACKEND_URL=https://your-api-domain.com
REACT_APP_DEBUG=false
```

### Nginx-Konfiguration
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 Monitoring

### Logs
```bash
# Backend-Logs
tail -f backend/app.log

# Frontend-Logs (Browser-Konsole)
# Oder mit Docker
docker logs boettcher-wiki-frontend
```

### Health-Checks
```bash
# Backend Health
curl http://localhost:8001/api/health

# Frontend Health
curl http://localhost:3000
```

## 🔒 Sicherheit

### SSL-Zertifikat (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Firewall
```bash
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 22
sudo ufw enable
```

### Backup
```bash
# MongoDB-Backup
mongodump --out /backup/boettcher-wiki-$(date +%Y%m%d)

# Restore
mongorestore /backup/boettcher-wiki-20240101
```

## 📈 Skalierung

### Load Balancer
```yaml
# docker-compose.yml
version: '3.8'
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend1
      - backend2
  
  backend1:
    build: ./backend
    environment:
      - MONGO_URL=mongodb://mongodb:27017/
  
  backend2:
    build: ./backend
    environment:
      - MONGO_URL=mongodb://mongodb:27017/
```

### Auto-Updates
```bash
# Watchtower für Docker
docker run -d \
  --name watchtower \
  -v /var/run/docker.sock:/var/run/docker.sock \
  containrrr/watchtower
```