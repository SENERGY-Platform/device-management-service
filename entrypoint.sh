#!/bin/sh

if [ "$GUNICORN_LOG" -eq 1 ]; then
  exec gunicorn -b 0.0.0.0:80 --workers 1 --threads 4 --worker-class gthread --access-logfile - --log-file - --log-level warning app:app
else
  exec gunicorn -b 0.0.0.0:80 --workers 1 --threads 4 --worker-class gthread --log-file - --log-level warning app:app
fi
