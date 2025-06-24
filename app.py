from doctest import debug
import os
from flask import jsonify, Flask
from pymongo import MongoClient
from dotenv import load_dotenv


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

if __name__ == "__main__":
    app.run(debug = True)
