def CustomerEntity(customer) -> dict:
    return {
        "id": str(customer["_id"]),
        "name": customer["name"],
        "identification": customer["identification"],
        "city": customer["city"],
        "contact": customer["contact"],
        "phone": customer["phone"],
        "address": customer["address"],
        "fields": customer["fields"],
        "tags": customer["tags"],
        "company": customer["company"],
        "active": customer["active"],
        "userName": customer["userName"],
        "updatedBy": customer["updatedBy"],
        "createdAt": customer["createdAt"],
        "updatedAt": customer["updatedAt"]
    }