def ShiftEntity(shift) -> dict:
    return {
        "id": str(shift["_id"]),
        "day": shift["day"],
        "startTime": shift["startTime"],
        "endTime": shift["endTime"],
        "color": shift["color"],
        "abbreviation": shift["abbreviation"],
        "description": shift["description"],
        "mode": shift["mode"],
        "type": shift["type"],
        "active": shift["active"],
        "keep": shift["keep"],
        "worker": shift["worker"],
        "stall": shift["stall"],
        "createdBy": shift["createdBy"],
        "updatedBy": shift["updatedBy"],
        "createdAt": shift["createdAt"],
        "updatedAt": shift["updatedAt"]
    }
    
def ShiftsEntity(shifts) -> list:
    return [ShiftEntity(shift) for shift in shifts]