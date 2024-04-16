FROM public.ecr.aws/lambda/python:3.10

# Copy the requirements.txt file to the container to install Python dependencies
COPY common/requirements.txt ./

# Install the Python dependencies
RUN python3.10 -m pip install -r requirements.txt -t .

COPY login/* ./

# Copy common folder to the container
COPY common ./common

# Command can be overwritten by providing a different command in the template directly.
CMD ["app.lambda_handler"]
 