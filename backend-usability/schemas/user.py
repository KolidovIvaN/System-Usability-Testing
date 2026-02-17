from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    email: EmailStr = Field(title="") 
    password: str = Field(title="", min_length=4, max_length=50)
    first_name: str = Field(title="")
    last_name: str = Field(title="")
    

class UserLogin(BaseModel):
    email: EmailStr = Field(title="")
    password: str = Field(title="")