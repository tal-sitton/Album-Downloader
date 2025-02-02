from datetime import datetime

from pydantic import model_validator

from models import BasicAlbum, DeezerTrack


class DeezerAlbum(BasicAlbum):
    @model_validator(mode="before")
    @classmethod
    def populate_name(cls, values):
        if values.get("name") is not None:
            return values
        values["name"] = values.get("title")
        return values

    @model_validator(mode="before")
    @classmethod
    def populate_release_date(cls, values):
        if values.get("release_date_epoch") is not None:
            return values
        raw_release_date = values.get("release_date")
        datetime_release = datetime.strptime(raw_release_date, "%Y-%m-%d")

        values["release_date_epoch"] = int(datetime_release.timestamp())
        return values

    @model_validator(mode="before")
    @classmethod
    def populate_image(cls, values):
        if values.get("image") is not None:
            return values
        values["image"] = values.get("cover_xl")
        return values

    @model_validator(mode="before")
    @classmethod
    def populate_url(cls, values):
        if values.get("url") is not None:
            return values
        values["url"] = values.get("link")
        return values

    @model_validator(mode="before")
    @classmethod
    def populate_tracks(cls, values):
        if not isinstance(values.get("tracks"), dict):
            return values
        values["tracks"] = [DeezerTrack(**track, track_number=index + 1) for index, track in
                            enumerate(values["tracks"]['data'])]
        return values

    @model_validator(mode="before")
    @classmethod
    def populate_album_type(cls, values):
        if values.get("album_type") is not None:
            return values
        values["album_type"] = values.get("record_type")
        return values

    @model_validator(mode="before")
    @classmethod
    def populate_explicit(cls, values):
        if values.get("explicit") is not None:
            return values
        values["explicit"] = values.get("explicit_lyrics")
        return values
