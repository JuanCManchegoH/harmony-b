"""Shift schemas."""

def shift_entity(shift) -> dict:
    """Shift entity."""
    return {
        "id": str(shift["_id"]),
        "day": shift["day"],
        "startTime": shift["startTime"],
        "endTime": shift["endTime"],
        "color": shift["color"],
        "abbreviation": shift["abbreviation"],
        "description": shift["description"],
        "sequence": shift["sequence"],
        "position": shift["position"],
        "type": shift["type"],
        "active": shift["active"],
        "keep": shift["keep"],
        "worker": shift["worker"],
        "workerName": shift["workerName"],
        "stall": shift["stall"],
        "stallName": shift["stallName"],
        "createdBy": shift["createdBy"],
        "updatedBy": shift["updatedBy"],
        "createdAt": shift["createdAt"],
        "updatedAt": shift["updatedAt"]
    }

def shifts_entity(shifts) -> list:
    """Shifts entity."""
    return [shift_entity(shift) for shift in shifts]
