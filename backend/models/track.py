from typing import Optional

from pydantic import BaseModel


class Track(BaseModel):
    id: Optional[str | int] = None
    name: Optional[str] = None
    artists: Optional[list[str]] = None
    track_number: Optional[int] = None
    duration: Optional[int] = None
    download_url: Optional[str] = None
