"""Stall schemas."""

from schemas.shift import shift_entity

def stall_entity(stall) -> dict:
    """Stall entity."""
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

def stalls_entity(stalls) -> dict:
    """Stalls entity."""
    return [stall_entity(stall) for stall in stalls]

def stalls_and_shifts(stalls, shifts) -> dict:
    """Stalls and shifts entity."""
    return {
        "stalls": [stall_entity(stall) for stall in stalls],
        "shifts": [shift_entity(shift) for shift in shifts]
    }
