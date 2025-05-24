import os
import shutil
from typing import List, Optional, Set
from uuid import UUID, uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy import or_
from sqlmodel import Session, func, select

from app.core.security import get_current_user, get_session
from app.models.play_history import PlayHistory
from app.models.track import PaginatedTracks, Track, TrackRead
from app.models.user import User

router = APIRouter()

UPLOAD_DIR = "uploads/"


@router.post("/upload")
def upload_track(
    title: str = Form(...),
    artist: str = Form(None),
    genre: str = Form(None),
    tags: str = Form(None),
    mood: str = Form(None),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    file_extension = os.path.splitext(file.filename)[1]
    file_name = f"{uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, file_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_url = f"/{file_path}"

    new_track = Track(
        title=title,
        artist=artist,
        genre=genre,
        tags=tags,
        mood=mood,
        file_url=file_url,
        uploaded_by=current_user.id,
    )
    session.add(new_track)
    session.commit()
    session.refresh(new_track)

    return {"message": "Track uploaded successfully", "track": new_track}


@router.get("/search", response_model=PaginatedTracks)
def search_tracks(
    title: Optional[str] = Query(None, description="Filter by track title"),
    artist: Optional[str] = Query(None, description="Filter by artist"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    tags: Optional[str] = Query(None, description="Filter by tags(comma-separated)"),
    mood: Optional[str] = Query(None, description="Filter by mood"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        10, ge=1, le=100, description="Maximum number of records to return"
    ),
    session: Session = Depends(get_session),
):
    base_query = select(Track)

    if title:
        base_query = base_query.where(Track.title.ilike(f"%{title}%"))
    if artist:
        base_query = base_query.where(Track.artist.ilike(f"%{artist}%"))
    if genre:
        base_query = base_query.where(Track.genre.ilike(f"%{genre}%"))
    if mood:
        base_query = base_query.where(Track.mood.ilike(f"%{mood}%"))
    if tags:
        for tag in tags.split(","):
            tag = tag.strip()
            base_query = base_query.where(Track.tags.ilike(f"%{tag}%"))

    count_query = select(func.count()).select_from(Track)

    if title:
        count_query = count_query.where(Track.title.ilike(f"%{title}%"))
    if artist:
        count_query = count_query.where(Track.artist.ilike(f"%{artist}%"))
    if genre:
        count_query = count_query.where(Track.genre.ilike(f"%{genre}%"))
    if mood:
        count_query = count_query.where(Track.mood.ilike(f"%{mood}%"))
    if tags:
        for tag in tags.split(","):
            tag = tag.strip()
            count_query = count_query.where(Track.tags.ilike(f"%{tag}%"))

    total = session.exec(count_query).one()
    results = session.exec(base_query.offset(skip).limit(limit)).all()
    page = (skip // limit) + 1

    return PaginatedTracks(
        total=total,
        page=page,
        size=limit,
        items=results,
    )


@router.post("/{track_id}/play", status_code=status.HTTP_201_CREATED)
def record_play(
    track_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    track = session.get(Track, track_id)
    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Track not found",
        )

    play_history = PlayHistory(user_id=current_user.id, track_id=track.id)
    session.add(play_history)
    session.commit()

    return {"message": "Play recorded successfully", "play_history": play_history}


@router.get("/recommendations", response_model=List[TrackRead])
def get_recommendations(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    limit: int = 10,
):
    recent_plays = session.exec(
        select(PlayHistory)
        .where(PlayHistory.user_id == current_user.id)
        .order_by(PlayHistory.played_at.desc())
        .limit(20)
    ).all()
    if not recent_plays:
        return session.exec(select(Track).limit(limit)).all()

    genres: Set[str] = set()
    tags: Set[str] = set()
    for play in recent_plays:
        if play.track.genre:
            genres.add(play.track.genre.lower())
        if play.track.tags:
            tags.update(tag.strip().lower() for tag in play.track.tags.split(","))

    played_track_ids = {play.track_id for play in recent_plays}

    tag_conditions = [Track.tags.ilike(f"%{tag}%") for tag in tags]

    query = (
        select(Track)
        .where((Track.genre.in_(genres)) | or_(*tag_conditions))
        .where(Track.id.not_in(played_track_ids))
        .limit(limit)
    )

    recommendations = session.exec(query).all()
    return recommendations
