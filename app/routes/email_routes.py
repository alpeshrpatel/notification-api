from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from fastapi import Header
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED

from app.models.email_models import EmailRequest, EmailResponse
from app.controllers.email_controller import EmailController
from app.config import settings
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database.database import get_db
from app.models.db_applications import Application  # Import Application model
from app.repositories.email_repositories import EmailRepository  # Import EmailRepository
# import pywhatkit
import os
import logging

# Configure logger
logger = logging.getLogger("email_routes")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Create router
router = APIRouter(tags=["emails"])

# Security configuration
# api_key_header = APIKeyHeader(name="X-API-Key")

# def verify_api_key(api_key: str = Depends(api_key_header)):
#     """Verify the API key provided in the request header"""
#     if api_key != settings.API_KEY:
#         raise HTTPException(
#             status_code=HTTP_403_FORBIDDEN,
#             detail="Not authenticated"
#         )
#     return api_key
async def verify_token(
    x_api_token: Optional[str] = Header(None),
    app_id: Optional[str] = Header(None),
    db = Depends(get_db)
):
    """Verify the token provided in request header using aiomysql"""
    if not x_api_token:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="API token is missing"
        )
    
    if not app_id:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Application ID is missing"
        )
    
    try:
        # If db is a connection pool
        if hasattr(db, 'acquire'):
            async with db.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        "SELECT id, token FROM applications WHERE id = %s AND token = %s", 
                        (app_id, x_api_token)
                    )
                    result = await cursor.fetchone()
        
        # If db is already a connection
        elif hasattr(db, 'cursor'):
            async with db.cursor() as cursor:
                await cursor.execute(
                    "SELECT id, token FROM applications WHERE id = %s AND token = %s", 
                    (app_id, x_api_token)
                )
                result = await cursor.fetchone()
        
        # If db is a database object with execute method
        elif hasattr(db, 'execute'):
            query = "SELECT id, token FROM applications WHERE id = %s AND token = %s"
            result = await db.execute(query, (app_id, x_api_token))
            if hasattr(result, 'fetchone'):
                result = await result.fetchone()
        
        else:
            raise ValueError("Unsupported database connection type")
        
        if not result:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="Invalid token or application not found"
            )
        
        # Return the application data
        return {"id": result[0], "token": result[1]}
                
    except Exception as e:
        # Log the error for debugging
        print(f"Database error: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error validating application token"
    
        )
        
@router.post("/send/email",
    response_model=EmailResponse,
    dependencies=[Depends(verify_token)],
    summary="Send an email using AWS SES",
    description="Send an email with optional HTML content, CC, BCC and Reply-To using AWS SES"
)
async def send_email(email_request: EmailRequest, db: Session = Depends(get_db)):
    """
    Send an email using AWS SES with the following information:
    - **sender**: Email address of the sender (must be verified in AWS SES)
    - **sender_name**: Optional name of the sender
    - **recipients**: List of email recipients with email and optional name
    - **cc**: Optional list of CC recipients
    - **bcc**: Optional list of BCC recipients
    - **content**: Email content with subject, text body and optional HTML body
    - **reply_to**: Optional list of reply-to email addresses
    """
    return await EmailController.send_email(email_request,db)

@router.post("/send/whatsapp",
    summary="Send a WhatsApp message using Twilio API",
    description="Send a WhatsApp message using Twilio API"
)
async def send_whatsapp_message(
    # message: str,
    # phone_number: str,
    # x_api_token: Optional[str] = Header(None),
    # app_id: Optional[str] = Header(None),
    # db: Session = Depends(get_db)
):
    """
    Send a WhatsApp message using Twilio API with the following information:
    - **message**: Message to be sent
    - **phone_number**: Phone number of the recipient
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(base_dir, "..", "images", "gotestli.png")

    # Implement the logic to send WhatsApp message using Twilio API
    # pywhatkit.sendwhatmsg("+14804923225", "Hi, This Is system generated message From Dipak", 8,44)
    # pywhatkit.sendwhats_image("+917567448419", image_path, "Team gotestli")
    print("Successfully Sent!")
    
    
@router.get("/email/metrics")
def get_email_metrics(months: int = 3, db: Session = Depends(get_db)):
    return {"metrics": EmailRepository.get_email_metrics(db, months=months)}


from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.repositories.email_repositories import EmailRepository

import json

# @router.post("/email/events")
# async def ses_event_listener(request: Request, db: Session = Depends(get_db)):
#     """
#     Endpoint for AWS SES to send bounce/complaint/open/click events.
#     """
#     body = await request.body()
#     message = json.loads(body)

#     # SNS message format
#     if "Message" in message:
#         ses_message = json.loads(message["Message"])
#         event_type = ses_message.get("eventType")

#         if event_type == "Bounce":
#             await EmailRepository.update_status(
#                 db=db,
#                 message_id=ses_message["mail"]["messageId"],
#                 status="Bounced",
#                 is_success=False
#             )

#         elif event_type == "Complaint":
#             await EmailRepository.update_status(
#                 db=db,
#                 message_id=ses_message["mail"]["messageId"],
#                 status="Complaint",
#                 is_success=False
#             )

#         elif event_type == "Open":
#             await EmailRepository.increment_open_count(
#                 db=db,
#                 message_id=ses_message["mail"]["messageId"]
#             )

#         elif event_type == "Click":
#             await EmailRepository.increment_click_count(
#                 db=db,
#                 message_id=ses_message["mail"]["messageId"]
#             )

#     return {"status": "ok"}


@router.post("/email/events")
async def ses_event_listener(request: Request, db: Session = Depends(get_db)):
    """
    Enhanced endpoint for AWS SES/SNS to send bounce/complaint/open/click events.
    Handles both subscription confirmations and notifications.
    """
    try:
        # Get the raw body
        body = await request.body()
        logger.info(f"Received webhook body length: {len(body)}")
        
        # Handle empty body
        if not body:
            logger.error("Received empty body")
            raise HTTPException(status_code=400, detail="Empty request body")
        
        # Parse the main message
        try:
            message = json.loads(body)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse main message: {e}")
            logger.error(f"Body content: {body.decode('utf-8', errors='replace')[:500]}")
            raise HTTPException(status_code=400, detail=f"Invalid JSON in request body: {e}")
        
        logger.info(f"Parsed main message type: {message.get('Type')}")
        
        # Handle SNS subscription confirmation
        if message.get("Type") == "SubscriptionConfirmation":
            logger.info("Received SNS subscription confirmation")
            subscribe_url = message.get("SubscribeURL")
            if subscribe_url:
                logger.info(f"Subscription URL: {subscribe_url}")
                # You can optionally auto-confirm by making a GET request to subscribe_url
                # import httpx
                # async with httpx.AsyncClient() as client:
                #     await client.get(subscribe_url)
            return {
                "status": "subscription_confirmation_received",
                "message": "Please confirm subscription manually via AWS console or implement auto-confirmation"
            }
        
        # Handle SNS notifications
        if message.get("Type") == "Notification":
            # Get the nested message
            nested_message = message.get("Message")
            
            if not nested_message:
                logger.error("No nested Message found in notification")
                return {"status": "error", "detail": "No Message field in notification"}
            
            # Handle case where Message might not be a string
            if not isinstance(nested_message, str):
                logger.error(f"Message field is not a string: {type(nested_message)}")
                return {"status": "error", "detail": "Message field must be a string"}
            
            # Strip and validate the nested message
            nested_message = nested_message.strip()
            if not nested_message:
                logger.error("Nested message is empty")
                return {"status": "error", "detail": "Empty nested message"}
            
            # Parse the SES event message
            try:
                ses_message = json.loads(nested_message)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse SES message: {e}")
                logger.error(f"SES message content: {nested_message[:500]}")
                return {"status": "error", "detail": f"Invalid JSON in SES message: {e}"}
            
            # Process the SES event
            event_type = ses_message.get("eventType") or ses_message.get("notificationType")
            logger.info(f"Processing SES event type: {event_type}")
            
            if not event_type:
                logger.error("No eventType found in SES message")
                return {"status": "error", "detail": "No eventType in SES message"}
            
            # Extract message ID
            message_id = None
            mail_info = ses_message.get("mail", {})
            if mail_info:
                message_id = mail_info.get("messageId")
            
            if not message_id:
                logger.error(f"No messageId found for event type {event_type}")
                return {"status": "error", "detail": "No messageId found"}
            
            logger.info(f"Processing {event_type} for message ID: {message_id}")
            
            # Handle different event types
            try:
                if event_type.lower() == "bounce":
                    await EmailRepository.update_status(
                        db=db,
                        message_id=message_id,
                        status="Bounced",
                        is_success=False
                    )
                    logger.info(f"Updated bounce status for message {message_id}")
                
                elif event_type.lower() == "complaint":
                    await EmailRepository.update_status(
                        db=db,
                        message_id=message_id,
                        status="Complaint",
                        is_success=False
                    )
                    logger.info(f"Updated complaint status for message {message_id}")
                
                elif event_type.lower() == "delivery":
                    await EmailRepository.update_status(
                        db=db,
                        message_id=message_id,
                        status="Delivered",
                        is_success=True
                    )
                    logger.info(f"Updated delivery status for message {message_id}")
                
                elif event_type.lower() == "open":
                    await EmailRepository.increment_open_count(
                        db=db,
                        message_id=message_id
                    )
                    logger.info(f"Incremented open count for message {message_id}")
                
                elif event_type.lower() == "click":
                    await EmailRepository.increment_click_count(
                        db=db,
                        message_id=message_id
                    )
                    logger.info(f"Incremented click count for message {message_id}")
                
                else:
                    logger.warning(f"Unhandled event type: {event_type}")
                    return {"status": "ignored", "event_type": event_type}
                
            except Exception as e:
                logger.error(f"Error updating database for {event_type}: {e}")
                return {"status": "error", "detail": f"Database update failed: {str(e)}"}
            
            return {"status": "processed", "event_type": event_type, "message_id": message_id}
        
        # Handle other message types
        logger.warning(f"Unhandled message type: {message.get('Type')}")
        return {"status": "ignored", "type": message.get("Type")}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in SES event listener: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
