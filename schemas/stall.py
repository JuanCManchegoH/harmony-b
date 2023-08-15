def StallEntity(stall) -> dict:
    return {
        "id": str(stall["_id"]),
        "name": stall["name"],
        "description": stall["description"],
        "ays": stall["ays"],
        "place": stall["place"],
        "monthAndYear": stall["monthAndYear"],
        "customer": stall["customer"],
        "customerName": stall["customerName"],
        "workers": stall["workers"],
        "createdBy": stall["createdBy"],
        "updatedBy": stall["updatedBy"],
        "createdAt": stall["createdAt"],
        "updatedAt": stall["updatedAt"]
    }