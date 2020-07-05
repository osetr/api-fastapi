from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import settings
import pymysql
pymysql.install_as_MySQLdb()

SQLALCHEMY_DATABASE_URL = (
                            "mysql://root:" +
                            str(settings.DB_PASS) +
                            "@127.0.0.1:3306/app"
                          )

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
