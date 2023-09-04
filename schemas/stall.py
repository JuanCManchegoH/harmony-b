from schemas.shift import ShiftEntity

def StallEntity(stall) -> dict:
    return {
        "id": str(stall["_id"]),
        "name": stall["name"],
        "description": stall["description"],
        "ays": stall["ays"],
        "branch": stall["branch"],
        "month": stall["month"],
        "year": stall["year"],
        "customer": stall["customer"],
        "customerName": stall["customerName"],
        "workers": stall["workers"],
        "stage": stall["stage"],
        "tag": stall["tag"],
        "createdBy": stall["createdBy"],
        "updatedBy": stall["updatedBy"],
        "createdAt": stall["createdAt"],
        "updatedAt": stall["updatedAt"]
    }
    
def StallsAndShifts(stalls, shifts) -> dict:
    return {
        "stalls": [StallEntity(stall) for stall in stalls],
        "shifts": [ShiftEntity(shift) for shift in shifts]
    }