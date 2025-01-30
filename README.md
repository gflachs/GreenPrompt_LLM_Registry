# LLM Registry Service
[![Build and Test](https://github.com/gflachs/GreenPrompt_LLM_Registry/actions/workflows/build.yml/badge.svg)](https://github.com/gflachs/GreenPrompt_LLM_Registry/actions/workflows/build.yml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=gflachs_GreenPrompt_LLM_Registry&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=gflachs_GreenPrompt_LLM_Registry)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=gflachs_GreenPrompt_LLM_Registry&metric=bugs)](https://sonarcloud.io/summary/new_code?id=gflachs_GreenPrompt_LLM_Registry)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=gflachs_GreenPrompt_LLM_Registry&metric=coverage)](https://sonarcloud.io/summary/new_code?id=gflachs_GreenPrompt_LLM_Registry)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=gflachs_GreenPrompt_LLM_Registry&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=gflachs_GreenPrompt_LLM_Registry)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=gflachs_GreenPrompt_LLM_Registry&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=gflachs_GreenPrompt_LLM_Registry)

## Table of Content
1. [Purpose](#purpose)
2. [Setup](#setup)
3. [Codebase Structure](#codebase-structure)
4. [Start the Service](#start-the-service)
5. [Contribution](#contribution)

## Purpose

This Service provides LLMS via an API. It is part of the Greenprompt project. The service registry is a central component of the Greenprompt project. It is responsible for managing the lifecycle of the LLMWrappers and providing information about the currently deployed LLMS to the other components of the Greenprompt project.

It knows which machines are available, spawns LLMWrapper on them and manages the LLMS, which are running inside the LLMWrappers. The service registry is also responsible for providing information about the currently deployed LLMS to the other components of the Greenprompt project.

## Architecture
### Components
This component diagram illustrates the key role of the LLM Registry in the GreenPrompt architecture. The Registry acts as a central hub, interacting with various components such as the LLM Machine, Prompting Service, and LLMConfig. It manages the deployment and lifecycle of LLM Wrappers, provides LLMs to the Prompting Service, and stores LLM information in the LLM Registry DB.

[![Components](https://tinyurl.com/2dml8ap9)](https://tinyurl.com/2dml8ap9)<!--![Components](./docs/architecture/components.puml)-->

### Sequenz
This sequence diagram illustrates the key role of the LLM Registry in managing LLM deployments and fulfilling LLM requests. The Registry interacts with various components, including the LLMConfig, LLM Machine, LLM Wrapper, and LLM, to ensure the availability of LLMs for the Prompting Service.

[![Sequenz](https://tinyurl.com/2dcbntvl)](https://tinyurl.com/2dcbntvl)<!--![Sequenz](./docs/architecture/sequenz.puml)-->

### Activity
This activity diagram illustrates the key role of the LLM Registry in managing the lifecycle of LLMs. The Registry orchestrates the deployment of LLM Wrappers, monitors their status, and ensures the availability of LLMs to fulfill requests from the Prompting Service. The Registry also plays a crucial role in coordinating the shutdown process.

[![Activity](https://tinyurl.com/2cxpee47)](https://tinyurl.com/2cxpee47)<!--![Activity](./docs/architecture/activity.puml)-->

### Communication with the Promtingservice
This workflow diagram illustrates the process of requesting and using an LLM through the LLM Registry. The Prompting Service initiates a request for an LLM, and the Registry handles the allocation of available LLMs. The Registry provides a temporary link for the Prompting Service to monitor the LLM's status. Once the LLM is ready, the Registry sends the necessary information to the Prompting Service for interaction. After the Prompting Service is finished, it releases the LLM back to the Registry.

[![Communication with the Promtingservice](https://tinyurl.com/29qrd7rv)](https://tinyurl.com/29qrd7rv)<!--![Communication with the Promtingservice](./docs/architecture/promptingservice_workflow.puml)-->

## Setup

Dependencies:
- **requests:** Used for making HTTP requests to communicate with external services.
- **pytest:** Utilized for writing and running tests.
- **pytest-mock:** A plugin for pytest to use mock objects.
- **fastapi[standard]:** A web framework for building APIs with Python 3.7+ based on standard Python type hints.
- **httpx:** Provides a fully featured HTTP client for Python.
- **paramiko:** A Python implementation of the SSHv2 protocol, providing both client and server functionality.

Install all dependencies from the `requirements.txt` file using pip:
```sh
pip install -r requirements.txt
```

## Codebase Structure
- **[.github/workflows](https://github.com/gflachs/GreenPrompt_LLM_Registry/tree/main/.github/workflows):**
  - **[build.yml](https://github.com/gflachs/GreenPrompt_LLM_Registry/blob/main/.github/workflows/build.yml):** Defines the build and test process.
  - **[plantuml.yml](https://github.com/gflachs/GreenPrompt_LLM_Registry/blob/main/.github/workflows/plantuml.yml):** Processes PlantUML diagrams in Markdown files.
  - **[sonarcube.yml](https://github.com/gflachs/GreenPrompt_LLM_Registry/blob/main/.github/workflows/sonarcube.yml):** Integrates SonarQube for code quality analysis.
- **[docs/architectur](https://github.com/gflachs/GreenPrompt_LLM_Registry/tree/main/docs/architecture):** Stores puml files, that allows you to generate UML diagrams from plain text descriptions.
- **[src](https://github.com/gflachs/GreenPrompt_LLM_Registry/tree/main/src):** Contains the source code files. </summary>
   - **[app](https://github.com/gflachs/GreenPrompt_LLM_Registry/tree/main/src/app):** Contains the main application logic and modules.
      - **[clients](https://github.com/gflachs/GreenPrompt_LLM_Registry/tree/main/src/app/clients):** Contains modules that manage interactions with external services or clients.
         - **[__init__.py](https://github.com/gflachs/GreenPrompt_LLM_Registry/blob/main/src/app/clients/__init__.py):** This file initializes the clients module.
         - **[wrapper_client.py](https://github.com/gflachs/GreenPrompt_LLM_Registry/blob/main/src/app/clients/wrapper_client.py):** This module handles sending requests to the LLM Wrapper for deploying, stopping, and checking the status of LLM instances.
      - **[controller](https://github.com/gflachs/GreenPrompt_LLM_Registry/blob/main/src/app/controller):** Contains modules that manage application logic and interactions with the database or other services.
         - **[__init__.py](https://github.com/gflachs/GreenPrompt_LLM_Registry/blob/main/src/app/controller/__init__.py):** This file initializes the controller module.
         - **[db_controller.py](https://github.com/gflachs/GreenPrompt_LLM_Registry/blob/main/src/app/controller/db_controller.py):** This module manages interactions with the SQLite database, including creating tables, inserting data, and running queries.
         - **[promptingservice_controller.py](https://github.com/gflachs/GreenPrompt_LLM_Registry/blob/main/src/app/controller/promptingservice_controller.py):** This module defines API endpoints for managing LLM deployment requests using FastAPI.
      - **[models](https://github.com/gflachs/GreenPrompt_LLM_Registry/blob/main/src/app/models):** This directory contains data models used in the application.
         - **[__init__.py](https://github.com/gflachs/GreenPrompt_LLM_Registry/blob/main/src/app/models/__init__.py):** This file initializes the models module.
         - **[request.py](https://github.com/gflachs/GreenPrompt_LLM_Registry/blob/main/src/app/models/request.py):** This file defines data models for handling LLM deployment requests using Pydantic.
      - **[services](https://github.com/gflachs/GreenPrompt_LLM_Registry/blob/main/src/app/services):** This directory contains business logic and service classes for the application.
         - **[__init__.py](https://github.com/gflachs/GreenPrompt_LLM_Registry/blob/main/src/app/services/__init__.py):** This file initializes the services module.
         - **[llm_registry_service.py](https://github.com/gflachs/GreenPrompt_LLM_Registry/blob/main/src/app/services/llm_registry_service.py):** This module manages the deployment, stopping, and status tracking of LLM instances.
         - **[llm_wrapper_service.py](https://github.com/gflachs/GreenPrompt_LLM_Registry/blob/main/src/app/services/llm_wrapper_service.py):** This module handles the interaction with the LLM Wrapper, including deploying and stopping LLM instances.
         - **[llm_wrapper_status_service.py](https://github.com/gflachs/GreenPrompt_LLM_Registry/blob/main/src/app/services/llm_wrapper_status_service.py):** This module checks and updates the status of LLM Wrappers.
      - **[utils](https://github.com/gflachs/GreenPrompt_LLM_Registry/blob/main/src/app/utils/):** This directory contains utility functions and classes used across the application.
         - **[configreader.py](https://github.com/gflachs/GreenPrompt_LLM_Registry/blob/main/src/app/utils/configreader.py):** This file defines a singleton class for reading configuration settings from a file.
         - **[logger.py](https://github.com/gflachs/GreenPrompt_LLM_Registry/blob/main/src/app/utils/logger.py):** This file provides logging functionality for both console and file logging.
      - **[__init__.py](https://github.com/gflachs/GreenPrompt_LLM_Registry/tree/main/src/app/__init__.py):** This file initializes the app module.
      - **[main.py](https://github.com/gflachs/GreenPrompt_LLM_Registry/tree/main/src/app/main.py):** This is the main entry point for the application, setting up the FastAPI app and managing its lifecycle.
   - **[tests](https://github.com/gflachs/GreenPrompt_LLM_Registry/tree/main/tests/):** Contains unit tests for various functionalities of the project.
      - **[clients](https://github.com/gflachs/GreenPrompt_LLM_Registry/tree/main/tests/clients/):**
         - **[test_wrapper_client.py](https://github.com/gflachs/GreenPrompt_LLM_Registry/tree/main/tests/clients/test_wrapper_client.py):** Tests the deploy_llm and stop_llm functions by mocking HTTP requests and validating responses based on different status codes.
      - **[controller](https://github.com/gflachs/GreenPrompt_LLM_Registry/tree/main/tests/controller/):**
         - **[test_db_controller.py](https://github.com/gflachs/GreenPrompt_LLM_Registry/tree/main/tests/controller/test_db_controller.py):** Tests the LLMRegistryDbController singleton behavior, table creation, data insertion, and retrieval methods including handling of specific LLM wrapper and request statuses.
         - **[test_promptingservice_controller.py](https://github.com/gflachs/GreenPrompt_LLM_Registry/tree/main/tests/controller/test_promptingservice_controller.py):** Tests API endpoints of the promptingservice_controller by mocking service responses and validating request payloads and response statuses.
      - **[services](https://github.com/gflachs/GreenPrompt_LLM_Registry/tree/main/tests/services/):**
         - **[test_llm_wrapper_service.py](https://github.com/gflachs/GreenPrompt_LLM_Registry/tree/main/tests/services/test_llm_wrapper_service.py):** Tests the interaction with llm_wrapper_service by mocking the wrapper_client and ensuring correct deployment and stopping of LLM instances based on returned statuses.
         - **[test_llm_wrapper_status_service.py](https://github.com/gflachs/GreenPrompt_LLM_Registry/tree/main/tests/services/test_llm_wrapper_status_service.py):** Tests the check_status function by mocking the database controller and wrapper client, and validating the handling of different LLM wrapper statuses like ready, deploying, stopping, restarting, and failure.
         - **[test_llm_registry_service.py](https://github.com/gflachs/GreenPrompt_LLM_Registry/tree/main/tests/services/test_llm_registry_service.py):** Tests the llm_registry_service by mocking its methods and validating the deployment, stopping, and status tracking of LLM instances.
      - **[utils](https://github.com/gflachs/GreenPrompt_LLM_Registry/tree/main/tests/utils/):**
         - **[test_configreader.py](https://github.com/gflachs/GreenPrompt_LLM_Registry/tree/main/tests/utils/test_configreader.py):** Tests the ConfigReader singleton behavior and its ability to read configuration values using mocked configparser.
      - **[__init__.py](https://github.com/gflachs/GreenPrompt_LLM_Registry/tree/main/tests/__init__.py):** Initializes the tests module.
      - **[test_main.py](https://github.com/gflachs/GreenPrompt_LLM_Registry/tree/main/tests/test_main.py):** Tests the FastAPI application's startup and shutdown processes, including lifecycle hooks and endpoint responses.
- **[.gitignore](https://github.com/gflachs/GreenPrompt_LLM_Registry/blob/main/.gitignore):** Specifies files and directories that should be ignored by Git in order to avoid committing them to the repository.
- **[LICENSE](https://github.com/gflachs/GreenPrompt_LLM_Registry/blob/main/LICENSE):** Contains the MIT License text, granting permission to use, copy, modify, and distribute the software.
- **[llm_config.json](https://github.com/gflachs/GreenPrompt_LLM_Registry/blob/main/llm_config.json):**
- **[pytest.ini](https://github.com/gflachs/GreenPrompt_LLM_Registry/blob/main/pytest.ini):** Configuration file for pytest, specifying the paths to test modules and other settings.
- **[requirements.txt](https://github.com/gflachs/GreenPrompt_LLM_Registry/blob/main/requirements.txt):** Lists the dependencies required for the project, which can be installed using pip.
- **[sonar-project.properties](https://github.com/gflachs/GreenPrompt_LLM_Registry/blob/main/sonar-project.properties):** Configuration file for SonarQube, specifying project details and paths for source files, tests, and coverage reports. 

## Start the Service 

### Development
```sh
cd src/app
fastapi dev main.py
```

### Production
```sh
cd src/app
uvicorn main:app --host
```


## Contribution

Thank you for your interest in contributing to our project! To ensure the quality and consistency of our code, we kindly ask you to follow these guidelines.

### Branch Protection

- All changes must be made through **Pull Requests**.
- We have **branch protection**: at least **one review** from another person is required before changes can be merged.
- All **checks must pass** before a merge is allowed.
- Make sure your branch is **up to date** with the target branch to avoid merge conflicts.

### Code Quality

- **Linting and code quality** must meet the defined standards. We use tools like **flake8** (Python) or similar linters to ensure the code is clean and readable.
- Use **pre-commit hooks** to check compliance with the standards before committing your code.

### No New Bugs

- Ensure that your code does not introduce **new errors**. Run all relevant **unit tests** and extend the test suite if necessary.
- Make sure that **existing tests do not fail**. New changes must not affect existing functionality.

### Tests

- Each new feature should be covered with appropriate **unit tests** or **integration tests** (minimum coverage 70%).
- Run all tests to ensure that existing functionality is not affected.

### Documentation

- All changes to the code should be documented in **comments** and/or in the **README.md**, if they affect usage.
- Clearly explain **why** you made the changes so that other developers can understand the motivation behind them.

### Pull Request (PR) Description

- Each PR should contain a **clear description** of the changes made.
- Explain why the change is necessary and what problem it solves.
- Reference relevant **issues** (e.g., `Fixes #123`) if available.

### Style Guidelines

- Follow the established **code conventions** (e.g., PEP8 for Python code).
- Ensure that your code adheres to the project's style guidelines.

### Feedback and Reviews

- Be open to **feedback**. Reviews are part of the process to ensure the quality of the code.
- Take the time to respond to comments and make necessary changes.

### Summary

With these guidelines, we aim to ensure that the code remains easy to read and maintain for all team members. We greatly appreciate your contributions and look forward to your Pull Requests!
