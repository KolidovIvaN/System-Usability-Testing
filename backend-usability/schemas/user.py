from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    email: EmailStr = Field(title="") 
    password: str = Field(title="", min_length=4, max_length=20)
    first_name: str = Field(title="")
    last_name: str = Field(title="")