from scripts.poll_orderbooks import _extract_payload_data, _normalize_side


def test_extract_payload_data_prefers_data():
    payload = {"data": {"bids": [[1, 2]]}, "result": {"bids": [[3, 4]]}}
    assert _extract_payload_data(payload) == {"bids": [[1, 2]]}


def test_extract_payload_data_falls_back_result():
    payload = {"result": {"asks": [[5, 6]]}}
    assert _extract_payload_data(payload) == {"asks": [[5, 6]]}


def test_normalize_side_supports_list_and_dict_shapes():
    levels = [
        ["100", "1.5"],
        {"price": "101", "qty": "2"},
        {"rate": "102", "amount": "3"},
        {"rate": "bad", "amount": "3"},
    ]
    out = _normalize_side(levels)
    assert out == [[100.0, 1.5], [101.0, 2.0], [102.0, 3.0]]
