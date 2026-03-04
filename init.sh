#!/bin/bash
source venv/bin/activate
./db_connect.sh
./duckdns.sh
uvicorn main:app --host 0.0.0.0 --port 8000
