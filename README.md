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
3. [Start the Service](#start-the-service)
4. [Contribution](#contribution)

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

```sh
pip install -r requirements.txt
```

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
