#!/bin/bash

alembic upgrade head
gunicorn src.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000

## скрипт для запуска миграции и сервера