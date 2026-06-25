# schemas for api request and response data 

from pydantic import BaseModel , ConfigDict , Field , EmailStr
from datetime import datetime

# User Schamas --------------------------------------------
class UserBase(BaseModel):
    username:str = Field(min_length=1, max_length=50)
    email:EmailStr = Field(max_length=120)

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    image_file : str | None
    image_path : str

class UserUpdate(BaseModel):
    username:str | None = Field(default=None,min_length=1, max_length=50)
    email:EmailStr | None = Field(default=None,max_length=120)
    image_file : str | None = Field(default=None, min_length=1, max_length=200)

# Post Schamas --------------------------------------------
class PostBase(BaseModel):
    title:str = Field(min_length=1, max_length=100)
    content:str = Field(min_length=10)

class PostCreate(PostBase):
    user_id:int # templorary 

# for partial update 
class PostUpdate(BaseModel):
    title:str | None = Field(default=None,min_length=1, max_length=100)
    content:str | None = Field(default=None,min_length=10)


class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)  # can access model fields using . \

    id:int
    date_posted : datetime
    user_id : int
    author : UserResponse
