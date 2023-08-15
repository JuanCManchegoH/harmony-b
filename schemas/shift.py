def ShiftEntity(shift) -> dict:
    return {
        "id": str(shift["_id"]),
        "day": shift["day"],
        "startTime": shift["startTime"],
        "endTime": shift["endTime"],
        "color": shift["color"],
        "abreviation": shift["abreviation"],
        "description": shift["description"],
        "mode": shift["mode"],
        "event": shift["event"],
        "customerEvent": shift["customerEvent"],
        "active": shift["active"],
        "keep": shift["keep"],
        "worker": shift["worker"],
        "stall": shift["stall"],
        "customer": shift["customer"],
        "createdBy": shift["createdBy"],
        "updatedBy": shift["updatedBy"],
        "createdAt": shift["createdAt"],
        "updatedAt": shift["updatedAt"]
    }