#!/bin/bash

celery -A config worker -Q chats,avatars,photos,other --max-tasks-per-child=100 --loglevel=INFO --pool=gevent --concurrency=500

echo "Celery started"