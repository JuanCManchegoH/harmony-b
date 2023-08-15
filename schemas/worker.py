def WorkerEntity(worker) -> dict:
    return {
        "id": str(worker["_id"]),
        "name": worker["name"],
        "identification": worker["identification"],
        "city": worker["city"],
        "phone": worker["phone"],
        "address": worker["address"],
        "fields": worker["fields"],
        "tags": worker["tags"],
        "company": worker["company"],
        "active": worker["active"],
        "userName": worker["userName"],
        "updatedBy": worker["updatedBy"],
        "createdAt": worker["createdAt"],
        "updatedAt": worker["updatedAt"]
    }
