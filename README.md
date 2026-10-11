# Healthcare Backend API

A RESTful backend for a healthcare application built with Django REST Framework and PostgreSQL. It provides JWT-based authentication, patient and doctor management, and patient-doctor assignments through structured API endpoints.

The project demonstrates API development, authentication, data validation, database integration, and endpoint testing using Postman.

## Features

- User registration and login with JWT authentication.
- Patient CRUD operations with user-based ownership.
- Doctor CRUD operations.
- Patient-doctor assignment and removal.
- Input validation and consistent API error responses.
- PostgreSQL database integration using Django ORM.
- Postman collection for endpoint testing.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.10+ | Backend programming |
| Django 5.2 | Web framework |
| Django REST Framework | REST API development |
| SimpleJWT | JWT authentication |
| PostgreSQL | Relational database |
| psycopg2-binary | PostgreSQL adapter |
| python-dotenv | Environment variable loading |
| Postman | API testing |

## Project Structure

```text
healthcare_backend/
├── config/          # Django settings and root URLs
├── accounts/        # Registration and login
├── patients/        # Patient models, serializers and views
├── doctors/         # Doctor models, serializers and views
├── mappings/        # Patient-doctor assignments
├── postman/         # Postman collection
├── screenshots/     # API testing evidence
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Prerequisites

- Python 3.10 or newer
- PostgreSQL 13 or newer
- pip
- Postman
- Git (optional, for version control)

## Local Setup

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd healthcare_backend
```

If you already have the project locally, open its root folder in VS Code and continue.

### 2. Create a virtual environment

**Windows PowerShell:**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt:

```bat
venv\Scripts\activate.bat
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure PostgreSQL

Create a PostgreSQL database and a dedicated database user. For example, using the PostgreSQL command-line client:

```sql
CREATE USER healthcare_user WITH PASSWORD 'choose-a-password' CREATEDB;
CREATE DATABASE healthcare_db OWNER healthcare_user;
```

The `CREATEDB` privilege is needed if your test configuration creates a temporary PostgreSQL database.

### 5. Configure environment variables

Copy the example environment file:

```powershell
Copy-Item .env.example .env
```

Update `.env` with your local configuration:

```dotenv
SECRET_KEY=replace-with-a-generated-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=healthcare_db
DB_USER=healthcare_user
DB_PASSWORD=your-database-password
DB_HOST=localhost
DB_PORT=5432
```

Use the variable names expected by your Django settings. Keep `.env` out of version control, and never publish real credentials or secret keys.

Generate a Django secret key with:

```bash
python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
```

### 6. Apply database migrations

```bash
python manage.py migrate
```

### 7. Start the development server

```bash
python manage.py runserver
```

The local API base URL is:

`http://127.0.0.1:8000/`

## Authentication

### Register a user

**POST** `/api/auth/register/`

Example request:

```json
{
  "name": "Alice Smith",
  "email": "alice@example.com",
  "password": "Use-A-Strong-Password-Here"
}
```

### Log in

**POST** `/api/auth/login/`

Example request:

```json
{
  "email": "alice@example.com",
  "password": "Use-A-Strong-Password-Here"
}
```

The login response contains access and refresh tokens.

For protected endpoints, select **Authorization → Bearer Token** in Postman and provide the access token.

Do not commit real access tokens, refresh tokens, passwords, or API credentials.

## API Reference

All endpoints below use the `/api/` prefix. Protected endpoints require a valid access token.

### Authentication

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/api/auth/register/` | Register a user | No |
| POST | `/api/auth/login/` | Log in and obtain JWT tokens | No |

### Patients

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/patients/` | Create a patient |
| GET | `/api/patients/` | List the authenticated user's patients |
| GET | `/api/patients/<id>/` | Retrieve a patient |
| PUT | `/api/patients/<id>/` | Update a patient |
| DELETE | `/api/patients/<id>/` | Delete a patient |

### Doctors

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/doctors/` | Create a doctor |
| GET | `/api/doctors/` | List doctors |
| GET | `/api/doctors/<id>/` | Retrieve a doctor |
| PUT | `/api/doctors/<id>/` | Update a doctor |
| DELETE | `/api/doctors/<id>/` | Delete a doctor |

### Patient-Doctor Mappings

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/mappings/` | Assign a doctor to a patient |
| GET | `/api/mappings/` | List the user's patient-doctor mappings |
| GET | `/api/mappings/<patient_id>/` | Retrieve mappings for a patient |
| DELETE | `/api/mappings/<id>/` | Remove a mapping by its ID |

## Example Request Bodies

### Create a patient

**POST** `/api/patients/`

```json
{
  "name": "Patient One",
  "age": 30,
  "gender": "male",
  "address": "Chennai"
}
```

Valid gender values are `male`, `female`, and `other`.

### Create a doctor

**POST** `/api/doctors/`

```json
{
  "name": "Dr. Ravi Kumar",
  "specialization": "Cardiology",
  "email": "dr.ravi@example.com",
  "phone": "9876543210"
}
```

### Assign a doctor to a patient

**POST** `/api/mappings/`

```json
{
  "patient": 1,
  "doctor": 1
}
```

Use patient and doctor IDs that exist in your database and that the authenticated user is authorized to access.

## Testing with Postman

1. Start the Django development server.
2. Import `postman/healthcare_backend.postman_collection.json` into Postman.
3. Run the authentication requests first.
4. Verify that the collection stores the access token.
5. Run the patient, doctor, and mapping requests.
6. Check successful responses and expected error cases.

The collection is intended to cover endpoint functionality, authentication, validation, and common failure scenarios.

## Screenshots

Screenshots from the API testing workflow can be stored in the `screenshots/` folder.

Add the following images using these filenames if they match the screenshots you captured:

### 1. User Registration

<img width="1548" height="964" alt="01-registration-success" src="https://github.com/user-attachments/assets/88a109f3-6202-4ac8-8255-0561129d2d37" />

### 2. JWT Login

<img width="1534" height="943" alt="02-login-jwt-tokens" src="https://github.com/user-attachments/assets/6b0ccd13-d1a0-4409-a5f7-d6bfd447c23f" />

### 3. Patient Creation

<img width="1543" height="936" alt="03-patient-creation-success" src="https://github.com/user-attachments/assets/206c7d2e-b0b9-444a-b80f-cde26decb155" />

### 4. Doctor Creation

<img width="1554" height="972" alt="04-doctor-creation-success" src="https://github.com/user-attachments/assets/2943524e-6572-4028-9897-9ec305685ab4" />

### 5. Patient-Doctor Mapping

<img width="1545" height="973" alt="05-patient-doctor-mapping-retrieval" src="https://github.com/user-attachments/assets/d2813b64-5560-4e22-b530-aae36f8e489c" />


## Error Handling

The API uses appropriate HTTP status codes for successful requests and common failures. Depending on the endpoint and failure, responses may include:

| Status | Meaning |
|---|---|
| 200 | Request successful |
| 201 | Resource created |
| 204 | Resource deleted |
| 400 | Invalid request data |
| 401 | Missing or invalid authentication |
| 403 | Permission denied |
| 404 | Resource not found |
| 405 | HTTP method not allowed |

## Implementation Notes

- User registration and login use the configured Django authentication model and JWT authentication.
- Patient records are associated with their creator.
- Patient access and mapping operations are restricted according to the configured ownership permissions.
- Doctor visibility and modification follow the implemented API permissions.
- Database operations use Django ORM.
- Sensitive configuration is supplied through environment variables.

## Automated Tests

Run the project's Django tests with:

```bash
python manage.py test
```

The test database configuration must be compatible with your PostgreSQL setup.

## Security Notes

- Never commit `.env` or production credentials.
- Use a strong, unique Django secret key.
- Disable `DEBUG` in production.
- Configure `ALLOWED_HOSTS` appropriately before deployment.
- Use HTTPS and securely managed secrets in production.

