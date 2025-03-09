import json
import sqlalchemy as sa
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from aws_get_secrets import get_secret

load_dotenv()

IMAGE_UPLOAD_DB_SECRET = os.getenv('IMAGE_UPLOAD_DB_SECRET')
secrets = json.loads(get_secret(IMAGE_UPLOAD_DB_SECRET))

url_object = sa.URL.create(
    f"{secrets["engine"]}+pymysql",
    username=secrets["username"],
    password=secrets["password"],
    host=secrets["host"],
    port=secrets["port"],
    database=secrets["dbname"],
)

engine = create_engine(url_object)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()