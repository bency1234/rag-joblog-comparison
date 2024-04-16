# rag-base-ai

This project contains source code and supporting files for a serverless application that you can deploy with the SAM CLI. It includes the following files and folders.

- hello_world - Code for the application's Lambda function and Project Dockerfile.
- events - Invocation events that you can use to invoke the function.
- tests - Unit tests for the application code. 
- template.yaml - A template that defines the application's AWS resources.

The application uses several AWS resources, including Lambda functions and an API Gateway API. These resources are defined in the `template.yaml` file in this project. You can update the template to add AWS resources through the same deployment process that updates your application code.


#### SonarQube - Dev and Demo status

Environment | Dev | Demo |
--- | --- | --- | 
Quality gate | [![Quality gate](http://122.168.196.5:9000/api/project_badges/quality_gate?project=rag-base-ai-dev)](http://122.168.196.5:9000/dashboard?id=rag-base-ai-dev)| [![Quality gate](http://122.168.196.5:9000/api/project_badges/quality_gate?project=rag-base-ai)](http://122.168.196.5:9000/dashboard?id=rag-base-ai) |
Bugs | [![Bugs](http://122.168.196.5:9000/api/project_badges/measure?project=rag-base-ai-dev&metric=bugs)](http://122.168.196.5:9000/dashboard?id=rag-base-ai-dev)| [![Bugs](http://122.168.196.5:9000/api/project_badges/measure?project=rag-base-ai&metric=bugs)](http://122.168.196.5:9000/dashboard?id=rag-base-ai) |
Code Smells | [![Code Smells](http://122.168.196.5:9000/api/project_badges/measure?project=rag-base-ai-dev&metric=code_smells)](http://122.168.196.5:9000/dashboard?id=rag-base-ai-dev)| [![Code Smells](http://122.168.196.5:9000/api/project_badges/measure?project=rag-base-ai&metric=code_smells)](http://122.168.196.5:9000/dashboard?id=rag-base-ai) |
Coverage | [![Coverage](http://122.168.196.5:9000/api/project_badges/measure?project=rag-base-ai-dev&metric=coverage)](http://122.168.196.5:9000/dashboard?id=rag-base-ai-dev)| [![Coverage](http://122.168.196.5:9000/api/project_badges/measure?project=rag-base-ai&metric=coverage)](http://122.168.196.5:9000/dashboard?id=rag-base-ai) |
Duplicated Lines (%) | [![Duplicated Lines (%)](http://122.168.196.5:9000/api/project_badges/measure?project=rag-base-ai-dev&metric=duplicated_lines_density)](http://122.168.196.5:9000/dashboard?id=rag-base-ai-dev) | [![Duplicated Lines (%)](http://122.168.196.5:9000/api/project_badges/measure?project=rag-base-ai&metric=duplicated_lines_density)](http://122.168.196.5:9000/dashboard?id=rag-base-ai) |
Maintainability Rating | [![Maintainability Rating](http://122.168.196.5:9000/api/project_badges/measure?project=rag-base-ai-dev&metric=sqale_rating)](http://122.168.196.5:9000/dashboard?id=rag-base-ai-dev) | [![Maintainability Rating](http://122.168.196.5:9000/api/project_badges/measure?project=rag-base-ai&metric=sqale_rating)](http://122.168.196.5:9000/dashboard?id=rag-base-ai) |
Lines of Code | [![Lines of Code](http://122.168.196.5:9000/api/project_badges/measure?project=rag-base-ai-dev&metric=ncloc)](http://122.168.196.5:9000/dashboard?id=rag-base-ai-dev)| [![Lines of Code](http://122.168.196.5:9000/api/project_badges/measure?project=rag-base-ai&metric=ncloc)](http://122.168.196.5:9000/dashboard?id=rag-base-ai) |
Reliability Rating | [![Reliability Rating](http://122.168.196.5:9000/api/project_badges/measure?project=rag-base-ai-dev&metric=reliability_rating)](http://122.168.196.5:9000/dashboard?id=rag-base-ai-dev) | [![Reliability Rating](http://122.168.196.5:9000/api/project_badges/measure?project=rag-base-ai&metric=reliability_rating)](http://122.168.196.5:9000/dashboard?id=rag-base-ai) |
Security Rating | [![Security Rating](http://122.168.196.5:9000/api/project_badges/measure?project=rag-base-ai-dev&metric=security_rating)](http://122.168.196.5:9000/dashboard?id=rag-base-ai-dev) | [![Security Rating](http://122.168.196.5:9000/api/project_badges/measure?project=rag-base-ai&metric=security_rating)](http://122.168.196.5:9000/dashboard?id=rag-base-ai) |
Technical Debt | [![Technical Debt](http://122.168.196.5:9000/api/project_badges/measure?project=rag-base-ai-dev&metric=sqale_index)](http://122.168.196.5:9000/dashboard?id=rag-base-ai-dev)| [![Technical Debt](http://122.168.196.5:9000/api/project_badges/measure?project=rag-base-ai&metric=sqale_index)](http://122.168.196.5:9000/dashboard?id=rag-base-ai) |
Vulnerabilities | [![Vulnerabilities](http://122.168.196.5:9000/api/project_badges/measure?project=rag-base-ai-dev&metric=vulnerabilities)](http://122.168.196.5:9000/dashboard?id=rag-base-ai-dev)| [![Vulnerabilities](http://122.168.196.5:9000/api/project_badges/measure?project=rag-base-ai&metric=vulnerabilities)](http://122.168.196.5:9000/dashboard?id=rag-base-ai) |

## Table of Contents
- [Code Formatting and Linting Guidelines](#code-Formatting-and-Linting-Guidelines)
- [Automatic Code Formatting and Linting with Pre-commit](#automatic-code-formatting-and-linting-with-pre-commit)


## Code Formatting and Linting Guidelines
Before merging any code into our project, it is essential that your contributions adhere to our code formatting and linting standards. We use Black for code formatting, isort for sorting imports, and Flake8 for checking code against coding style (PEP8), programming errors, and other issues. Below are the steps to ensure your code meets these standards.

Note: It's crucial to maintain consistency in versions between pre-commit.yaml and dev_requirements.txt to ensure that the results of automatic and manual formatting and linting are consistent. Different versions may yield different results.

## Automatic Code Formatting and Linting with Pre-commit
To streamline the process and ensure your code is automatically formatted and linted before each commit, follow these steps:

### 1. Install pre-commit:

First, install pre-commit using pip. Open your terminal and run:

```bash
pip install -r dev_requirements.txt
```
#### 2. Activate pre-commit in your repository:

Next, set up pre-commit in your project by running:

```bash
pre-commit install
```
This command configures pre-commit to run automatically on git commit.

#### 3. Making Commits:

With pre-commit installed, it will automatically run Black, isort, and Flake8 each time you commit changes.

If pre-commit makes changes, simply add those changes to your commit with git add -u && !!

```bash
git add -u && !!
```

###  Running the Tools Manually:

```bash
pre-commit run --all-files
```


By following these guidelines, you help ensure that our codebase remains clean, readable, and consistent. Please make sure your contributions pass these checks before submitting a pull request.

## Deploy the sample application

The Serverless Application Model Command Line Interface (SAM CLI) is an extension of the AWS CLI that adds functionality for building and testing Lambda applications. It uses Docker to run your functions in an Amazon Linux environment that matches Lambda. It can also emulate your application's build environment and API.

To use the SAM CLI, you need the following tools.

* SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* Docker - [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)

You may need the following for local testing.
* [Python 3 installed](https://www.python.org/downloads/)

To build and deploy your application for the first time, run the following in your shell:

```bash
sam build
sam deploy --guided
```

The first command will build a docker image from a Dockerfile and then copy the source of your application inside the Docker image. The second command will package and deploy your application to AWS, with a series of prompts:

* **Stack Name**: The name of the stack to deploy to CloudFormation. This should be unique to your account and region, and a good starting point would be something matching your project name.
* **AWS Region**: The AWS region you want to deploy your app to.
* **Confirm changes before deploy**: If set to yes, any change sets will be shown to you before execution for manual review. If set to no, the AWS SAM CLI will automatically deploy application changes.
* **Allow SAM CLI IAM role creation**: Many AWS SAM templates, including this example, create AWS IAM roles required for the AWS Lambda function(s) included to access AWS services. By default, these are scoped down to minimum required permissions. To deploy an AWS CloudFormation stack which creates or modifies IAM roles, the `CAPABILITY_IAM` value for `capabilities` must be provided. If permission isn't provided through this prompt, to deploy this example you must explicitly pass `--capabilities CAPABILITY_IAM` to the `sam deploy` command.
* **Save arguments to samconfig.toml**: If set to yes, your choices will be saved to a configuration file inside the project, so that in the future you can just re-run `sam deploy` without parameters to deploy changes to your application.

You can find your API Gateway Endpoint URL in the output values displayed after deployment.

## Use the SAM CLI to build and test locally

Build your application with the `sam build` command.

```bash
rag-base-ai$ sam build
```

The SAM CLI builds a docker image from a Dockerfile and then installs dependencies defined in `hello_world/requirements.txt` inside the docker image. The processed template file is saved in the `.aws-sam/build` folder.

Test a single function by invoking it directly with a test event. An event is a JSON document that represents the input that the function receives from the event source. Test events are included in the `events` folder in this project.

Run functions locally and invoke them with the `sam local invoke` command.

```bash
rag-base-ai$ sam local invoke HelloWorldFunction --event events/event.json
```

The SAM CLI can also emulate your application's API. Use the `sam local start-api` to run the API locally on port 3000.

```bash
rag-base-ai$ sam local start-api
rag-base-ai$ curl http://localhost:3000/
```

The SAM CLI reads the application template to determine the API's routes and the functions that they invoke. The `Events` property on each function's definition includes the route and method for each path.

```yaml
      Events:
        HelloWorld:
          Type: Api
          Properties:
            Path: /hello
            Method: get
```

## Add a resource to your application
The application template uses AWS Serverless Application Model (AWS SAM) to define application resources. AWS SAM is an extension of AWS CloudFormation with a simpler syntax for configuring common serverless application resources such as functions, triggers, and APIs. For resources not included in [the SAM specification](https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md), you can use standard [AWS CloudFormation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-template-resource-type-ref.html) resource types.

## Fetch, tail, and filter Lambda function logs

To simplify troubleshooting, SAM CLI has a command called `sam logs`. `sam logs` lets you fetch logs generated by your deployed Lambda function from the command line. In addition to printing the logs on the terminal, this command has several nifty features to help you quickly find the bug.

`NOTE`: This command works for all AWS Lambda functions; not just the ones you deploy using SAM.

```bash
rag-base-ai$ sam logs -n HelloWorldFunction --stack-name "rag-base-ai" --tail
```

You can find more information and examples about filtering Lambda function logs in the [SAM CLI Documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-logging.html).

## Unit tests

Tests are defined in the `tests` folder in this project. Use PIP to install the [pytest](https://docs.pytest.org/en/latest/) and run unit tests from your local machine.

```bash
rag-base-ai$ pip install pytest pytest-mock --user
rag-base-ai$ python -m pytest tests/ -v
```

## Cleanup

To delete the sample application that you created, use the AWS CLI. Assuming you used your project name for the stack name, you can run the following:

```bash
sam delete --stack-name "rag-base-ai"
```

## Resources

See the [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) for an introduction to SAM specification, the SAM CLI, and serverless application concepts.

Next, you can use AWS Serverless Application Repository to deploy ready to use Apps that go beyond hello world samples and learn how authors developed their applications: [AWS Serverless Application Repository main page](https://aws.amazon.com/serverless/serverlessrepo/)
