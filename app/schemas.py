from pydantic import BaseModel, Field
from typing import List


class UserCreate(BaseModel):
    login: str = Field(..., min_length=2, max_length=30)
    password: str = Field(..., min_length=5)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    current_user: str = None


class PostCreate(BaseModel):
    post: str = Field(..., min_length=1)


class Post(PostCreate):
    id: int
    date_time: str


class PostsList(BaseModel):
    all_posts_list: List[Post]


class Like(BaseModel):
    lover: str
    loved: str
    post_id: int


class LikeList(BaseModel):
    number_of_likes: int = None
    made_by: List[str] = None


class LastLike(BaseModel):
    post_id: int = None
    post_owner: str = None


class LastPost(BaseModel):
    post_id: int = None
    post_body: str = None


class LastLogin(BaseModel):
    login: str
    date_time: str


class UsersList(BaseModel):
    all_users_list: List[str]


class LastRequest(BaseModel):
    last_like: LastLike
    last_post: LastPost
    last_login: LastLogin
