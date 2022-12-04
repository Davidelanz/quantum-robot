#!/bin/sh

# Start redis server
redis-server --daemonize yes

# This will exec the CMD from the Dockerfile
exec "$@"