from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.security import get_current_user, get_session
from app.models.playlist import Playlist, PlaylistCreate, PlaylistRead
from app.models.track import Track
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=PlaylistRead, status_code=status.HTTP_201_CREATED)
def create_playlist(
    playlist_in: PlaylistCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    tracks = session.exec(
        select(Track).where(Track.id.in_(playlist_in.track_ids))
    ).all()
    if len(tracks) != len(set(playlist_in.track_ids)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Some tracks not found",
        )
    playlist = Playlist(
        name=playlist_in.name,
        description=playlist_in.description,
        owner_id=current_user.id,
        tracks=tracks,
    )
    session.add(playlist)
    session.commit()
    session.refresh(playlist)
    return playlist


@router.get("/", response_model=List[PlaylistRead])
def get_playlists(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    playlists = session.exec(
        select(Playlist).where(Playlist.owner_id == current_user.id)
    ).all()
    return playlists


@router.get("/{playlist_id}", response_model=PlaylistRead)
def get_playlist(
    playlist_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    playlist = session.get(Playlist, playlist_id)
    if not playlist or playlist.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found",
        )
    return playlist


@router.put("/{playlist_id}", response_model=PlaylistRead)
def update_playlist(
    playlist_id: UUID,
    playlist_in: PlaylistCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    playlist = session.get(Playlist, playlist_id)
    if not playlist or playlist.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found",
        )
    tracks = session.exec(
        select(Track).where(Track.id.in_(playlist_in.track_ids))
    ).all()
    if len(tracks) != len(set(playlist_in.track_ids)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Some tracks not found",
        )
    playlist.name = playlist_in.name
    playlist.description = playlist_in.description
    playlist.tracks = tracks

    session.add(playlist)
    session.commit()
    session.refresh(playlist)
    return playlist


@router.delete("/{playlist_id}", status_code=status.HTTP_200_OK)
def delete_playlist(
    playlist_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    playlist = session.get(Playlist, playlist_id)
    if not playlist or playlist.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found",
        )
    session.delete(playlist)
    session.commit()
    return {"detail": "Playlist deleted successfully"}
