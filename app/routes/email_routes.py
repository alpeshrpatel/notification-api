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