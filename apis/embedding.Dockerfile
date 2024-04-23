# Use the base image provided by AWS for Lambda functions with Python 3.10
FROM python:3.10

RUN apt-get update && apt-get install -y libreoffice libreoffice-gnome

# Copy the requirements.txt file to the container to install Python dependencies
COPY common/requirements.txt ./common_requirements.txt
COPY ai/requirements.txt ./ai_requirements.txt

# Install the Python dependencies
RUN python3.10 -m pip install -r common_requirements.txt -t .
RUN python3.10 -m pip install -r ai_requirements.txt -t .

RUN python3.10 -m pip install antiword

# Copy all Python files from the settings directory to the container
# Ensure that the settings directory is at the same level as this Dockerfile
COPY embedding/*.py ./

# Copy common folder to the container
COPY common ./common
COPY ai ./ai

# The default command that will be executed when the Lambda function is invoked
# Command can be overwritten by providing a different command in the template directly.
CMD ["app.lambda_handler"]
