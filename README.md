# Magic Square Game (Flask + Vanilla JS)

Solve odd-order magic squares (3×3, 5×5, 7×7, 9×9, …). Same sum for rows, columns, and diagonals. Frontend talks to a Flask API. MongoDB stores puzzles and leaderboard.

## Quick Start (Local)

### Prereqs
- Python 3.11+
- Node not required (vanilla JS)
- MongoDB (or use mock db in tests)

```bash
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
export MONGO_MOCK=1  # optional for local dev without Mongo
python app.py
# open http://localhost:5000
```

## With Docker Compose

```bash
docker compose up --build
# App: http://localhost:5000  | MongoDB: localhost:27017
```

## API Endpoints

- `GET /api/puzzles` – list available puzzle sizes/IDs
- `GET /api/puzzle/<id>` – fetch puzzle (odd `id` like 3,5,7)
- `POST /api/submit` – `{ username, puzzle_id, solution, duration_ms }`
- `GET /api/leaderboard?puzzle_id=3&limit=10`
- `GET /health`

## Tests

```bash
pytest -q
```

Tests use `MONGO_MOCK=1` to avoid a real database.

## CI/CD

GitHub Actions workflow:
- Run unit tests (magic logic + API)
- On pushes to `main`, build and push Docker image to GHCR (`ghcr.io/<owner>/<repo>:latest`).

## Notes

- Magic squares generated via Siamese method for odd `n`.
- Masking hides a portion of cells (roughly 34% for 3×3, 44% for 5×5) to create the puzzle.
- Leaderboard stores best (lowest) `duration_ms` per user per puzzle.
