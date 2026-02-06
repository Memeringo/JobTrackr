
import os
from bson.errors import InvalidId
from bson.objectid import ObjectId
from flask import jsonify, Flask, request, abort
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

# Load environment variables from .env file
load_dotenv()

# Initialize Flask application
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-secret")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(
    minutes=int(os.getenv("ACCESS_TOKEN_EXPIRES_MIN", "60"))
)
jwt = JWTManager(app)

# Connect to MongoDB using URI from environment variable
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client.get_database() # Gets the default database defined in the URI

# -----------------------------
# Helpers
# -----------------------------

#Parse ObjectId or abort 400 with JSON.
def parse_object_id(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError):
        abort(400, description="Invalid ID Format")

#Read JWT identity (string) and convert to ObjectId.
def current_user_object_id() -> ObjectId:
    identity = get_jwt_identity()
    try:
        return ObjectId(identity)
    except (InvalidId, TypeError):
        # This would indicate a bad token identity format
        abort(422, description="Invalid token identity")

#Convert Mongo job doc into JSON-safe dict.
def serialize_job(job: dict) -> dict:
    job["_id"] = str(job["_id"])
    if "user_id" in job:
        # you can delete this instead if you don't want to expose it
        job["user_id"] = str(job["user_id"])
    return job


# -----------------------------
# JSON error handlers
# -----------------------------

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

@app.errorhandler(422)
def unprocessable_entity(error):
    response = jsonify({"error": error.description})
    response.status_code = 422
    return response

# -----------------------------
# JWT error handlers
# -----------------------------

@jwt.unauthorized_loader
def jwt_missing_token(reason):
    return jsonify({"error": "missing_token", "message": reason}), 401


@jwt.invalid_token_loader
def jwt_invalid_token(reason):
    return jsonify({"error": "invalid_token", "message": reason}), 422


@jwt.expired_token_loader
def jwt_expired_token(jwt_header, jwt_payload):
    return jsonify({"error": "token_expired", "message": "Token has expired"}), 401


@jwt.revoked_token_loader
def jwt_revoked_token(jwt_header, jwt_payload):
    return jsonify({"error": "token_revoked", "message": "Token has been revoked"}), 401

# -----------------------------
# Routes
# -----------------------------

# Creates a new user with hashed password
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    # Check if user already exists
    if db.users.find_one({"username": username}):
        return jsonify({"error": "User already exists"}), 400

    hashed_pw = generate_password_hash(password)
    res = db.users.insert_one({"username": username, "password": hashed_pw})
    return jsonify({"message": "User registered", "user_id": str(res.inserted_id)}), 201

@app.route("/login", methods=["POST"])
def login():

    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    user = db.users.find_one({"username": username})
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid credentials"}), 401

    # Put the user's id as the token identity
    access_token = create_access_token(identity=str(user["_id"]))
    return jsonify({"access_token": access_token}), 200

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

#DELETE /jobs/<job_id> – Deletes a job application
@app.route("/jobs/<job_id>", methods=["DELETE"])
def delete_job(job_id):
    try:
        job_object_id = ObjectId(job_id)
    except Exception:
        abort(400, description = "Invalid ID Format")

    result = db.jobs.delete_one({"_id": job_object_id})

    if result.deleted_count == 0:
        abort(404, description = "Job not found")

    return jsonify({"message": "Job deleted successfully"}), 200

# Start the Flask development server
if __name__ == "__main__":
    app.run(debug = True)
