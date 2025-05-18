"""
tools.py

KEGG API tool wrappers: list_pathway_drugs and get_drug_info.
"""

import re
import time
import random
import logging
import requests
from typing import List, Dict, Any
from config import KEGG_BASE, REQUEST_INTERVAL, MAX_RETRIES

logger = logging.getLogger("kegg_agent.tools")


def kegg_get(url: str) -> requests.Response:
    """
    GET with retry/backoff on 429.
    """
    retries = 0
    while True:
        resp = requests.get(url)
        if resp.status_code == 429 and retries < MAX_RETRIES:
            wait = int(resp.headers.get("Retry-After", 1)) * (2 ** retries)
            jitter = random.uniform(0, 0.5)
            logger.warning(f"429 received. Sleeping {wait+jitter:.2f}s")
            time.sleep(wait + jitter)
            retries += 1
            continue
        time.sleep(REQUEST_INTERVAL + random.uniform(0, 0.2))
        return resp


def list_pathway_drugs(pathway_id: str) -> List[str]:
    """
    Given a pathway ID (e.g. "path:map00010"), return a list of drug IDs.
    """
    if not re.match(r"^path:[a-z0-9]+$", pathway_id):
        raise ValueError(f"Invalid pathway_id: {pathway_id}")
    url = f"{KEGG_BASE}/get/{pathway_id}"
    text = kegg_get(url).text
    match = re.search(r"^DRUG\s+(.+?)(?:^\S|\Z)", text, flags=re.M | re.S)
    if not match:
        return []
    return re.findall(r"\b(D\d+)\b", match.group(1))


def get_drug_info(drug_id: str) -> Dict[str, Any]:
    """
    Given a drug ID (e.g. "D01234"), return its metadata.
    """
    if not re.match(r"^D\d+$", drug_id):
        raise ValueError(f"Invalid drug_id: {drug_id}")
    url = f"{KEGG_BASE}/get/{drug_id}"
    resp = kegg_get(url)
    lines = resp.text.splitlines() if resp.ok else []
    info: Dict[str, Any] = {
        "Drug ID": drug_id,
        "Name": next((l.split("NAME")[1].strip()
                      for l in lines if l.startswith("NAME")), "Not found"),
        "Class": next((l.split("CLASS")[1].strip()
                       for l in lines if l.startswith("CLASS")), "Not found"),
        "Targets": [],
    }
    in_tgt = False
    for line in lines:
        if line.startswith("TARGET"):
            in_tgt = True
            info["Targets"].append(line[6:].strip())
        elif in_tgt and line.startswith(" "):
            info["Targets"].append(line.strip())
        elif in_tgt:
            break
    return info
