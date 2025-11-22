#!/bin/sh

if nc -z db 5432; then
  exit 0
else
  exit 1
fi
