def get_status(result: dict) -> dict:
    return {"status": result.get("status"), "change_request_id": result.get("change_request_id")}
