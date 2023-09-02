from typing import List
from .errorsResponses import errors

def required_roles(roles: List[str], required_roles: List[str]) -> bool:
    if "super_admin" in roles:
        return True
    acces = set(required_roles).issubset(set(roles))
    if not acces:
        raise errors["Unauthorized"]

def allowed_roles(roles: List[str], allowed_roles: List[str]) -> bool:
    if "super_admin" in roles:
        return True
    acces = set(allowed_roles).intersection(set(roles))
    if not acces:
        raise errors["Unauthorized"]