#!/usr/bin/env bash

uvicorn bgd.application:app --host 0.0.0.0 --port $PORT
