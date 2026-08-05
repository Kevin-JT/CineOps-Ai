from pydantic import BaseModel, EmailStr, Field


class UserCredentialsRequest(BaseModel):
    """
    Request model for user registration and login.
    """
    email: EmailStr
    password: str = Field(..., min_length=8)


class TokenResponse(BaseModel):
    """
    Response model for authentication tokens.
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """
    Request model for refreshing an access token.
    """
    refresh_token: str
