#!/bin/sh

# Start redis server
redis-server --daemonize yes

# This will exec the CMD from your Dockerfile
exec "$@"