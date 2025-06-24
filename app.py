from doctest import debug

from flask import jsonify, Flask

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"message":"JobTrackr is live!"})

if __name__ == "__main__":
    app.run(debug = True)
