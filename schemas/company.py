def CompanyEntity(company) -> dict:
    return {
        "id": str(company["_id"]),
        "name": company["name"],
        "website": company["website"],
        "workerFields": company["workerFields"],
        "customerFields": company["customerFields"],
        "positions": company["positions"],
        "conventions": company["conventions"],
        "sequences": company["sequences"],
        "tags": company["tags"],
        "pColor": company["pColor"],
        "sColor": company["sColor"],
        "logo": company["logo"],
        "active": company["active"],
    }
