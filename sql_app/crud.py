from sqlalchemy.orm import Session
from passlib.context import CryptContext
from . import models, schemas
from datetime import datetime, timedelta
import jwt
from jwt import PyJWTError
from fastapi import Depends, FastAPI, HTTPException, status
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "ffd3fccf1ab4cf54495121526f473be5ff49fb32873d664962da7eca3d111ce5"
ALGORITHM = "HS256"
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def get_user_by_login(db: Session, login: str):
    return db.query(models.User).filter(models.User.login == login).first()

def get_post_by_id(db: Session, post_id: int):
    return db.query(models.Post).filter(models.Post.id == post_id).first()

def get_users(db: Session, limit: int = 100):
    return db.query(models.User.login).limit(limit).all()

def get_certain_posts(db: Session, login: str, limit: int = 100):
    return db.query(models.Post.id, models.Post.post, models.Post.date_time).filter(models.Post.login == login).limit(limit).all()

def get_posts(db: Session, limit: int = 100):
    return db.query(models.Post.id, models.Post.post, models.Post.date_time).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(login=user.login, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return schemas.UserCreate(login = user.login, password = hashed_password)

def create_post(db: Session, user_login: str, post: schemas.PostCreate):
    db_post = models.Post(login=user_login, post = post.post)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return schemas.NewPostCreated(login = user_login, post = post.post)

def like(db: Session, user_login:str, post_id: int):
    loved = db.query(models.Post.login).filter(models.Post.id == post_id).limit(1).all()
    loved = loved[0][0]
    db_post = models.Love(lover=user_login, loved = loved, post_id = post_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return schemas.Like(lover = user_login, loved = loved, post_id = post_id)

def unlike(db: Session, user_login:str, post_id: int):
    loved = db.query(models.Post.login).filter(models.Post.id == post_id).limit(1).all()
    loved = loved[0][0]
    if (db.query(models.Love).filter(models.Love.post_id == post_id).filter(models.Love.lover == user_login).delete(synchronize_session='fetch') == 0):
        raise "Something went wrong"
    db.commit()
    return schemas.Like(lover = user_login, loved = loved, post_id = post_id)

def authenticate_user(db: Session, login: str, password: str):
    user = get_user_by_login(db, login)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def likes_info(post_id: int, db: Session, date_from: str, date_to:str):
    date_from = datetime.strptime(date_from,'%Y-%m-%d')
    date_to = datetime.strptime(date_to,'%Y-%m-%d')
    return db.query(models.Love.lover).filter(models.Love.post_id == post_id).filter(models.Love.date_time<date_to).filter(models.Love.date_time>date_from).all()

def last_request(db: Session, login: str):
    last_like = db.query(models.Love.post_id, models.Love.loved).filter(models.Love.lover == login).order_by(models.Love.date_time).all()[slice(-1, None)][0]
    last_like_post_id = last_like[0]
    last_like_post_owner = last_like[1]
    last_post = db.query(models.Post.id, models.Post.post).filter(models.Post.login == login).order_by(models.Post.date_time).all()[slice(-1, None)][0]
    last_post_post_id = last_post[0]
    last_post_post_body = last_post[1]
    return {"last_like" : schemas.LastLike(post_id=last_like_post_id, post_owner=last_like_post_owner),
            "last_post" : schemas.LastPost(post_id=last_post_post_id, post_body=last_post_post_body)}

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# async def get_current_user(db: Session, token: str = Depends(oauth2_scheme)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#         token_data = schemas.TokenData(username=username)
#     except PyJWTError:
#         raise credentials_exception
#     user = get_user_by_login(db, username=token_data.username)
#     if user is None:
#         raise credentials_exception
#     return user
#
# async def get_current_active_user(current_user: schemas.UserCreate = Depends(get_current_user)):
#     return current_user
