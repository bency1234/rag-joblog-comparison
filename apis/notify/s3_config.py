import os

import boto3
import botocore
from common.envs import get_secret_value_from_secret_manager
from dotenv import load_dotenv


class S3Manager:
    def __init__(self):
        load_dotenv()
        self.aws_access_key = get_secret_value_from_secret_manager("AWS_ACCESS_KEY")
        self.aws_secret_key = get_secret_value_from_secret_manager("AWS_SECRET_KEY")
        self.bucket_name = get_secret_value_from_secret_manager("BUCKET_NAME")

    def delete_files_from_local(self, file):
        """
        Deletes a file from the local system.
        """
        if os.path.isfile(file):
            try:
                os.remove(file)
                print("Deleted file from local")
            except OSError as e:
                print(f"Error: {self.file} : {e.strerror}")

    def download_csv(self, file_path=None, file_name=None):
        """
        Downloads a CSV file from an Amazon S3 bucket.
        """
        try:
            file_name = file_name or self.filename
            file_path = file_path or self.file
            print(
                f"Attempting to download file - file_path {file_path}, file_name {file_name}"
            )

            session = boto3.Session(
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
            )
            s3 = session.resource("s3")
            s3.Bucket(self.bucket_name).download_file(file_path, file_name)
            return True
        except botocore.exceptions.ClientError as e:
            print(f"Failed to download file from '{self.bucket_name}/{file_path}': {e}")
            return False
