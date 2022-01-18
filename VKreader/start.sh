#!/bin/sh

sleep 15
uvicorn VKreader.vk_reader:app --host 0.0.0.0 --port 8001
