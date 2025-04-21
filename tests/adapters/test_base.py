from llmcli.adapters import parse_api_params

def test_parse_api_params():
    params = ["param1=value1", "param2=value2", "param3=val=ue=3"]
    expected_result = {"param1": "value1", "param2": "value2", "param3": "val=ue=3"}
    assert parse_api_params(params) == expected_result