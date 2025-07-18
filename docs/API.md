# API-Dokumentation

## Authentifizierung

### POST /api/admin/login
Admin-Anmeldung

**Request:**
```json
{
  "username": "admin",
  "password": "boettcher2024"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "username": "admin"
}
```

### GET /api/admin/verify
Token-Verifizierung

**Headers:**
```
Authorization: Bearer <token>
```

## Wissenseinträge

### GET /api/knowledge
Alle Wissenseinträge abrufen

**Parameter:**
- `category` (optional): Kategorie-Filter
- `limit` (optional): Anzahl der Einträge (default: 100)

### POST /api/knowledge
Neuen Eintrag erstellen (Admin-only)

**Request:**
```json
{
  "question": "Wie funktioniert X?",
  "answer": "Schritt-für-Schritt Anleitung...",
  "category": "IT-Support",
  "tags": ["tag1", "tag2"],
  "attachments": []
}
```

### PUT /api/knowledge/{id}
Eintrag aktualisieren (Admin-only)

### DELETE /api/knowledge/{id}
Eintrag löschen (Admin-only)

## Datei-Upload

### POST /api/upload
Datei hochladen (Admin-only)

**Request:** Multipart/form-data
```
file: <binary_data>
```

**Response:**
```json
{
  "id": "uuid",
  "filename": "example.pdf",
  "file_type": "documents",
  "file_size": 1024,
  "content_type": "application/pdf",
  "file_data": "base64_encoded_data",
  "thumbnail": "base64_encoded_thumbnail",
  "uploaded_at": "2024-01-01T00:00:00"
}
```

### GET /api/files/{file_id}/download
Datei herunterladen

## Kategorien

### GET /api/categories
Alle Kategorien abrufen

### POST /api/categories
Neue Kategorie erstellen (Admin-only)

**Request:**
```json
{
  "name": "Neue Kategorie",
  "icon": "🆕",
  "color": "bg-blue-100 text-blue-800 border-blue-500",
  "description": "Beschreibung der Kategorie"
}
```

### DELETE /api/categories/{id}
Kategorie löschen (Admin-only)

## Suche

### POST /api/search
Wissensdatenbank durchsuchen

**Request:**
```json
{
  "query": "Suchbegriff",
  "category": "IT-Support"
}
```

## Statistiken

### GET /api/stats
Statistiken abrufen

**Response:**
```json
{
  "total_entries": 25,
  "categories_count": 5,
  "total_attachments": 12
}
```

## Fehler-Codes

- `200` - Erfolg
- `400` - Ungültige Anfrage
- `401` - Nicht authentifiziert
- `403` - Nicht autorisiert
- `404` - Nicht gefunden
- `413` - Datei zu groß
- `500` - Server-Fehler