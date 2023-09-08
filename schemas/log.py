def LogEntity(log) -> dict:
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
    
def LogsEntity(logs) -> list:
    return [LogEntity(log) for log in logs]