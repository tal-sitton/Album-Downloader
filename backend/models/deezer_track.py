from pydantic import model_validator

from models import Track


class DeezerTrack(Track):
    @model_validator(mode="before")
    @classmethod
    def populate_name(cls, values):
        if values.get("name") is not None:
            return values
        values["name"] = values.get("title")
        return values

    @model_validator(mode="before")
    @classmethod
    def populate_artists(cls, values):
        if values.get("artists") is not None:
            return values
        values["artists"] = [values.get("artist").get("name")]
        return values

    @model_validator(mode="before")
    @classmethod
    def populate_track_number(cls, values):
        if values.get("track_number") is not None:
            return values
        values["track_number"] = values.get("track_position")
        return values

    @model_validator(mode="before")
    @classmethod
    def populate_download_url(cls, values):
        if values.get("download_url") is not None:
            return values
        values["download_url"] = values.get("link")
        return values
