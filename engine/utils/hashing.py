import hashlib
import json


def stable_hash(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",",":")).encode()
    return hashlib.sha256(encoded).hexdigest()
