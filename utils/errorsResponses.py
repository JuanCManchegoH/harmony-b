#  errorsResponses.py contains the error responses for the API
from fastapi import HTTPException, status

errors = {
    "Unauthorized": HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden, access denied"),
    "Token expired": HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"),      
    "Authentication error": HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication error"),
    "Creation error": HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Creation error"),
    "Read error": HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Read error"),
    "Update error": HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Update error"),
    "Deletion error": HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Deletion error"),
    "Deactivation error": HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Deactivation error"),
}