from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel

from app.models.playlist_track import PlaylistTrackLink

if TYPE_CHECKING:
    from app.models.track import Track
    from app.models.user import User


class Playlist(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    owner_id: UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    owner: Optional["User"] = Relationship(back_populates="playlists")
    tracks: List["Track"] = Relationship(
        back_populates="playlists", link_model=PlaylistTrackLink
    )

    @property
    def track_ids(self) -> List[UUID]:
        return [track.id for track in self.tracks] if self.tracks else []


class PlaylistCreate(BaseModel):
    name: str
    description: Optional[str] = None
    track_ids: List[UUID] = []


class PlaylistRead(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    owner_id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    track_ids: List[UUID]

    class Config:
        from_attributes = True
