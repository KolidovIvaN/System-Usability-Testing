from pydantic import BaseModel, Field


class UserToken(BaseModel):
    refresh_token: str = Field(title="")