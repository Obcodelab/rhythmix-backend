from uuid import UUID

from sqlmodel import Field, SQLModel


class PlaylistTrackLink(SQLModel, table=True):
    playlist_id: UUID = Field(foreign_key="playlist.id", primary_key=True)
    track_id: UUID = Field(foreign_key="track.id", primary_key=True)
