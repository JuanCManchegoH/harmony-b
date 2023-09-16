"""User schemas module."""

def user_entity(user) -> dict:
    """User entity."""
    return {
        "id": str(user["_id"]),
        "userName": user["userName"],
        "email": user["email"],
        "company": user["company"],
        "customers": user["customers"],
        "workers": user["workers"],
        "roles": user["roles"],
        "active": user["active"],
    }

def user_entity_list(users) -> list:
    """User entity list."""
    return [user_entity(user) for user in users]
