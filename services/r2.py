import boto3
import os
from botocore.exceptions import ClientError

r2 = boto3.client(
    "s3",
    endpoint_url=f"https://{os.getenv('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com",
    aws_access_key_id=os.getenv("R2_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("R2_SECRET_KEY"),
    region_name="auto",
)

BUCKET = os.getenv("R2_BUCKET")

def upload_fileobj(file_obj, key, content_type="text/csv"):
    """Streams a file object directly to R2 (used during initial v0 upload)"""
    r2.upload_fileobj(
        file_obj,
        BUCKET,
        key,
        ExtraArgs={"ContentType": content_type},
    )

def upload_file(local_path, key, content_type="text/csv"):
    """Uploads a file from the disk to R2 (used after agents finish processing)"""
    r2.upload_file(
        local_path,
        BUCKET,
        key,
        ExtraArgs={"ContentType": content_type},
    )

def download_to_path(key, local_path):
    """Downloads a file straight to the disk for the LangChain agents to use"""
    r2.download_file(BUCKET, key, local_path)

def generate_presigned_url(key, expiration=3600):
    """Generates a secure, temporary URL for the Next.js frontend to download files"""
    try:
        response = r2.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET, 'Key': key},
            ExpiresIn=expiration
        )
        return response
    except ClientError as e:
        print(f"Error generating presigned URL: {e}")
        return None