from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, Security
from fastapi.security import HTTPBearer
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from models import User
from schemas import UserCreate, Token, AuthType
from config.settings import settings
from database import get_db
import logging
import time
import traceback
from google.oauth2 import id_token
from google.auth.transport import requests

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
logger = logging.getLogger(__name__)

security = HTTPBearer()

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     logger.debug("Verifying password")
#     return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    logger.info(f"Creating access token with data: {data}")
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    logger.debug(f"Token payload: {to_encode}")
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info("Access token created successfully")
    return encoded_jwt


def get_password_hash(password: str) -> str:
    logger.debug("Hashing password")
    return pwd_context.hash(password)


async def create_user(db: Session, user: UserCreate):
    logger.info(f"Attempting to create user with email: {user.email}")
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        logger.warning(f"User with email {user.email} already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    try:
        # Create new user
        logger.debug("Hashing password for new user")
        hashed_password = get_password_hash(user.password)
        db_user = User(email=user.email, password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"Successfully created user with email: {user.email}")
        return db_user
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        logger.error(traceback.format_exc())
        db.rollback()
        raise


async def login_user(db: Session, email: str, password: str) -> Token:
    """
    Authenticate user and return JWT token
    """
    logger.info(f"Login attempt for email: {email}")
    try:
        # Query user
        logger.debug("Querying database for user")
        user = db.query(User).filter(User.email == email).first()

        # Log user query result
        if user:
            logger.debug(f"Found user with ID: {user.user_id}")
        else:
            logger.warning(f"No user found with email: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # Verify password
        logger.debug("Verifying password")
        if not pwd_context.verify(password, user.password):
            logger.warning(f"Invalid password attempt for user: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # Extract username from email
        username = email.split('@')[0]
        logger.debug(f"Generated username: {username}")

        # Create token
        logger.debug("Creating access token")
        token_data = {
            "sub": user.email,
            "user_id": user.user_id,
            "username": username
        }
        logger.debug(f"Token data: {token_data}")

        access_token = create_access_token(data=token_data)
        logger.info(f"Successfully logged in user: {email}")

        return Token(
            access_token=access_token,
            token_type="bearer",
            username=username
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error during login: {str(e)}"
        )

# called as Depends(auth_service.validate_token) in routers
# retrieves credentials from request header
# decodes token using jwt and extracts payload with email and username
# retrieves user record from database based on email
# returns user object


async def validate_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
):
    """Validate JWT token and return user"""
    logger.info("validate_token called")
    try:
        logger.info("Getting token from credentials")
        token = credentials.credentials
        logger.info(f"Token: {token[:10]}...")

        logger.debug("Decoding JWT token")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug(f"Token payload: {payload}")

        exp_timestamp = payload.get('exp')
        time_until_expiry = exp_timestamp - int(time.time())
        logger.info(f"Token expires in {time_until_expiry} seconds")

        email: str = payload.get("sub")
        username: str = payload.get("username")
        logger.info(f"Token decoded, email: {email}, username: {username}")

        if email is None:
            logger.error("Token payload missing email")
            raise HTTPException(
                status_code=401,
                detail="Invalid token payload"
            )

        logger.debug("Querying user from database")
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            logger.error(f"No user found for email: {email}")
            raise HTTPException(
                status_code=401,
                detail="User not found"
            )

        # Add username to user object for convenience
        user.username = username
        logger.info(f"Successfully validated token for user: {email}")
        return user

    except Exception as e:
        logger.error("############## JWT validation error ##############")
        logger.error(f"JWT validation error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {str(e)}"
        )


async def verify_google_token(token: str):
    """Verify Google ID token and return user info"""
    try:
        # Verify the token with Google
        idinfo = id_token.verify_oauth2_token(
            token, requests.Request(), GOOGLE_CLIENT_ID)

        # Get user info from token
        email = idinfo['email']
        google_id = idinfo['sub']

        return {
            'email': email,
            'google_id': google_id
        }
    except Exception as e:
        logger.error(f"Error verifying Google token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token"
        )


async def handle_google_auth(db: Session, id_token: str) -> Token:
    """Handle Google OIDC authentication flow"""
    logger.info("Processing Google authentication")
    try:
        # Verify Google token and get user info
        user_info = await verify_google_token(id_token)
        email = user_info['email']
        google_id = user_info['google_id']

        # Check if user exists
        user = db.query(User).filter(User.google_id == google_id).first()

        if not user:
            # Check if email is already registered with native auth
            existing_email = db.query(User).filter(User.email == email).first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered with password authentication"
                )

            # Create new user
            user = User(
                email=email,
                google_id=google_id,
                auth_type=AuthType.GOOGLE
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Created new user with Google ID: {google_id}")

        # Generate JWT token
        username = email.split('@')[0]
        token_data = {
            "sub": email,
            "user_id": user.user_id,
            "username": username
        }

        access_token = create_access_token(data=token_data)
        logger.info(f"Successfully authenticated Google user: {email}")

        return Token(
            access_token=access_token,
            token_type="bearer",
            username=username
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during Google auth: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error during Google auth: {str(e)}"
        )
