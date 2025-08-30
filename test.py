from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Load Mongo URI & DB name from .env
mongo_uri = os.getenv("MONGO_URI")
db_name = os.getenv("DB_NAME")

client = MongoClient(mongo_uri)
db = client[db_name]   # database = magicgame
scores_collection = db["magicgame"]   # collection = magicgame

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    data = request.json
    try:
        doc = {
            "name": data["name"],
            "time": data["time"],
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        scores_collection.insert_one(doc)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    scores = list(scores_collection.find({}, {"_id": 0}))
    return jsonify(scores)

if __name__ == "__main__":
    app.run(port=9000, debug=True)
