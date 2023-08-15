def UserEntity(user) -> dict:
    return {
        "id": str(user["_id"]),
        "userName": user["userName"],
        "email": user["email"],
        "company": str(user["company"]),
        "customers": user["customers"],
        "roles": user["roles"],
        "active": user["active"],
    }
    
def ProfileEntity(user) -> dict:
    return {
        "id": str(user["_id"]),
        "userName": user["userName"],
        "email": user["email"],
        "company": user["company"],
        "customers": user["customers"],
        "roles": user["roles"],
        "active": user["active"],
        "company": user["company"],
    }