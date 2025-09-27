#!/bin/bash
set -e # Exit on error

echo "Creating virtual environment..."
python -m venv .coder-env

echo "Activating virtual environment..."
./.coder-env/bin/activate

echo "Update pip .. "
./.coder-env/bin/pip install --upgrade pip

echo "Setting up package in dev mode..."
./.coder-env/bin/pip install -e .
