#!/usr/bin/env bash
# Start both backend and frontend for development

trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

echo "Starting Backend on http://localhost:8000 ..."
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload &

echo "Starting Frontend on http://localhost:5173 ..."
(cd frontend && npm run dev) &

wait
