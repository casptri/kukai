def merge_nested(d1: dict, d2: dict) -> dict:
    for key, value in d2.items():
        if key in d1:
            if isinstance(d1[key], dict) and isinstance(value, dict):
                merge_nested(d1[key], value)
            elif isinstance(d1[key], list) and isinstance(value, list):
                d1[key].extend(value)
            else:
                d1[key] = value
        else:
            d1[key] = value
    return d1
