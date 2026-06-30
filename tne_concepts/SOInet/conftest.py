"""Pytest import defaults for the standalone SOInet concept module."""

import sys
from pathlib import Path

SOINET_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SOINET_DIR))
