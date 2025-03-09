from email.message import Message

import uvicorn
from bucket_crud import upload_to_s3, delete_from_s3
import models
from fastapi import Depends, FastAPI, UploadFile
from typing import List
from pydantic import BaseModel
from sqlalchemy import select, delete
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from presign_url import presign_url
from validate import validate_file_size_type

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

class ImageBase(BaseModel):
    id: int
    image_url: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/images")
def get_images(db: Session = Depends(get_db)):
    stmt = select(models.Image)
    presigned_url_list: List[ImageBase] = []

    for data in db.scalars(stmt):
        url = presign_url(data)
        response = ImageBase(id = data.id, image_url = url)
        presigned_url_list.append(response)

    return presigned_url_list

@app.post("/images")
def upload_images(file: UploadFile, db: Session = Depends(get_db)):
    validate_file_size_type(file)
    return upload_to_s3(file, "images", db=db)

@app.delete("/images")
def delete_images():
    # stmt = delete(models.Image).where(models.Image.id == id)
    test_image = "images/vue-js-logo.png"
    delete_from_s3(test_image)


if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, log_level="info", reload=True)