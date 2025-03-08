import json
import os
import boto3
from dotenv import load_dotenv
from aws_get_secrets import get_secret
from models import Image

load_dotenv()

IMAGE_UPLOAD_USER_SECRET = os.getenv('IMAGE_UPLOAD_USER_SECRET')
REGION_NAME = os.getenv('REGION_NAME')
BUCKET_NAME = os.getenv('BUCKET_NAME')

secrets = json.loads(get_secret(IMAGE_UPLOAD_USER_SECRET))

def aws_client():
    s3_client = boto3.client(
        "s3", 
        aws_access_key_id=secrets["aws_access_key_id"],
        aws_secret_access_key=secrets["aws_secret_access_key"],
        region_name=REGION_NAME, 
        endpoint_url=f"https://s3.{REGION_NAME}.amazonaws.com"
    )

    return s3_client

def presign_url(data: Image):
    s3_client = aws_client()

    url = s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": BUCKET_NAME, "Key": data.object_key},
                ExpiresIn=3600, 
        )
    
    return url