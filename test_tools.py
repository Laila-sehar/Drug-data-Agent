import pytest
from tools import list_pathway_drugs, get_drug_info
from unittest.mock import patch

@patch("tools.requests.get")
def test_list_pathway_drugs(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "DRUG    D00001 D00002\n"
    assert list_pathway_drugs("path:map00010") == ["D00001", "D00002"]

@patch("tools.requests.get")
def test_get_drug_info(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "NAME   Aspirin\nCLASS  NSAID\nTARGET P12345\n"
    info = get_drug_info("D00001")
    assert info["Name"] == "Aspirin"
    assert "P12345" in info["Targets"]
