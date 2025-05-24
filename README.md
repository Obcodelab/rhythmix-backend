# Rhythmix Backend

A music player backend built with FastAPI, SQLModel, and Python — supporting track uploads with metadata, user authentication, playlists, play history, and AI-driven recommendations.

## Features

- User registration, authentication (JWT)

- Track upload with metadata: title, artist, genre, tags, mood, file upload

- Playlist management (create, update, delete, add/remove tracks)

- Play history tracking per user

- AI-based track recommendations using listening history & metadata

- Search tracks by title, artist, genre, tags, mood with pagination

- Secure password hashing and authorization

- Local file storage for uploads (can be extended to cloud storage)

## Tech Stack

- Python 3.12

- FastAPI (web framework)

- SQLModel (ORM, built on SQLAlchemy)

- SQLite (default database, easy to switch to PostgreSQL)

- JWT for authentication

- Pydantic for data validation

- Uvicorn (ASGI server)

## Getting Started

### Prerequisites

- Python 3.10+ installed

- Git installed

### Installation

1. Clone the repo:

```bash
git clone https://github.com/Obcodelab/rhythmix-backend.git
cd rhythmix-backend
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate # On Windows use `venv\Scripts\activate`
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a .env file in the root with:

```bash
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite:///./rhythmix.db
# Replace SECRET_KEY with a secure random string.
```

5. Run the server:

```bash
uvicorn app.main:app --reload
# Uvicorn running on http://127.0.0.1:8000
```

## API Endpoints

### Auth

- POST /auth/signup — Register new user

- POST /auth/login — Login and get JWT token

### Tracks

- POST /tracks/upload — Upload track with metadata and file

- GET /tracks/search — Search tracks with filters and pagination

- GET /tracks/recommendations — Get AI-driven track recommendations

### Playlists

- GET /playlists — List user’s playlists

- POST /playlists — Create playlist

- PUT /playlists/{id} — Update playlist (including tracks)

- DELETE /playlists/{id} — Delete playlist

### Play History

- POST /{user_id}/play — Log track play for user

## Usage

- Authenticate using /auth/login to receive JWT token

- Include Authorization: Bearer <token> header on all protected endpoints

- Upload audio files using multipart form data

- Use query parameters on /tracks/search for filtering (title, artist, genre, tags, mood)

- Paginate search results using skip and limit parameters

## Video usage

https://github.com/user-attachments/assets/e7e58154-90fe-452e-9fff-a48e11c8e41c

## Project Structure

```bash
app/
├── core/ # Security, dependencies, config
├── models/ # SQLModel database models
├── routes/ # API routers
├── db.py # Database connection & initialization
└── main.py # FastAPI app instance
```

## Testing

Tests are to be implemented (or extend this section if you have tests).

## Future Improvements

- Move file storage to cloud (AWS S3, Cloudinary)

- Enhance AI recommendation with collaborative filtering

- Add user roles and permissions

- Add unit and integration tests

- Support streaming and audio metadata extraction

- Frontend integration (React/Vue/Next.js)

## License

MIT License © Obcodelab
