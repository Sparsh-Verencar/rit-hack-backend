import os
from fastapi import APIRouter, Request, HTTPException, Header
from svix.webhooks import Webhook, WebhookVerificationError

# 1. FIXED: Importing the shared instance from core.database
from core.database import db

router = APIRouter()

@router.post("/webhooks/clerk")
async def clerk_webhook(
    request: Request,
    # 2. FIXED: Using alias ensures FastAPI looks for the exact hyphenated string
    svix_id: str = Header(default=None, alias="svix-id"),
    svix_timestamp: str = Header(default=None, alias="svix-timestamp"),
    svix_signature: str = Header(default=None, alias="svix-signature"),
):
    # Verify headers exist before trying to read the body
    if not svix_id or not svix_timestamp or not svix_signature:
        raise HTTPException(status_code=400, detail="Missing Svix headers")

    payload = await request.body()
    headers = {
        "svix-id": svix_id,
        "svix-timestamp": svix_timestamp,
        "svix-signature": svix_signature,
    }

    secret = os.getenv("CLERK_WEBHOOK_SECRET")
    if not secret:
        raise HTTPException(status_code=500, detail="CLERK_WEBHOOK_SECRET not set in .env")

    wh = Webhook(secret)
    try:
        event = wh.verify(payload, headers)
    except WebhookVerificationError:
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    event_type = event["type"]
    data = event["data"]

    # Helper to safely extract user properties without throwing KeyError
    email_list = data.get("email_addresses", [])
    email = email_list[0].get("email_address") if email_list else ""
    name = f"{data.get('first_name') or ''} {data.get('last_name') or ''}".strip() or None
    image_url = data.get("image_url")

    if event_type == "user.created":
        # 3. FIXED: Upsert handles webhook retries gracefully
        await db.user.upsert(
            where={"id": data["id"]},
            data={
                "create": {
                    "id": data["id"],
                    "email": email,
                    "name": name,
                    "imageUrl": image_url,
                },
                "update": {
                    "email": email,
                    "name": name,
                    "imageUrl": image_url,
                }
            }
        )

    elif event_type == "user.updated":
        await db.user.update(
            where={"id": data["id"]},
            data={
                "email": email,
                "name": name,
                "imageUrl": image_url,
            }
        )

    elif event_type == "user.deleted":
        await db.user.delete(where={"id": data["id"]})

    return {"status": "ok"}