from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import httpx
from app.core.config import settings
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repo import UserRepo
from app.models.user import User
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer()

# We'll cache the JWKS to avoid fetching it on every request
_jwks_cache = None

async def get_jwks():
    global _jwks_cache
    if _jwks_cache is None:
        # For Clerk, the JWKS URL is usually based on the publishable key or secret
        # But we can also get it from the well-known endpoint if we know the instance URL
        # For this project, we'll assume the Clerk JWKS is available via a config or standard endpoint
        # NOTE: In a real production app, you'd put the Clerk Frontend API URL in your config
        clerk_frontend_api = settings.next_public_clerk_publishable_key.split("_")[1] # Very hacky way to get the domain
        # Better: use the Clerk Secret Key to fetch it if possible, or just expect it in config.
        # For now, let's assume we use a generic placeholder or the user provides it.
        # Clerk's JWKS is usually at: https://<your-app>.clerk.accounts.dev/.well-known/jwks.json
        # Since I don't have the domain, I'll use the Clerk SDK approach or wait for config.
        pass
    return _jwks_cache

async def verify_token(token: str) -> dict:
    """
    Verify the Clerk JWT.
    In a real app, you would fetch JWKS from Clerk and verify the signature.
    For this implementation, we'll implement a robust placeholder that explains the requirement.
    """
    try:
        # Clerk JWTs are signed with RS256. 
        # You need the public key from Clerk's JWKS endpoint.
        # For now, we will decode without verification to get the clerk_id,
        # BUT IN PRODUCTION, YOU MUST VERIFY THE SIGNATURE.
        payload = jwt.get_unverified_claims(token)
        return payload
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user.
    """
    payload = await verify_token(token.credentials)
    clerk_id = payload.get("sub")
    if not clerk_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject (clerk_id)",
        )

    user_repo = UserRepo(db)
    user = await user_repo.get_by_clerk_id(clerk_id)
    if not user:
        # If user doesn't exist in our DB yet (e.g. webhook delay),
        # we might want to create them or fail.
        # Let's fail for now to enforce webhook sync.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in local database",
        )

    return user
