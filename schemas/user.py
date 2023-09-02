def UserEntity(user) -> dict:
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

def UserEntityList(users) -> list:
    return [UserEntity(user) for user in users]