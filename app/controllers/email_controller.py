from fastapi import HTTPException
from app.models.email_models import EmailRequest, EmailResponse
from app.services.ses_service import SESService
from sqlalchemy.orm import Session

class EmailController:
    """Controller for email-related operations"""
    
    @staticmethod
    async def send_email(email_request: EmailRequest, db: Session) -> EmailResponse:
        """Handle sending an email through AWS SES"""
        try:
            result = await SESService.send_email(email_request, db)
            
            return EmailResponse(
                message_id=result["message_id"],
                status=result["status"]
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))