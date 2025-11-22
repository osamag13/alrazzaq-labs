#!/bin/sh

max_retries=5
retry_delay=5

for i in $(seq 1 $max_retries); do
  if nc -z db 5432; then
    echo "Database is ready!"
    exec "$@"
    exit 0
  else
    echo "Waiting for database... Attempt $i/$max_retries"
    sleep $retry_delay
  fi
done

echo "Failed to connect to database after $max_retries attempts"
exit 1
