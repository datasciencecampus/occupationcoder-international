#!/bin/bash
python -m venv .coder-env
source .coder-env/bin/activate
pip install -r requirements.txt
python setup.py install