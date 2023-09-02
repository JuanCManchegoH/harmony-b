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
        "branches": customer["branches"],
        "company": customer["company"],
        "active": customer["active"],
        "userName": customer["userName"],
        "updatedBy": customer["updatedBy"],
        "createdAt": customer["createdAt"],
        "updatedAt": customer["updatedAt"]
    }
    
def CustomerEntityList(customers) -> list:
    return [CustomerEntity(customer) for customer in customers]