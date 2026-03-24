import boto3
import os

r2 = boto3.client(
    "s3",
    endpoint_url=f"https://{os.getenv('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com",
    aws_access_key_id=os.getenv("R2_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("R2_SECRET_KEY"),
    region_name="auto",
)

BUCKET = os.getenv("R2_BUCKET")

def upload_fileobj(file_obj, key, content_type):
    r2.upload_fileobj(
        file_obj,
        BUCKET,
        key,
        ExtraArgs={"ContentType": content_type},
    )


def download_file(key):
    obj = r2.get_object(Bucket=BUCKET, Key=key)
    return obj["Body"].read()
