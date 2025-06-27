# JobTrackr

**JobTrackr** is a work-in-progress job application tracking API built with:

- Python (Flask)
- MongoDB
- Docker 
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
- Add new job applications
- View all job applications
- View a single job application by ID
- Runs MongoDB in a Docker container for easy setup

---

### Setup Instructions

#### Prerequisites
- Python 3.x installed  
- Docker installed and running  
- Git installed



#### Clone the repo
```bash
git clone https://github.com/Memeringo/JobTrackr.git
cd JobTrackr
```
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

### API Endpoints

#### POST /jobs
Creates a new job application
#### Body Example:
 ```json
{
  "position": "Software Engineer",
  "company": "Acme Corp",
  "status": "applied",
  "date_applied": "2025-06-23"
}
```

#### GET /jobs
Retrieves all job applications

#### GET /jobs/<id>
Retrieves a single job application by its ID

#### PUT /jobs/<id>
Updates a job application by ID.  
Only the fields `company`, `position`, and `status` can be updated.
#### Body Example:
```json
{
  "company": "New Company Name",
  "position": "Senior Developer",
  "status": "interview"
}
```

---

### Error Handling

The API returns errors in JSON format, for example:

- `400 Bad Request`  
  When input data is missing, invalid, or the ID format is incorrect.
#### Example error response:
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

---

### Work In Progress (WIP)

- [x] Update job application
- [x] Basic error handling with JSON responses
- [ ] Delete job application
- [ ] Swagger/OpenAPI documentation
- [ ] Dockerize full application (not just MongoDB)
- [ ] Authentication (optional)
- [ ] Connect to Gmail API (experimental)