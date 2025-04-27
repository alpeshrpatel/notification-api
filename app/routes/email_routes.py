from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN

from app.models.email_models import EmailRequest, EmailResponse
from app.controllers.email_controller import EmailController
from app.config import settings
from sqlalchemy.orm import Session
from app.database.database import get_db

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

@router.post(
    "/send/email",
    response_model=EmailResponse,
    # dependencies=[Depends(verify_api_key)],
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