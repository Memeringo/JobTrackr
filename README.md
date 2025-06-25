# JobTrackr

**JobTrackr** is a work-in-progress job application tracking API built with:

- Python (Flask)
- MongoDB
- Docker (eventually)
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
- (Planned) Update and delete job applications
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
  "title": "Software Engineer",
  "company": "Acme Corp",
  "status": "applied",
  "date_applied": "2025-06-23"
}
```

#### GET /jobs
Retrieves all job applications

#### GET /jobs/<id>
Retrieves a single job application by its ID