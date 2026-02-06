# JobTrackr

**JobTrackr** is a work-in-progress job application tracking API built with:

- Python (Flask)
- MongoDB
- Docker + Docker Compose
- RESTful API

---

### Project Status

This project is currently in active development.  
Features and full documentation will be added soon.

---

### Goals

- Track job applications
- Learn Flask + MongoDB
- Practice REST APIs, version control, and deployment

---

### Features
- User registration and login (JWT authentication)
- Add new job applications
- View all job applications
- View a single job application by ID
- Update and delete job applications
- Runs MongoDB in a Docker container for easy setup

---

### Setup Instructions

#### Prerequisites
- Python 3.x installed *(only for development or testing outside containers)*  
- Docker installed and running  
- Git installed



#### Clone the Repository
```bash
git clone https://github.com/Memeringo/JobTrackr.git
cd JobTrackr
```
#### Run Entire App with Docker Compose
```bash
docker-compose up --build
```
The API will be available at:
http://localhost:5000

### Running Flask manually (Alternative):

#### Install Dependencies
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.\.venv\Scripts\activate   # Windows PowerShell
pip install -r requirements.txt
```

#### Run the Flask App
```bash
python app.py
```
Flask will start on http://127.0.0.1:5000
#### Run MongoDB with Docker
```bash
docker run -d -p 27017:27017 --name jobtrackr-mongo mongo
```


---

### Authentication (JWT)

JobTrackr uses JSON Web Tokens (JWT) for authentication.

#### Register
Create a new user account:

`POST /register`

Body:
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

#### Login
Authenticate and receive an access token:

`POST /login`

Body:
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

Response:
```json
{
  "access_token": "JWT_TOKEN_HERE"
}
```
---

### API Endpoints

### API Overview

| Endpoint        | Method | Auth | Description                         | Parameters |
|----------------|--------|------|-------------------------------------|------------|
| `/register`     | POST   | No   | Register a new user                 | `username`, `password` |
| `/login`        | POST   | No   | Login and get JWT token             | `username`, `password` |
| `/jobs`         | POST   | No   | Create a new job application        | `position`, `company`, `status`, `date_applied` *(optional)* |
| `/jobs`         | GET    | No   | Retrieve all job applications       | None |
| `/jobs/:id`     | GET    | No   | Retrieve a job by ID                | `id` (MongoDB ObjectId) |
| `/jobs/:id`     | PUT    | No   | Update a job application            | `company`, `position`, `status` |
| `/jobs/:id`     | DELETE | No   | Delete a job application            | `id` (MongoDB ObjectId) |
---

### Error Handling

The API returns errors in JSON format, for example:

- `400 Bad Request`  
  When input data is missing, invalid, or the ID format is incorrect.

```json
{
  "error": "Invalid ID Format"
}
```
- `404 Not Found`  
  When a job with the specified ID does not exist.
```json
{
  "error": "Job Not Found"
}
```
- `401 Unauthorized`  
  When authentication is missing or the token has expired.

```json
{
  "error": "missing_token",
  "message": "Missing Authorization Header"
}
```

- `422 Unprocessable Entity`

  When the token is invalid.

```json
{
  "error": "invalid_token",
  "message": "Signature verification failed"
}
```

---

### Work In Progress (WIP)

- [x] Update job application
- [x] Basic error handling with JSON responses
- [x] Delete job application
- [x] Docker Compose setup for both API and MongoDB
- [x] Authentication (JWT)
- [ ] Protect routes with authentication
- [ ] Per-User Job Ownership
- [ ] Connect to Gmail API (experimental)
- [ ] Swagger/OpenAPI documentation