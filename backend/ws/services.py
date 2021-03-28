def processing_ws(ws_dict: dict) -> dict:
    assert "type" in ws_dict and "data" in ws_dict

    r_type = ws_dict["type"]
    assert r_type in ("",)  # TODO: Добавить типы запросов

    data = ws_dict["data"]

    # TODO : Добавить обработку запросов

    return ws_dict

# TODO: Методы для обработки запроса
