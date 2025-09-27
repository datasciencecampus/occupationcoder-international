#!/bin/bash
set -e # Exit on error

echo "Creating virtual environment..."
python -m venv env

echo "Activating virtual environment..."
source ./env/bin/activate

echo "Update pip .. "
pip install --upgrade pip

echo "Setting up package in dev mode..."
pip install -e .
