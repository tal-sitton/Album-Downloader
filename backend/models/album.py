from typing import Optional

from pydantic import BaseModel

from models import Artist, Track


class BasicAlbum(BaseModel):
    name: Optional[str] = None
    id: Optional[str | int] = None
    artist: Optional[Artist] = None
    release_date_epoch: Optional[int] = None
    image: Optional[str] = None
    url: Optional[str] = None
    tracks: Optional[list[Track] | dict] = None
    album_type: Optional[str] = None
    explicit: Optional[bool] = None

    @property
    def total_tracks(self) -> int:
        return len(self.tracks) if self.tracks else -1
