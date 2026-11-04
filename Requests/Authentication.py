
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from Class.Authentication import Authentication
from Class.Auth import get_current_user


router = APIRouter()
authentication = Authentication()


class LoginRequest(BaseModel):
    Id_Number: str
    Password: str


# LOGIN
@router.post("/authentication/login")
def login(request: LoginRequest):
    return authentication.login(
        request.Id_Number,
        request.Password
    )


# VERIFY AUTHENTICATION
@router.get("/authentication/me")
def get_logged_in_user(
    current_user: dict = Depends(get_current_user)
):
    return {
        "success": True,
        "message": "Authenticated user retrieved successfully.",
        "data": current_user
    }
