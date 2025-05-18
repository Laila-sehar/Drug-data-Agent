import pytest
from agent import compile_drug_table
from cache import list_pathway_drugs, get_drug_info

def test_compile_drug_table(monkeypatch):
    monkeypatch.setattr(list_pathway_drugs, "__wrapped__", lambda pid: ["D1"])
    monkeypatch.setattr(get_drug_info, "__wrapped__",
                        lambda d: {"Drug ID": d, "Name": "X", "Class": "Y", "Targets": []})
    df = compile_drug_table(["path:map00010"])
    assert not df.empty
    assert df.iloc[0]["Drug ID"] == "D1"
