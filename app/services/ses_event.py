# app/api/ses_events.py
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.repositories.email_repositories import EmailRepository
from app.database import get_db

import json

router = APIRouter()

# @router.post("/email/events")
async def ses_event_listener(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint for AWS SES to send bounce/complaint/open/click events.
    """
    body = await request.body()
    message = json.loads(body)

    # SNS message format
    if "Message" in message:
        ses_message = json.loads(message["Message"])
        event_type = ses_message.get("eventType")

        if event_type == "Bounce":
            await EmailRepository.update_status(
                db=db,
                message_id=ses_message["mail"]["messageId"],
                status="Bounced",
                is_success=False
            )

        elif event_type == "Complaint":
            await EmailRepository.update_status(
                db=db,
                message_id=ses_message["mail"]["messageId"],
                status="Complaint",
                is_success=False
            )

        elif event_type == "Open":
            await EmailRepository.increment_open_count(
                db=db,
                message_id=ses_message["mail"]["messageId"]
            )

        elif event_type == "Click":
            await EmailRepository.increment_click_count(
                db=db,
                message_id=ses_message["mail"]["messageId"]
            )

    return {"status": "ok"}
