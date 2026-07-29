# Hollywood Closet

Ein glamouröser Web-Kleiderschrank-Manager im Hollywood-Stil. Benutzer registrieren sich,
laden Kleidungsstücke mit Bildern und Kategorien hoch, durchstöbern ihre Garderobe in
einer eleganten Galerie und kombinieren im Outfit-Creator Einzelteile zu gespeicherten Outfits.

**Tech-Stack:** Python 3.11+, FastAPI, SQLite via SQLAlchemy, Vite + React + TypeScript

---

## Features

- **Benutzerkonten:** Registrierung und Login mit E-Mail und Passwort
- **Digitale Garderobe:** Kleidungsstücke mit Bild-Upload, Kategorie und Notizen verwalten
- **Kategorie-Filter:** Galerie-Ansicht filterbar nach Kategorien (Oberteile, Hosen, Kleider, Schuhe, Accessoires)
- **Outfit-Creator:** Kleidungsstücke zu Outfits kombinieren und speichern
- **Outfit-Verwaltung:** Gespeicherte Outfits anzeigen, bearbeiten und löschen
- **Konto-Löschung:** Vollständige Datenlöschung inklusive aller hochgeladenen Bilder

---

## Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --port 8000
```

Der Server startet unter `http://localhost:8000`. Die SQLite-Datenbank `dev.db`
wird automatisch erstellt. Das Upload-Verzeichnis `uploads/` wird ebenfalls
angelegt.

### Frontend

```bash
cd frontend
npm ci
npm run dev
```

Das Frontend startet unter `http://localhost:5173`. Der Vite-Dev-Server
proxied API-Anfragen automatisch an den Backend-Server (`localhost:8000`).

### Production Build

```bash
cd frontend
npm run build
```

Das gebaute Frontend wird in `frontend/dist/` abgelegt. Der Backend-Server
serviert es dann automatisch unter `/`.

---

## How to Use

1. **Registrierung:** Auf der Startseite auf "Jetzt loslegen" klicken, E-Mail
   und Passwort eingeben.
2. **Login:** Mit den Zugangsdaten anmelden.
3. **Garderobe:** Kleidungsstücke mit Bild, Name, Kategorie und optionaler Notiz
   hochladen. Die Galerie zeigt alle Stücke, filterbar nach Kategorie.
4. **Outfits:** Im Outfit-Creator Kleidungsstücke auswählen, kombinieren und als
   Outfit speichern. Gespeicherte Outfits können bearbeitet oder gelöscht werden.

---

## API Endpoints

### Auth (`/api/auth`)

| Methode | Pfad        | Body                              | Response        | Status |
|---------|-------------|-----------------------------------|-----------------|--------|
| POST    | `/register` | `{"email": "...", "password": "..."}` | `TokenResponse` | 201    |
| POST    | `/login`    | `{"email": "...", "password": "..."}` | `TokenResponse` | 200    |
| GET     | `/me`       | –                                 | `UserResponse`  | 200    |
| DELETE  | `/account`  | –                                 | –               | 204    |

### Wardrobe (`/api/wardrobe`)

| Methode | Pfad      | Body / Params                                      | Response              | Status |
|---------|-----------|---------------------------------------------------|-----------------------|--------|
| POST    | `/`       | `multipart: name, category, image, note`          | `ClothingItemResponse`| 201    |
| GET     | `/`       | `?category=...` (optional)                        | `[ClothingItemResponse]` | 200 |
| GET     | `/{id}`   | –                                                 | `ClothingItemResponse`| 200    |
| PUT     | `/{id}`   | `ClothingItemCreate`                              | `ClothingItemResponse`| 200    |
| DELETE  | `/{id}`   | –                                                 | –                     | 204    |

### Outfits (`/api/outfits`)

| Methode | Pfad      | Body                                              | Response          | Status |
|---------|-----------|---------------------------------------------------|-------------------|--------|
| POST    | `/`       | `{"name": "...", "item_ids": [...]}`              | `OutfitResponse`  | 201    |
| GET     | `/`       | –                                                 | `[OutfitResponse]`| 200    |
| GET     | `/{id}`   | –                                                 | `OutfitResponse`  | 200    |
| PUT     | `/{id}`   | `{"name": "...", "item_ids": [...]}`              | `OutfitResponse`  | 200    |
| DELETE  | `/{id}`   | –                                                 | –                 | 204    |

### Health

| Methode | Pfad          | Response                    |
|---------|---------------|-----------------------------|
| GET     | `/api/health` | `{"status": "ok"}`          |

---

## Environment Variables

| Variable     | Default (Dev)       | Beschreibung                     |
|-------------|---------------------|----------------------------------|
| `DB_PATH`   | `backend/dev.db`    | Pfad zur SQLite-Datenbank       |
| `JWT_SECRET`| (dev-fallback)      | Geheimnis für JWT-Signierung    |
| `JWT_EXPIRY`| `86400`             | JWT-Ablaufzeit in Sekunden      |

---

## License

Proprietary
