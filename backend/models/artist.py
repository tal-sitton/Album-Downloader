from typing import Optional

from pydantic import BaseModel, model_validator


class Artist(BaseModel):
    name: str = None
    id: str | int
    image: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def populate_image(cls, values):
        if values.get("image") is not None:
            return values
        values["image"] = values["picture_xl"]
        return values
