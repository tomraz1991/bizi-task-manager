#!/bin/bash

# Make sure we're in the backend directory
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Use the venv's Python explicitly
venv/bin/python main.py
