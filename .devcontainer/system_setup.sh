#!/bin/bash
set -e # Exit on error

echo "Creating virtual environment..."
python -m venv .coder-env

echo "Installing dependencies..."
./.coder-env/bin/pip install -r requirements.txt

echo "Running setup.py..."
./.coder-env/bin/python setup.py install

echo "Activating virtual environment..."
./.coder-env/bin/activate
