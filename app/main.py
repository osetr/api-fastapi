from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import re
import pymysql
from .import crud, models, schemas, settings
from .database import SessionLocal, engine
from fastapi.security import OAuth2PasswordRequestForm
pymysql.install_as_MySQLdb()


ACCESS_TOKEN_EXPIRE_MINUTES = int(settings.ACCESS_TOKEN_EXPIRE_MINUTES)

models.Base.metadata.create_all(bind=engine)


app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/users/", response_model=schemas.UsersList)
def read_users(limit: int=100, db: Session=Depends(get_db)):
    return crud.get_users(db, limit=limit)


@app.get("/users/me/", response_model=schemas.TokenData)
async def read_users_me(current_user=Depends(crud.get_current_user)):
    return current_user


@app.post("/users/new_user",
          response_model=schemas.UserCreate,
          status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate,
                db: Session=Depends(get_db)):
    db_user = crud.get_user_by_login(db, login=user.login)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Login already registered"
        )
    return crud.create_user(db=db, user=user)


@app.get("/users/{user_login}/last_request/",
         response_model=schemas.LastRequest)
def read_posts(user_login: str,
               db: Session=Depends(get_db),
               current_user=Depends(crud.get_current_user)):
    if user_login != current_user.current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="There're no permissions for user " +
            current_user.current_user
        )
    db_user = crud.get_user_by_login(db, login=user_login)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User_login not found"
        )
    return crud.last_request(db, login=user_login)


@app.get("/users/posts/", response_model=schemas.PostsList)
def read_posts(limit: int=100,
               db: Session=Depends(get_db)):
    return crud.get_posts(db, limit=limit)


@app.get("/users/{user_login}/posts/", response_model=schemas.PostsList)
def read_posts(user_login: str=None,
               limit: int=100,
               db: Session=Depends(get_db)):
    db_user = crud.get_user_by_login(db, login=user_login)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User_login not found"
        )
    return crud.get_certain_posts(db, login=user_login, limit=limit)


@app.post("/users/{user_login}/posts/create/",
          response_model=schemas.PostCreate,
          status_code=status.HTTP_201_CREATED)
def create_post(user_login: str=None,
                current_user=Depends(crud.get_current_user),
                post: schemas.PostCreate=None,
                db: Session=Depends(get_db)):
    if user_login != current_user.current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="There're no permissions for user " +
            current_user.current_user
        )
    db_user = crud.get_user_by_login(db, user_login)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User_login not found"
        )
    return crud.create_post(db=db, post=post, user_login=user_login)


@app.post("/users/{user_login}/likes/", response_model=schemas.Like)
def like(user_login: str,
         post_id: int,
         db: Session=Depends(get_db),
         current_user=Depends(crud.get_current_user)):
    if user_login != current_user.current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="There're no permissions for user " +
            current_user.current_user
        )
    db_user = crud.get_user_by_login(db, user_login)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User_login not found"
        )
    db_post = crud.get_post_by_id(db, post_id)
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post not found"
        )
    try:
        return crud.like(db=db, user_login=user_login, post_id=post_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Probably like already exists"
        )


@app.delete("/users/{user_login}/unlikes/", response_model=schemas.Like)
def unlike(user_login: str,
           post_id: int,
           db: Session=Depends(get_db),
           current_user=Depends(crud.get_current_user)):
    if user_login != current_user.current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="There're no permissions for user " +
            current_user.current_user
        )
    db_user = crud.get_user_by_login(db, user_login)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User_login not found"
        )
    db_post = crud.get_post_by_id(db, post_id)
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post not found"
        )
    try:
        return crud.unlike(db=db, user_login=user_login, post_id=post_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Probably user still unlikes post"
        )


@app.get("/likes_info/", response_model=schemas.LikeList)
def likes_info(post_id: int,
               db: Session = Depends(get_db),
               date_from: str = "2000-12-31",
               date_to: str = "2020-12-12"):
    db_post = crud.get_post_by_id(db, post_id)
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post not found"
        )
    re_e_1 = "^20[0-9][0-9](-)(0[1-9]|1[0-2])(-)(0[1-9]|1[0-9]|2[0-9]|3[0-1])$"
    re_e_2 = "^20[0-9][0-9](-)(0[1-9]|1[0-2])(-)(0[1-9]|1[0-9]|2[0-9]|3[0-1])$"
    if not (re.search(re_e_1, date_from) and (re.search(re_e_2, date_to))):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uncorrect date input"
        )
    return crud.likes_info(post_id=post_id,
                           db=db,
                           date_from=date_from,
                           date_to=date_to)


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
                form_data: OAuth2PasswordRequestForm=Depends(),
                db: Session=Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crud.create_access_token(db=db,
                                            data={"sub": user.login},
                                            expires_delta=access_token_expires)
    return schemas.Token(access_token=access_token, token_type="bearer")
