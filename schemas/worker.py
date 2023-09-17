"""Worker schemas"""

def worker_entity(worker) -> dict:
    """Worker entity."""
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

def worker_entity_list(workers) -> list:
    """Worker entity list."""
    return [worker_entity(worker) for worker in workers]
