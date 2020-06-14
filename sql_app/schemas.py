from pydantic import BaseModel


class UserBase(BaseModel):
    login: str

class UserCreate(UserBase):
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str = None

class PostCreate(BaseModel):
    post: str

class NewPostCreated(PostCreate):
    login: str


class Like(BaseModel):
    lover: str
    loved: str
    post_id: int

class LastLike(BaseModel):
    post_id: int
    post_owner: str

class LastPost(BaseModel):
    post_id: int
    post_body: str
