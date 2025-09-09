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
    
class SESMail(BaseModel):
    timestamp: str | None = None
    messageId: str | None = None

class SESBounce(BaseModel):
    bounceType: str | None = None
    bouncedRecipients: list[dict] | None = None
    timestamp: str | None = None

class SESComplaint(BaseModel):
    complainedRecipients: list[dict] | None = None
    timestamp: str | None = None

class SESDelivery(BaseModel):
    timestamp: str | None = None
    processingTimeMillis: int | None = None
    recipients: list[str] | None = None
    smtpResponse: str | None = None

class SESOpen(BaseModel):
    timestamp: str | None = None
    ipAddress: str | None = None
    userAgent: str | None = None

class SESClick(BaseModel):
    timestamp: str | None = None
    ipAddress: str | None = None
    userAgent: str | None = None
    link: str | None = None

class SESMessage(BaseModel):
    eventType: str | None = None
    notificationType: str | None = None
    mail: SESMail | None = None
    bounce: SESBounce | None = None
    complaint: SESComplaint | None = None
    delivery: SESDelivery | None = None
    open: SESOpen | None = None
    click: SESClick | None = None

# --- SNS wrapper ---
class SNSPayload(BaseModel):
    Type: str
    MessageId: str
    TopicArn: str | None = None
    Message: SESMessage
    Timestamp: str | None = None
    SubscribeURL: str | None = None
    UnsubscribeURL: str | None = None
    
    
