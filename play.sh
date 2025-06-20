#!/bin/bash

# Start PHP built-in server in the background
php -S 0.0.0.0:8080 &

# Save the PHP server's PID so you can kill it later if needed
PHP_PID=$!

# Run the Python script (this will block until it exits)
python3 play.py

# After Python script ends, kill the PHP server
kill $PHP_PID
