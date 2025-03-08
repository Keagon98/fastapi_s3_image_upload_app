import uvicorn
from bucket_upload import upload_to_s3
import models
from fastapi import Depends, FastAPI, UploadFile
from typing import List
from pydantic import BaseModel
from sqlalchemy import select
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
async def get_image(db: Session = Depends(get_db)):
    stmt = select(models.Image)
    presigned_url_list: List[ImageBase] = []

    for data in db.scalars(stmt):
        url = presign_url(data)
        response = ImageBase(id = data.id, image_url = url)
        presigned_url_list.append(response)

    return presigned_url_list

@app.post("/uploadfile")
def upload_file(file: UploadFile, db: Session = Depends(get_db)):
    validate_file_size_type(file)
    return upload_to_s3(file, "images", db=db)

if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, log_level="info", reload=True)