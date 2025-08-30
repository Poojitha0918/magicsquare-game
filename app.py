# import os
# from datetime import datetime, timezone
# from typing import Any, Dict, List

# from flask import Flask, jsonify, request, render_template
# from flask_cors import CORS
# from pymongo import MongoClient
# from dotenv import load_dotenv

# from magic import generate_puzzle, is_valid_solution, matches_given

# # ---------- Load .env ----------
# load_dotenv()

# # ---------- Flask App ----------
# app = Flask(__name__, template_folder="templates", static_folder="static")
# CORS(app)

# # ---------- MongoDB ----------
# MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
# DB_NAME   = os.getenv("MONGO_DB", "magicgame")

# def get_db():
#     """Connect to MongoDB (raises if unavailable)."""
#     client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
#     client.admin.command("ping")  # test connection
#     return client[DB_NAME]

# # ---------- Game config ----------
# DEFAULT_SIZES = [3, 5, 7, 9]

# def puzzle_id_for_size(n: int) -> str:
#     return f"{n}"

# def get_puzzle_record(n: int) -> Dict[str, Any]:
#     """Return deterministic puzzle so leaderboard makes sense."""
#     pid = puzzle_id_for_size(n)

#     if n == 3:
#         blank_ratio = 0.34
#     elif n == 5:
#         blank_ratio = 0.44
#     elif n == 7:
#         blank_ratio = 0.50
#     else:
#         blank_ratio = 0.55

#     puz = generate_puzzle(n, blank_ratio=blank_ratio, seed=n * 1009)
#     return {
#         "_id": pid,
#         "size": n,
#         "magic_constant": puz["magic_constant"],
#         "given": puz["given"],
#         "mask": puz["mask"],
#         "created_at": datetime.now(timezone.utc).isoformat(),
#     }

# # ---------- Routes ----------
# @app.route("/")
# def index():
#     return render_template("index.html")

# @app.get("/api/puzzles")
# def list_puzzles():
#     return jsonify([
#         {
#             "id": puzzle_id_for_size(n),
#             "size": n,
#             "magic_constant": n * (n*n + 1) // 2
#         }
#         for n in DEFAULT_SIZES
#     ])

# @app.get("/api/puzzle/<pid>")
# def fetch_puzzle(pid: str):
#     try:
#         n = int(pid)
#     except ValueError:
#         return jsonify({"error": "Invalid puzzle id"}), 400
#     if n < 3 or n % 2 == 0:
#         return jsonify({"error": "Only odd sizes >= 3 supported"}), 400

#     rec = get_puzzle_record(n)
#     return jsonify({
#         "id": rec["_id"],
#         "size": rec["size"],
#         "magic_constant": rec["magic_constant"],
#         "given": rec["given"],
#         "mask": rec["mask"],
#     })

# @app.post("/api/submit")
# def submit():
#     data = request.get_json(force=True, silent=True) or {}
#     username = (data.get("username") or "").strip() or "anon"
#     pid = data.get("puzzle_id")
#     solution: List[List[int]] = data.get("solution")
#     duration_ms = data.get("duration_ms")

#     # Basic validation
#     try:
#         n = int(pid)
#     except Exception:
#         return jsonify({"ok": False, "error": "Invalid puzzle_id"}), 400

#     rec = get_puzzle_record(n)
#     given = rec["given"]

#     if not isinstance(solution, list):
#         return jsonify({"ok": False, "error": "solution must be 2D list"}), 400
#     if len(solution) != n or any(len(row) != n for row in solution):
#         return jsonify({"ok": False, "error": "Wrong dimensions"}), 400
#     if not matches_given(solution, given):
#         return jsonify({"ok": False, "error": "Does not respect given clues"}), 200
#     if not is_valid_solution(solution):
#         return jsonify({"ok": False, "error": "Not a valid magic square"}), 200

#     try:
#         duration_ms = int(duration_ms)
#     except Exception:
#         duration_ms = None

#     # Connect to Mongo
#     try:
#         db = get_db()
#     except Exception as e:
#         return jsonify({"ok": False, "error": f"MongoDB not available: {e}"}), 503

#     users = db["users"]
#     lb = db["leaderboard"]

#     # Upsert user
#     users.update_one(
#         {"username": username},
#         {"$setOnInsert": {
#             "username": username,
#             "joined_at": datetime.now(timezone.utc).isoformat()
#         }},
#         upsert=True
#     )

#     entry = {
#         "puzzle_id": str(n),
#         "username": username,
#         "duration_ms": duration_ms if duration_ms is not None else None,
#         "submitted_at": datetime.now(timezone.utc).isoformat()
#     }

#     # Keep best (lowest) duration per user/puzzle
#     existing = lb.find_one({"puzzle_id": str(n), "username": username})
#     if duration_ms is not None:
#         if existing is None or duration_ms < existing.get("duration_ms", 1 << 60):
#             lb.update_one(
#                 {"puzzle_id": str(n), "username": username},
#                 {"$set": entry},
#                 upsert=True
#             )
#     else:
#         lb.insert_one(entry)

#     # Rank (only when timed)
#     rank = None
#     if duration_ms is not None:
#         better = lb.count_documents({"puzzle_id": str(n), "duration_ms": {"$lt": duration_ms}})
#         rank = better + 1

#     return jsonify({"ok": True, "rank": rank, "message": "Submitted successfully"})

# @app.get("/api/leaderboard")
# def leaderboard():
#     pid = request.args.get("puzzle_id", "3")
#     limit = int(request.args.get("limit", "10"))

#     try:
#         db = get_db()
#     except Exception:
#         return jsonify([])

#     lb = db["leaderboard"]
#     cur = lb.find({"puzzle_id": pid, "duration_ms": {"$ne": None}}).sort("duration_ms", 1).limit(limit)
#     items = [{
#         "username": d.get("username", "anon"),
#         "duration_ms": d.get("duration_ms"),
#         "submitted_at": d.get("submitted_at")
#     } for d in cur]
#     return jsonify(items)

# @app.get("/health")
# def health():
#     ok = True
#     try:
#         _ = get_db()
#     except Exception:
#         ok = False
#     return jsonify({"status": "ok" if ok else "degraded"})

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=int(os.getenv("PORT", 9000)), debug=False)


import os
from datetime import datetime
from typing import Any, Dict, List

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv  # NEW

from magic import generate_puzzle, is_valid_solution, matches_given

# ---------- Load .env ----------
load_dotenv()  # will read .env file in project root

# ---------- Flask App ----------
app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# ---------- MongoDB ----------
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME   = os.getenv("MONGO_DB", "magicgame")

def get_db():
    """Create client lazily so app can start even if mongod spins up a bit later."""
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    client.admin.command("ping")  # will raise if unreachable
    return client[DB_NAME]

# ---------- Game config ----------
DEFAULT_SIZES = [3, 5, 7, 9]   # UI will show whatever you list here

def puzzle_id_for_size(n: int) -> str:
    return f"{n}"

def get_puzzle_record(n: int) -> Dict[str, Any]:
    """Deterministic puzzle (same each restart) so leaderboard is meaningful."""
    pid = puzzle_id_for_size(n)

    if n == 3:
        blank_ratio = 0.34
    elif n == 5:
        blank_ratio = 0.44
    elif n == 7:
        blank_ratio = 0.50
    else:
        blank_ratio = 0.55

    puz = generate_puzzle(n, blank_ratio=blank_ratio, seed=n * 1009)
    return {
        "_id": pid,
        "size": n,
        "magic_constant": puz["magic_constant"],
        "given": puz["given"],
        "mask": puz["mask"],
        "created_at": datetime.utcnow().isoformat(),
    }

# ---------- Routes ----------
@app.route("/")
def index():
    return render_template("index.html")

@app.get("/api/puzzles")
def list_puzzles():
    return jsonify([
        {
            "id": puzzle_id_for_size(n),
            "size": n,
            "magic_constant": n * (n*n + 1) // 2
        }
        for n in DEFAULT_SIZES
    ])

@app.get("/api/puzzle/<pid>")
def fetch_puzzle(pid: str):
    try:
        n = int(pid)
    except ValueError:
        return jsonify({"error": "Invalid puzzle id"}), 400
    if n < 3 or n % 2 == 0:
        return jsonify({"error": "Only odd sizes >= 3 supported"}), 400

    rec = get_puzzle_record(n)
    return jsonify({
        "id": rec["_id"],
        "size": rec["size"],
        "magic_constant": rec["magic_constant"],
        "given": rec["given"],
        "mask": rec["mask"],
    })

@app.post("/api/submit")
def submit():
    data = request.get_json(force=True, silent=True) or {}
    username = (data.get("username") or "").strip() or "anon"
    pid = data.get("puzzle_id")
    solution: List[List[int]] = data.get("solution")
    duration_ms = data.get("duration_ms")

    # Basic validation
    try:
        n = int(pid)
    except Exception:
        return jsonify({"ok": False, "error": "Invalid puzzle_id"}), 400

    rec = get_puzzle_record(n)
    given = rec["given"]

    if not isinstance(solution, list):
        return jsonify({"ok": False, "error": "solution must be 2D list"}), 400
    if len(solution) != n or any(len(row) != n for row in solution):
        return jsonify({"ok": False, "error": "Wrong dimensions"}), 400
    if not matches_given(solution, given):
        return jsonify({"ok": False, "error": "Does not respect given clues"}), 200
    if not is_valid_solution(solution):
        return jsonify({"ok": False, "error": "Not a valid magic square"}), 200

    try:
        duration_ms = int(duration_ms)
    except Exception:
        duration_ms = None

    # Connect to Mongo
    try:
        db = get_db()
    except Exception as e:
        return jsonify({"ok": False, "error": f"MongoDB not available: {e}"}), 503

    users = db["users"]
    lb = db["leaderboard"]

    # Upsert user (stores first-seen timestamp)
    users.update_one(
        {"username": username},
        {"$setOnInsert": {"username": username, "joined_at": datetime.utcnow().isoformat()}},
        upsert=True
    )

    entry = {
        "puzzle_id": str(n),
        "username": username,
        "duration_ms": duration_ms if duration_ms is not None else None,
        "submitted_at": datetime.utcnow().isoformat()
    }

    # Keep best (lowest) duration per user/puzzle where timing is present
    existing = lb.find_one({"puzzle_id": str(n), "username": username})
    if duration_ms is not None:
        if existing is None or duration_ms < existing.get("duration_ms", 1 << 60):
            lb.update_one(
                {"puzzle_id": str(n), "username": username},
                {"$set": entry},
                upsert=True
            )
    else:
        lb.insert_one(entry)

    # Rank (only when timed)
    rank = None
    if duration_ms is not None:
        better = lb.count_documents({"puzzle_id": str(n), "duration_ms": {"$lt": duration_ms}})
        rank = better + 1

    return jsonify({"ok": True, "rank": rank, "message": "Submitted successfully"})

@app.get("/api/leaderboard")
def leaderboard():
    pid = request.args.get("puzzle_id", "3")
    limit = int(request.args.get("limit", "10"))

    try:
        db = get_db()
    except Exception:
        return jsonify([])

    lb = db["leaderboard"]
    cur = lb.find({"puzzle_id": pid, "duration_ms": {"$ne": None}}).sort("duration_ms", 1).limit(limit)
    items = [{
        "username": d.get("username", "anon"),
        "duration_ms": d.get("duration_ms"),
        "submitted_at": d.get("submitted_at")
    } for d in cur]
    return jsonify(items)

@app.get("/health")
def health():
    ok = True
    try:
        _ = get_db()
    except Exception:
        ok = False
    return jsonify({"status": "ok" if ok else "degraded"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 9000)), debug=False)
