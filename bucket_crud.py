
import json
import os
import boto3
from dotenv import load_dotenv
from fastapi import HTTPException, UploadFile
from sqlmodel import Session
from aws_get_secrets import get_secret
import models

load_dotenv()

IMAGE_UPLOAD_USER_SECRET = os.getenv('IMAGE_UPLOAD_USER_SECRET')
REGION_NAME = os.getenv('REGION_NAME')
BUCKET_NAME = os.getenv('BUCKET_NAME')

def aws_client():
    secrets = json.loads(get_secret(IMAGE_UPLOAD_USER_SECRET))

    client = boto3.client(
        "s3",
        aws_access_key_id=secrets["aws_access_key_id"],
        aws_secret_access_key=secrets["aws_secret_access_key"]
    )

    return client


def upload_to_s3(file: UploadFile, folder: str, db: Session):
    s3_client = aws_client()

    object_key = f"{folder}/{file.filename}"
    content_type = file.content_type
    file.file.seek(0)

    try:
        s3_client.upload_fileobj(file.file, BUCKET_NAME, object_key, ExtraArgs={"ContentType": content_type})

        image = models.Image(object_key=f"{folder}/{file.filename}")
        db.add(image)
        db.commit()
        db.refresh(image)

        file_url = f"https://{BUCKET_NAME}.s3.{REGION_NAME}.amazonaws.com/{object_key}"
        return {"file_url": file_url, "content_type": content_type}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file to S3: {str(e)}")

def delete_from_s3(key: str):
    s3_client = aws_client()

    try:
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file from S3: {str(e)}")