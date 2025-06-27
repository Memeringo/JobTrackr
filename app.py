
import os
from bson.objectid import ObjectId
from flask import jsonify, Flask, request, abort
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Initialize Flask application
app = Flask(__name__)

# Connect to MongoDB using URI from environment variable
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client.get_database() # Gets the default database defined in the URI

# Custom error handler for 400 Bad Request – returns JSON instead of HTML
@app.errorhandler(400)
def bad_request(error):
    response = jsonify({"error": error.description})
    response.status_code = 400
    return response

# Custom error handler for 404 Not Found – returns JSON instead of HTML
@app.errorhandler(404)
def not_found(error):
    response = jsonify({"error": error.description})
    response.status_code = 404
    return response

# Root route – confirms that the API is live
@app.route("/")
def home():
    return jsonify({"message":"JobTrackr is live!"})

# Test route – lists all MongoDB collection names
@app.route("/test-mongo")
def test_mongo():
    collections = db.list_collection_names()
    return jsonify({"collections": collections})

# POST /jobs – Creates a new job application
@app.route("/jobs", methods=["POST"])
def add_job():
    data = request.get_json()

    # Ensure required fields are present
    required_fields = ["company", "position", "status"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    # Create job document with optional date_applied or current timestamp
    job = {
        "company": data["company"],
        "position": data["position"],
        "status": data["status"],
        "date_applied": data.get("date_applied", datetime.now().strftime("%Y-%m-%d %H:%M"))
    }

    # Insert job into MongoDB and return the full document with generated ID
    result = db.jobs.insert_one(job)
    job["_id"] = str(result.inserted_id)
    return jsonify(job), 201

# GET /jobs – Returns all job applications
@app.route("/jobs", methods=["GET"])
def get_jobs():
    jobs = list(db.jobs.find())

    # Convert Mongo ObjectIds to strings for JSON serialization
    for job in jobs:
        job["_id"] = str(job["_id"])

    return jsonify(jobs), 200

# GET /jobs/<job_id> – Returns a specific job by ID
@app.route("/jobs/<job_id>", methods=["GET"])
def get_job(job_id):
    try:
        job = db.jobs.find_one({"_id": ObjectId(job_id)})
    except Exception:
        # If ObjectId conversion fails, return 400 error
        abort(400, description = "Invalid ID Format")

    if job is None:
        # If no job found with the given ID
        abort(404, description = "Job Not Found")

    job["_id"] = str(job["_id"])
    return jsonify(job), 200

# PUT /jobs/<job_id> – Updates a job application
@app.route("/jobs/<job_id>", methods=["PUT"])
def update_job(job_id):
    try:
        job_object_id = ObjectId(job_id)
    except Exception:
        abort(400, description = "Invalid ID Format")

    data = request.get_json()
    if not data:
        return jsonify({"error": "No update data provided"}), 400

    # Define which fields can be updated
    allowed_fields = {"company", "position", "status"}
    update_fields = {}

    # Filter only allowed fields
    for key, value in data.items():
        if key in allowed_fields:
            update_fields[key] = value
        else:
            return jsonify({"error":f"Field'{key}' is not allowed to be updated"})

    if not update_fields:
        return jsonify({"error": "No valid fields provided to update"}), 400

    # Perform update
    result = db.jobs.update_one(
        {"_id": job_object_id},
        {"$set": update_fields}
    )

    if result.matched_count == 0:
        abort(404, description = "Job not found")

    # Return updated job
    updated_job = db.jobs.find_one({"_id": job_object_id})
    updated_job["_id"] = str(updated_job["_id"])
    return jsonify(updated_job), 200

# Start the Flask development server
if __name__ == "__main__":
    app.run(debug = True)
