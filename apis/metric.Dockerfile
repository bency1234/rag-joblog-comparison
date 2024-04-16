# Use the base image provided by AWS for Lambda functions with Python 3.10
FROM public.ecr.aws/lambda/python:3.10

# Copy the requirements.txt file to the container to install Python dependencies
COPY common/requirements.txt ./

# Install the Python dependencies
RUN python3.10 -m pip install -r requirements.txt -t .
RUN python3.10 -m pip install tqdm==4.64.1 -t .

# Copy all Python files from the settings directory to the container
# Ensure that the settings directory is at the same level as this Dockerfile
COPY metric_scheduler/* ./

# Copy common folder to the container
COPY common ./common

# The default command that will be executed when the Lambda function is invoked
# Command can be overwritten by providing a different command in the template directly.
CMD ["job.lambda_handler"]