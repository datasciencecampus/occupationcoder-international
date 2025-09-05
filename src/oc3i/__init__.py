# src/oc3i/__init__.py
from pathlib import Path
import tomllib  # built-in in Python 3.11+

pyproject_file = Path(__file__).resolve().parents[2] / "pyproject.toml"
with pyproject_file.open("rb") as f:
    pyproject_data = tomllib.load(f)

__version__ = pyproject_data["project"]["version"]