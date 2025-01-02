from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from sqlalchemy.orm import Session
from database import get_db
from services import auth_service
from schemas import UserCreate, Token, AuthType
from typing import Annotated
from pydantic import BaseModel, Field
from config.settings import settings

router = APIRouter()


class GoogleAuthRequest(BaseModel):
    """Schema for Google auth request"""
    id_token: str = Field(description="Google ID token from client")


@router.post(
    "/google/callback",
    response_model=Token,
    summary="Handle Google OIDC authentication"
)
async def google_auth(
    request: GoogleAuthRequest,
    db: Session = Depends(get_db)
):
    """
    Handle Google OIDC authentication. This endpoint:
    1. Verifies the Google ID token
    2. Creates a new user if they don't exist
    3. Returns a JWT token for the user

    - **id_token**: Google ID token from client-side Google Sign-In
    """
    try:
        token = await auth_service.handle_google_auth(db, request.id_token)
        return token
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/register",
    response_model=UserCreate,
    summary="Register a new user"
)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user with:
    - **email**: valid email address
    - **password**: string
    """
    return await auth_service.create_user(db, user)


@router.post(
    "/login",
    response_model=Token,
    summary="Login to get JWT token",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "username": "john.doe"
                    }
                }
            }
        },
        401: {
            "description": "Invalid credentials"
        }
    }
)
async def login(
    username: Annotated[str, Form(description="User's email address")],
    password: Annotated[str, Form(description="User's password")],
    db: Session = Depends(get_db)
):
    """
    Login with email and password to get a JWT token.

    - **username**: email address
    - **password**: user password

    Returns:
    - **access_token**: JWT token to use for authentication
    - **token_type**: "bearer"
    - **username**: user's username
    """
    try:
        token = await auth_service.login_user(db, username, password)
        return token
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/google/auth-url",
    summary="Get Google OAuth2 authorization URL"
)
async def google_auth_url():
    """
    Get the URL to redirect users to for Google OAuth2 authentication.
    This URL will redirect users to Google's consent screen.
    """
    return {
        "auth_url": f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        "response_type=id_token&"
        f"redirect_uri={settings.GOOGLE_REDIRECT_URI}&"
        "scope=openid email profile&"
        "nonce=random_nonce"  # In production, generate a secure random nonce
    }
