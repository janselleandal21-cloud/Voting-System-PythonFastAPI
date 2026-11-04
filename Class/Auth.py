from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from .Database import Database

# JWT SETTINGS
SECRET_KEY = "vskey09462242111"
ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = 60

security = HTTPBearer(auto_error=False)


# VERIFY TOKEN AND CHECK ACCOUNT STATUS
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Please log in first."
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        idnum = payload.get("Id_Number")

        if not idnum:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token."
            )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Session expired. Please log in again."
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token."
        )

    db = Database()
    cursor = db.conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT Id_Number, Role, Status
            FROM users
            WHERE Id_Number = %s
            LIMIT 1
            """,
            (idnum,)
        )

        user = cursor.fetchone()

        if not user or user["Status"] != "Active":
            raise HTTPException(
                status_code=401,
                detail="Your account is inactive or no longer exists."
            )

        return {
            "Id_Number": user["Id_Number"],
            "Role": user["Role"]
        }

    finally:
        cursor.close()


# CHECK USER ROLE
def require_role(required_role: str):
    def role_checker(
        current_user: dict = Depends(get_current_user)
    ):
        if current_user["Role"].lower() != required_role.lower():
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this resource."
            )

        return current_user

    return role_checker
