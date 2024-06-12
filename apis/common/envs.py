import json
import logging
import os

import boto3

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


# Function to get secret value from environment
def get_secret_value_from_environment(key):
    return os.getenv(key)


# Function to get secret value securely from AWS Secrets Manager
def get_secret_value_from_secret_manager(key):
    CI = get_secret_value_from_environment("CI")  # Moved inside the function
    if CI:  # Assuming CI is defined elsewhere
        try:
            # Create a Secrets Manager client
            client = boto3.client(
                service_name=get_secret_value_from_environment("SEC_SERVICE")
            )

            # Retrieve the secret
            get_secret_value_response = client.get_secret_value(
                SecretId=get_secret_value_from_environment("SEC_NAME")
            )

            # Access the desired value using its key
            data = json.loads(get_secret_value_response.get("SecretString"))

            return data[key]
        except Exception as e:
            logger.error(f"Error retrieving secret from AWS Secrets Manager: {str(e)}")
            # Handle exception appropriately, possibly raise or return None
            return None
    else:
        return get_secret_value_from_environment(key)
