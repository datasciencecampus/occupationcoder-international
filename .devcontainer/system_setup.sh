#!/bin/bash

# This bash script sets up a Python virtual environment and installs the package in editable mode.
# It replicates the package setup set out in README and serves as a helper for the Devcontainer setup.

set -e # Exit on error

echo "Creating virtual environment..."
python -m venv env

echo "Activating virtual environment..."
source env/bin/activate

echo "Update pip .. "
pip install --upgrade pip

echo "Setting up package in dev mode..."
pip install -e .
