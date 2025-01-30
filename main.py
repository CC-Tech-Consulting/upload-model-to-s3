import os
import boto3
import logging

from botocore.config import Config
from boto3.s3.transfer import TransferConfig
from huggingface_hub import snapshot_download


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def download_model_to_s3(repo_id, bucket_name, s3_prefix, region):
    session = boto3.Session()
    current_region = session.region_name or os.environ.get("AWS_REGION", region)

    logging.info(f"Current AWS region: {current_region}")

    s3_config = Config(
        region_name=current_region,
        max_pool_connections=50,
        retries={"max_attempts": 5}
    )

    s3 = boto3.client("s3", config=s3_config)

    # Verify bucket exists and is in the correct region
    bucket_location = s3.get_bucket_location(Bucket=bucket_name).get("LocationConstraint")
    bucket_region = bucket_location if bucket_location else region

    if bucket_region != current_region:
        raise ValueError(f"Bucket {bucket_name} is in {bucket_region}, expected {current_region}")

    # Get the directory of main.py
    script_dir = os.path.dirname(os.path.abspath(__file__)) 
    local_path = os.path.join(script_dir, "model_download")  

    logging.info(f"Downloading model {repo_id} from Hugging Face to {local_path}...")

    # Download everything from the Hugging Face repo
    snapshot_download(
        repo_id=repo_id,
        local_dir=local_path,
        allow_patterns=None  # Download all files
    )

    logging.info(f"Model downloaded to {local_path}")

    # Configure S3 upload settings
    transfer_config = TransferConfig(
        multipart_threshold=1024 * 25,  # 25MB
        max_concurrency=10,
        use_threads=True
    )

    # Upload all files to S3
    for root, _, files in os.walk(local_path):
        for file in files:
            local_file_path = os.path.join(root, file)
            s3_key = os.path.join(s3_prefix, os.path.relpath(local_file_path, local_path)).replace("\\", "/")

            logging.info(f"Uploading {local_file_path} to s3://{bucket_name}/{s3_key}")

            try:
                s3.upload_file(
                    local_file_path,
                    bucket_name,
                    s3_key,
                    Config=transfer_config
                )
                os.remove(local_file_path)  # Remove after successful upload
            except Exception as e:
                logging.error(f"Failed to upload {local_file_path}: {str(e)}")

    logging.info("Model upload completed successfully.")


if __name__ == "__main__":
    region = "us-west-2"
    bucket_name = "llm-demo"
    s3_prefix = "DeepSeek-R1-Distill-Llama-8B"
    repo_id = "deepseek-ai/DeepSeek-R1-Distill-Llama-8B"

    try:
        download_model_to_s3(repo_id, bucket_name, s3_prefix, region)
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
