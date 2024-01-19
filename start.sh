#!/bin/bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
gunicorn -b 0.0.0.0:8000 -k uvicorn.workers.UvicornWorker api:app