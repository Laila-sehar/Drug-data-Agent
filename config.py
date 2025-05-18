"""
config.py

Loads configuration for the KEGG agent.
"""

import os

KEGG_BASE: str = os.getenv("KEGG_BASE", "https://rest.kegg.jp")
REQUEST_INTERVAL: float = float(os.getenv("REQUEST_INTERVAL", 0.5))
MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", 3))