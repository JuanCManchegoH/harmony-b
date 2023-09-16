"""Log schemas module."""

def log_entity(log) -> dict:
    """Log entity."""
    return {
        "id": str(log["_id"]),
        "company": log["company"],
        "user": log["user"],
        "userName": log["userName"],
        "type": log["type"],
        "message": log["message"],
        "month": log["month"],
        "year": log["year"],
        "createdAt": log["createdAt"]
    }

def log_entity_list(logs) -> list:
    """Log entity list."""
    return [log_entity(log) for log in logs]
