# Bitcot rag-base-ai
# Changelog


All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

### Sprint 35 - May 06 - May 17

### Added
- Fix - Updated code to fix the Sonar Issues

### Added
- [AI-23] -Fixed Thumbs-Up Feedback Submission Issue
          -Increased the token limit 

### Added
- [AI-18] - Added code to get store the s3 url while embedding the document and use that as citation
          - Prompt Update to get the s3 url

### Added
- [AI-18] - Added app.app_context() to get citation

### Sprint 34 - Apr 22 - May 03


### Fixed
- Updated code in embeddings to store in tmp folder
### Fixed
[AI-20]
- Implemented fix for empty message log and inability to recall previous conversations.
- Also Updated the Prompt to Respond with a summary of previous interactions

### Fixed
[AI-14]
- Updated file handling to use file paths instead of filenames for database storage.
- Updated MAX_CHUNK_OVERLAP parameter to 200

### Fixed
- [AI-09] - To pass the client and connection id in the streaming 

### Added
- Updated code from dev to master

### Added
[AI-09]
- Code changes on streaming to get the citation in chatbot response
- updated the chat interface prompt 

### Added
[AI-02]
- Fixed the Embeddings for the following extension [.md, .docx, .pdf]
- Revised the code for the chat interface.
- Added prompt for chat interface 

## [Unreleased]

### Fixed
- Optimized code within the metric_scheduler to improve performance 

### Added
- Added docstring to evaluate_chatbot_data function.
- Added non-nullable constraints to the fields user_input and final_response
- Added date field in evaluation api response

### Fixed
- Added Role for metric scheduler in template.yaml 
- Fixed import statements from ResponseEvaluation to EvaluationScores as the table name changed
- Updated the evaluated flag to is_evaluated in metric scheduler folder

### Changed
- Updated README.md

### Fixed
- Renamed table name from response_evaluation to evaluation_scores  
- Removed duplicates in migrations folder

### Changed
- Ran precommit
- changed the cron time interval

### Added
- Added cron for RAGAS evaluation
- Added RAGAS evaluation

### Fixed
- Updated template.yaml
- Updated github workflows
- Updated feedback function in write_to_db
- Added None condition in feedback if records does not exits

### Removed
- Removed get_secret_value_from_environment from apis/llms/constants

### Added
- Added Feedback models and feedback api

### Removed
- Code Fix, remove unnecssary code and correct the code to add data to DB
- Remove Redis 

### Added
- Added setuptools in requirements.txt

### Fixed
- Added migrations

- Ran precommit and removed USE_OPENAI

### Added
- Added new branch for RAG psql

### Fixed
- Added imports in Embeddings
- Updated chat api
- Removed user-info api
- Run precommit 
- Updated template.yaml
- Remove unnecessary APIs

### Changed
- Updated the models

### Fixed
- Fixed migration error.

### Changed
- Changed os.environ.get to get_secret_value_from_environmen

### Added
- Add models and migration
- Add psql RAG

### Fixed
- Update the QE check version to 0.0.9
- Update the prompt to fix "Fallback repsonse" and "Corpus" issue
- Fixed response time issue

### Added
- Add Dynamodb setup

### Changed
- Update the Prompt based on Feedback
- Create New thread for every message

### Added
- Add SES for Error Email's

### Changed
- Update the Prompt based on Feedback

### Added
- Allow ALL Methods in Chat Function

### Changed
- API Gateway functionality to direct Lambda Invocation

### Fixed
- Update the Prompt for better responses
- Revert Changes
- Updated the Prompt as per the requirements, it should respond as an FAQ Bot

### Added
- Added sonar badges & format instructions in README.md

### Fixed
- Formatted Code 
