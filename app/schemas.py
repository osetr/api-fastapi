from pydantic import BaseModel
from typing import List


class UserCreate(BaseModel):
    login: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    current_user: str = None

class PostCreate(BaseModel):
    post: str

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
    number_of_likes: int
    made_by: List[str]

class LastLike(BaseModel):
    post_id: int
    post_owner: str

class LastPost(BaseModel):
    post_id: int
    post_body: str

class LastLogin(BaseModel):
    login: str
    date_time: str

class UsersList(BaseModel):
    all_users_list: List[str]

class LastRequest(BaseModel):
    last_like: LastLike
    last_post: LastPost
    last_login: LastLogin
