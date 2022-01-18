#!/bin/sh

sleep 15
uvicorn TgSender.tg_sender:app --host 0.0.0.0 --port 8002
