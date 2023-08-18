def UserEntity(user) -> dict:
    return {
        "id": str(user["_id"]),
        "userName": user["userName"],
        "email": user["email"],
        "company": str(user["company"]),
        "customers": user["customers"],
        "workers": user["workers"],
        "roles": user["roles"],
        "active": user["active"],
    }
