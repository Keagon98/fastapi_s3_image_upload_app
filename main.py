from http.client import HTTPException

import uvicorn
from starlette import status
from starlette.responses import Response

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

@app.delete("/images/{image_id}")
def delete_images(image_id: int, db: Session = Depends(get_db)):
    image = db.query(models.Image).filter(models.Image.id == image_id)
    delete_from_s3(image.first().object_key)

    if image.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Image with id: {image_id} does not exist")

    image.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, log_level="info", reload=True)