# api/webhooks.py

from fastapi import APIRouter, Request, HTTPException
from prisma import Prisma
import os
import json
import hmac
import hashlib

router = APIRouter()
db = Prisma()

CLERK_WEBHOOK_SECRET = os.getenv("CLERK_WEBHOOK_SECRET")


def verify_clerk_signature(request: Request, body: bytes):
    signature = request.headers.get("svix-signature")
    if not signature:
        raise HTTPException(status_code=400, detail="Missing signature")

    expected = hmac.new(CLERK_WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=400, detail="Invalid signature")


@router.post("/webhooks/clerk")
async def clerk_webhook(request: Request):
    body = await request.body()

    # 🔐 verify webhook
    verify_clerk_signature(request, body)

    payload = json.loads(body)
    event_type = payload.get("type")

    if event_type == "user.created":
        data = payload["data"]

        user_id = data["id"]
        email = data["email_addresses"][0]["email_address"]
        name = data.get("first_name", "") + " " + data.get("last_name", "")

        await db.connect()

        # 🧠 upsert (important: avoid duplicates)
        await db.user.upsert(
            where={"id": user_id},
            data={
                "create": {"id": user_id, "email": email, "name": name.strip() or None},
                "update": {"email": email, "name": name.strip() or None},
            },
        )

        await db.disconnect()

    return {"status": "ok"}
