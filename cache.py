"""
cache.py

Optional LRU caching for expensive calls.
"""

from functools import lru_cache
import tools

# cache up to 128 unique pathway queries
list_pathway_drugs = lru_cache(maxsize=128)(tools.list_pathway_drugs)
# cache up to 256 unique drug info queries
get_drug_info = lru_cache(maxsize=256)(tools.get_drug_info)
