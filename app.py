from doctest import debug
import os
from flask import jsonify, Flask, request
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()

app = Flask(__name__)

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client.get_database()

@app.route("/")
def home():
    return jsonify({"message":"JobTrackr is live!"})

@app.route("/test-mongo")
def test_mongo():
    collections = db.list_collection_names()
    return jsonify({"collections": collections})

@app.route("/jobs", methods=["POST"])
def add_job():
    data = request.get_json()

    required_fields = ["company", "position", "status"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    job = {
        "company": data["company"],
        "position": data["position"],
        "status": data["status"],
        "date_applied": data.get("date_applied", datetime.utcnow().strftime("%Y-%m-%d %H:%M"))
    }

    result = db.jobs.insert_one(job)
    job["_id"] = str(result.inserted_id)
    return jsonify(job), 201

@app.route("/jobs", methods=["GET"])
def get_jobs():
    jobs = list(db.jobs.find())

    for job in jobs:
        job["_id"] = str(job["_id"])

    return jsonify(jobs), 200

if __name__ == "__main__":
    app.run(debug = True)
