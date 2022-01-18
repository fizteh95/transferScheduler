#!/bin/sh

sleep 5
python migrator.py
uvicorn scheduler.scheduler:app --host 0.0.0.0
