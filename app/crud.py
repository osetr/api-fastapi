from sqlalchemy.orm import Session
from passlib.context import CryptContext
from . import models, schemas, settings
from datetime import datetime, timedelta
import jwt
from jwt import PyJWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



def get_users(db: Session, limit: int = 100):
    users_lists = db.query(models.User.login).limit(limit).all()
    users_list = []
    for i in users_lists:
        users_list.append(i[0])
    return schemas.UsersList(all_users_list=users_list)

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception
    return schemas.TokenData(current_user = username)

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(login=user.login, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return schemas.UserCreate(login = user.login, password = hashed_password)

def last_request(db: Session, login: str):
    last_like = db.query(models.Love.post_id, models.Love.loved).filter(models.Love.lover == login).order_by(models.Love.date_time).all()[slice(-1, None)][0]
    last_like_post_id = last_like[0]
    last_like_post_owner = last_like[1]

    last_post = db.query(models.Post.id, models.Post.post).filter(models.Post.login == login).order_by(models.Post.date_time).all()[slice(-1, None)][0]
    last_post_post_id = last_post[0]
    last_post_post_body = last_post[1]

    last_request = db.query(models.Login.date_time).filter(models.Login.login == login).order_by(models.Login.date_time).all()[slice(-1, None)][0]
    last_login_date_time = str(last_request[0])

    last_like = schemas.LastLike(post_id=last_like_post_id, post_owner=last_like_post_owner)
    last_post = schemas.LastPost(post_id=last_post_post_id, post_body=last_post_post_body)
    last_login = schemas.LastLogin(login=login, date_time=last_login_date_time)
    return schemas.LastRequest(last_like=last_like, last_post=last_post, last_login=last_login)



def get_posts(db: Session, limit: int = 100):
    posts_lists = db.query(models.Post.id, models.Post.post, models.Post.date_time).limit(limit).all()
    posts_list = []
    for i in posts_lists:
        posts_list.append(schemas.Post(id=i[0], post=i[1], date_time=str(i[2])))
    return schemas.PostsList(all_posts_list=posts_list)

def get_certain_posts(db: Session, login: str, limit: int = 100):
    posts_lists = db.query(models.Post.id, models.Post.post, models.Post.date_time).filter(models.Post.login == login).limit(limit).all()
    posts_list = []
    for i in posts_lists:
        posts_list.append(schemas.Post(id=i[0], post=i[1], date_time=str(i[2])))
    return schemas.PostsList(all_posts_list=posts_list)

def create_post(db: Session, user_login: str, post: schemas.PostCreate):
    db_post = models.Post(login=user_login, post = post.post)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return schemas.PostCreate(post = post.post)



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

def likes_info(post_id: int, db: Session, date_from: str, date_to:str):
    date_from = datetime.strptime(date_from,'%Y-%m-%d')
    date_to = datetime.strptime(date_to,'%Y-%m-%d')
    likes_lists = db.query(models.Love.lover).filter(models.Love.post_id == post_id).filter(models.Love.date_time<date_to).filter(models.Love.date_time>date_from).all()
    likes = []
    for i in likes_lists:
        likes.append(i[0])
    return schemas.LikeList(number_of_likes=len(likes),made_by=likes)




def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user_by_login(db: Session, login: str):
    return db.query(models.User).filter(models.User.login == login).first()

def get_post_by_id(db: Session, post_id: int):
    return db.query(models.Post).filter(models.Post.id == post_id).first()

def authenticate_user(db: Session, login: str, password: str):
    user = get_user_by_login(db, login)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(db: Session, data: dict, expires_delta: timedelta = None):
    db_post = models.Login(login=data["sub"])
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
