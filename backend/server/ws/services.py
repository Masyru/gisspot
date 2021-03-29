WS_TYPES = {"processing": lambda data: data}


def processing_user(ws_dict: dict) -> None:
    assert "type" in ws_dict and "data" in ws_dict
    assert ws_dict["type"] in WS_TYPES.keys()

    WS_TYPES[ws_dict["type"]](ws_dict["data"])
