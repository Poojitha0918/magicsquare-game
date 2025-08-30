# Project Outline

## Goal
A web-based Magic Square puzzle platform. Supports odd-order boards (3×3, 5×5, ...). Players solve puzzles in the browser, and the backend validates and tracks leaderboards.

## Core Components
- **Flask API**: puzzle catalog, retrieve puzzle, submit solutions, leaderboard, health.
- **Magic Engine (magic.py)**: Siamese generator, mask generator, validator.
- **Frontend**: simple vanilla JS app with timer and submission.
- **Data Store**: MongoDB for puzzles and leaderboard.
- **Docker**: app + MongoDB via docker-compose.
- **CI/CD**: GitHub Actions to run tests and push image to GHCR.

## Stretch
- User accounts and auth
- More mask strategies (difficulty levels)
- Hints and cell validation feedback
