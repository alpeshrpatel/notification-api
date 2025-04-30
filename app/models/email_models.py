from pydantic import BaseModel, EmailStr
from typing import List, Optional

class EmailRecipient(BaseModel):
    """Model for email recipients with name and email"""
    email: EmailStr
    name: Optional[str] = None

class EmailContent(BaseModel):
    """Model for email content with subject and body"""
    subject: str
    body_text: str
    body_html: Optional[str] = None

class EmailRequest(BaseModel):
    """Model for email request with sender, recipients and content"""
    sender: EmailStr
    sender_name: Optional[str] = None
    recipients: List[EmailRecipient]
    cc: Optional[List[EmailRecipient]] = None
    bcc: Optional[List[EmailRecipient]] = None
    content: EmailContent
    reply_to: Optional[List[EmailStr]] = None
    app_id: int

class EmailResponse(BaseModel):
    """Model for email response with message ID and status"""
    message_id: str
    status: str

class ErrorResponse(BaseModel):
    """Model for error responses"""
    detail: str