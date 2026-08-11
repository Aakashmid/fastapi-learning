# schemas for api request and response data

from pydantic import BaseModel, ConfigDict, Field, EmailStr
from datetime import datetime


# User Schamas --------------------------------------------
class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str = Field(min_length=1, max_length=50)
    id: int
    image_file: str | None
    image_path: str


class UserPrivate(UserPublic):
    email: EmailStr = Field(max_length=120)

class Token(BaseModel):
    access_token : str 
    token_type : str


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=120)


# Post Schamas --------------------------------------------
class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=10)


class PostCreate(PostBase):
    pass


# for partial update
class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    content: str | None = Field(default=None, min_length=10)


class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)  # can access model fields using . \

    id: int
    date_posted: datetime
    user_id: int
    author: UserPublic


class PaginatedPostsResponse(BaseModel):
    posts: list[PostResponse]
    total: int
    skip: int
    limit: int
    has_more:bool