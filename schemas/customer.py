"""Customer schemas."""

def customer_entity(customer) -> dict:
    """Customer entity."""
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

def customer_entity_list(customers) -> list:
    """Customer entity list."""
    return [customer_entity(customer) for customer in customers]
