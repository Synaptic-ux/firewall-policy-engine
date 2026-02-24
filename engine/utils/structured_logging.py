import json


def log(level: str, message: str, **context: object) -> None:
    record = {"level": level, "message": message, **context}
    print(json.dumps(record, sort_keys=True))
