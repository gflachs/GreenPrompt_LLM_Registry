# LLM Registry Service

## Table of Content
1. [Purpose](#purpose)
2. [Setup](#setup)
3. [Contribution](#contribution)

## Purpose

This Service provides LLMS via an API. It is part of the Greenprompt project. The service registry is a central component of the Greenprompt project. It is responsible for managing the lifecycle of the LLMWrappers and providing information about the currently deployed LLMS to the other components of the Greenprompt project.

It knows which machines are available, spawns LLMWrapper on them and manages the LLMS, which are running inside the LLMWrappers. The service registry is also responsible for providing information about the currently deployed LLMS to the other components of the Greenprompt project.

## Architecture

[![Components](https://tinyurl.com/2dml8ap9)](https://tinyurl.com/2dml8ap9)<!--![Components](./docs/architecture/components.puml)-->
[![Sequenz](https://tinyurl.com/2dcbntvl)](https://tinyurl.com/2dcbntvl)<!--![Sequenz](./docs/architecture/sequenz.puml)-->
[![Activity](https://tinyurl.com/2cxpee47)](https://tinyurl.com/2cxpee47)<!--![Activity](./docs/architecture/activity.puml)-->

### Communication with the Promtingservice
<!--![Communication with the Promtingservice](./docs/architecture/promptingservice_workflow.puml)-->

## Setup

```sh
pip install -r requirements.txt
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