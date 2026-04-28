from fastapi import APIRouter, Request, HTTPException, Depends, Header
from svix.webhooks import Webhook, WebhookVerificationError
from app.core.config import settings
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repo import UserRepo
from app.models.user import User
from app.core.security import get_current_user
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/webhook")
async def clerk_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    svix_id: str = Header(None, alias="svix-id"),
    svix_timestamp: str = Header(None, alias="svix-timestamp"),
    svix_signature: str = Header(None, alias="svix-signature"),
):
    """
    Handle Clerk webhooks for user synchronization.
    """
    if not settings.clerk_webhook_secret:
        logger.error("CLERK_WEBHOOK_SECRET is not set")
        raise HTTPException(status_code=500, detail="Webhook secret not configured")

    payload = await request.body()
    
    # Verify webhook signature
    wh = Webhook(settings.clerk_webhook_secret)
    try:
        msg = wh.verify(
            payload.decode("utf-8"),
            {
                "svix-id": svix_id,
                "svix-timestamp": svix_timestamp,
                "svix-signature": svix_signature,
            }
        )
    except WebhookVerificationError as e:
        logger.warning(f"Webhook verification failed: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = msg.get("type")
    data = msg.get("data")
    user_repo = UserRepo(db)

    if event_type == "user.created":
        clerk_id = data.get("id")
        email = data.get("email_addresses")[0].get("email_address")
        logger.info(f"Creating user {clerk_id}")
        await user_repo.create(clerk_id=clerk_id, email=email)

    elif event_type == "user.updated":
        clerk_id = data.get("id")
        email = data.get("email_addresses")[0].get("email_address")
        user = await user_repo.get_by_clerk_id(clerk_id)
        if user:
            user.email = email
            await user_repo.update(user)
            logger.info(f"Updated user {clerk_id}")

    elif event_type == "user.deleted":
        clerk_id = data.get("id")
        user = await user_repo.get_by_clerk_id(clerk_id)
        if user:
            await user_repo.delete(user)
            logger.info(f"Deleted user {clerk_id}")

    return {"status": "success"}

@router.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    """
    Return the current authenticated user.
    """
    return {
        "id": user.id,
        "clerk_id": user.clerk_id,
        "email": user.email,
        "preferred_language": user.preferred_language,
        "created_at": user.created_at
    }
