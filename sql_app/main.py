from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
import pymysql
pymysql.install_as_MySQLdb()
from .import crud, models, schemas
from .database import SessionLocal, engine
from fastapi.security import OAuth2PasswordRequestForm

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

models.Base.metadata.create_all(bind=engine)


app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.get("/users/")
def read_users(limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, limit=limit)
    return users

@app.get("/users/me/")
async def read_users_me(current_user = Depends(crud.get_current_user)):
    return current_user

@app.post("/users/new_user", response_model=schemas.UserCreate)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_login(db, login=user.login)
    if db_user:
        raise HTTPException(status_code=400, detail="Login already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/{user_login}/last_request/")
def read_posts(user_login: str = None, db: Session = Depends(get_db), current_user = Depends(crud.get_current_user)):
    if user_login != current_user["current_user"]:
        raise HTTPException(status_code=400, detail="User_login not found")
    db_user = crud.get_user_by_login(db, login=user_login)
    if not db_user:
        raise HTTPException(status_code=400, detail="User_login not found")
    request = crud.last_request(db, login=user_login)
    return request



@app.get("/users/posts/")
def read_posts(limit:int = 100, db: Session = Depends(get_db)):
    posts = crud.get_posts(db, limit=limit)
    return posts

@app.get("/users/{user_login}/posts/")
def read_posts(user_login: str = None, limit:int = 100, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_login(db, login=user_login)
    if not db_user:
        raise HTTPException(status_code=400, detail="User_login not found")
    posts = crud.get_certain_posts(db, login=user_login, limit=limit)
    return posts

@app.post("/users/{user_login}/posts/create/", response_model=schemas.NewPostCreated)
def create_post(user_login: str = None, current_user = Depends(crud.get_current_user), post: schemas.PostCreate = None, db: Session = Depends(get_db)):
    if user_login != current_user["current_user"]:
        raise HTTPException(status_code=400, detail="User_login not found")
    db_user = crud.get_user_by_login(db, user_login)
    if not db_user:
        raise HTTPException(status_code=400, detail="Faulty user_login")
    return crud.create_post(db=db, post=post, user_login=user_login)



@app.post("/users/{user_login}/likes/", response_model=schemas.Like)
def like(user_login: str, post_id: int, db: Session = Depends(get_db), current_user = Depends(crud.get_current_user)):
    if user_login != current_user["current_user"]:
        raise HTTPException(status_code=400, detail="User_login not found")
    db_user = crud.get_user_by_login(db, user_login)
    if not db_user:
        raise HTTPException(status_code=400, detail="Faulty user_login")
    db_post = crud.get_post_by_id(db, post_id)
    if not db_post:
        raise HTTPException(status_code=400, detail="Post not found")
    try:
        return crud.like(db=db, user_login=user_login, post_id=post_id)
    except:
        raise HTTPException(status_code=409, detail="Probably like already exist")

@app.delete("/users/{user_login}/unlikes/", response_model=schemas.Like)
def unlike(user_login: str, post_id: int, db: Session = Depends(get_db), current_user = Depends(crud.get_current_user)):
    if user_login != current_user["current_user"]:
        raise HTTPException(status_code=400, detail="User_login not found")
    db_user = crud.get_user_by_login(db, user_login)
    if not db_user:
        raise HTTPException(status_code=400, detail="Faulty user_login")
    db_post = crud.get_post_by_id(db, post_id)
    if not db_post:
        raise HTTPException(status_code=400, detail="Post not found")
    try:
        return crud.unlike(db=db, user_login=user_login, post_id=post_id)
    except:
        raise HTTPException(status_code=409, detail="Probably user still unlike this post")

@app.get("/likes_info/")
def likes_info(post_id: int, db: Session = Depends(get_db), date_from: str = "2000-12-31", date_to: str = "2020-12-12"):
    db_post = crud.get_post_by_id(db, post_id)
    if not db_post:
        raise HTTPException(status_code=400, detail="Post not found")
    if not (re.search("^20[0-9][0-9](-)(0[1-9]|1[0-2])(-)(0[1-9]|1[0-9]|2[0-9]|3[0-1])$",date_from) and (re.search("^20[0-9][0-9](-)(0[1-9]|1[0-2])(-)(0[1-9]|1[0-9]|2[0-9]|3[0-1])$",date_to))):
        raise HTTPException(status_code=400, detail="Uncorrect date")
    return crud.likes_info(post_id=post_id, db=db, date_from=date_from, date_to=date_to)



@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crud.create_access_token(db = db,
        data={"sub": user.login}, expires_delta=access_token_expires
    )
    return schemas.Token(access_token = access_token, token_type = "bearer")
