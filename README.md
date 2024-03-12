# WheatNet API

## Introduction
WheatNet API is a service designed to classify wheat diseases from images. It utilizes pre-trained deep learning models to classify images into five classes: septoria, brown rust, yellow rust, mildew, and healthy. This API provides endpoints for user management, authentication, image upload, image diagnosis, and analytics reporting.

## Endpoints

### User Management
- **POST /users/create-user:** Create a new user.
- **GET /users/get-user:** Get user details.
- **GET /users/get-users:** Get a list of all users.
- **GET /users/get-user-fullname:** Get the full name of a user.
- **PUT /users/update-profile:** Update user profile.
- **PUT /users/update-password:** Update user password.
- **PUT /users/request-password-reset:** Request OTP for password reset.

### Authentication
- **POST /auth/login:** Login to obtain an access token.

### Diagnosis
- **POST /diagnosis/upload-image:** Upload a single image for diagnosis.
- **POST /diagnosis/upload-images:** Upload multiple images for diagnosis.
- **POST /diagnosis/diagnose-on-upload:** Diagnose uploaded images automatically.
- **PUT /diagnosis/update-manual-diagnosis:** Update manual diagnosis for an image.
- **GET /diagnosis/get-diagnoses:** Get a list of all diagnoses.

### Analytics
- **GET /analytics/get-diagnosis-report:** Get a report of diagnoses.
- **GET /analytics/get-system-report:** Get a report of the system.

## Technologies Used

This application utilizes the following technologies:

- **FastAPI**: A modern web framework for building APIs with Python.
- **Pydantic**: A data validation and settings management library for Python using Python type annotations.
- **JWT**: JSON Web Tokens for secure authentication.
- **SQLAlchemy**: A SQL toolkit and Object-Relational Mapping (ORM) library for database operations.
- **PyTorch**: A machine learning framework used for image classification tasks.


## Setup

Ensure you have Python installed. Clone the repository and navigate to the project directory. Then, install the required dependencies using pip:

```bash

pip install -r requirements.txt
```


## Running the Application
To start the application, run the following command:

```bash
uvicorn app.main:app --reload
```



