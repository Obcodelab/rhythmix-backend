from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel

from app.models.playlist_track import PlaylistTrackLink

if TYPE_CHECKING:
    from app.models.play_history import PlayHistory
    from app.models.playlist import Playlist


class Track(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    title: str = Field(index=True, nullable=False)
    artist: Optional[str] = Field(default=None, index=True)
    genre: Optional[str] = Field(default=None, index=True)
    tags: Optional[str] = Field(default=None, index=True)
    mood: Optional[str] = Field(default=None, index=True)
    file_url: str = Field(nullable=False)
    cover_url: Optional[str] = Field(default=None)
    uploaded_by: UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    playlists: List["Playlist"] = Relationship(
        back_populates="tracks", link_model=PlaylistTrackLink
    )
    play_histories: List["PlayHistory"] = Relationship(back_populates="track")


class TrackRead(BaseModel):
    id: UUID
    title: str
    artist: Optional[str]
    genre: Optional[str]
    tags: Optional[str]
    mood: Optional[str]
    file_url: str
    cover_url: Optional[str]
    uploaded_by: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class PaginatedTracks(BaseModel):
    total: int
    page: int
    size: int
    items: List[TrackRead]
