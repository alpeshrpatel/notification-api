# import json
# from sqlalchemy.orm import Session
# from app.models.db_models import EmailLog
# from app.models.email_models import EmailRequest

# class EmailRepository:
#     """Repository for email log operations"""

#     @staticmethod
#     async def create_email_log(db: Session, email_request: EmailRequest, is_success: bool = True, error_message: str = None):
#         """Create a new email log entry"""
#         # Create email log with simplified fields
#         email_log = EmailLog(
#             sender_email=email_request.sender,
#             recipient_email=email_request.recipients[0].email if email_request.recipients else None,
#             subject=email_request.content.subject,
#             is_success=is_success,
#             error_message=error_message
#         )

#         # Add to database
#         db.add(email_log)
#         db.commit()
#         db.refresh(email_log)
#         return email_log

#     @staticmethod
#     def get_email_logs(db: Session, skip: int = 0, limit: int = 100):
#         """Get all email logs with pagination"""
#         return db.query(EmailLog).order_by(EmailLog.sent_at.desc()).offset(skip).limit(limit).all()

#     @staticmethod
#     def get_email_log_by_id(db: Session, email_log_id: int):
#         """Get a specific email log by ID"""
#         return db.query(EmailLog).filter(EmailLog.id == email_log_id).first()


import json
from sqlalchemy.orm import Session
from app.models.db_emaillog import EmailLog
from app.models.email_models import EmailRequest

class EmailRepository:
    """Repository for email log operations"""
    
    @staticmethod
    async def create_email_log(db: Session, email_request: EmailRequest, message_id: str = None, status: str = "Pending", is_success: bool = True, error_message: str = None):
        """Create a new email log entry"""
        
        # Convert recipients, cc, and bcc to JSON strings
        recipients_json = json.dumps([{"email": r.email, "name": r.name} for r in email_request.recipients])
        
        cc_json = None
        if email_request.cc:
            cc_json = json.dumps([{"email": r.email, "name": r.name} for r in email_request.cc])
        
        bcc_json = None
        if email_request.bcc:
            bcc_json = json.dumps([{"email": r.email, "name": r.name} for r in email_request.bcc])
        
        # Create email log
        email_log = EmailLog(
            sender_email=email_request.sender,
            sender_name=email_request.sender_name,
            recipients=recipients_json,
            cc=cc_json,
            bcc=bcc_json,
            subject=email_request.content.subject,
            message_id=message_id,
            status=status,
            is_success=is_success,
            error_message=error_message
        )
        
        # Add to database
        db.add(email_log)
        db.commit()
        db.refresh(email_log)
        
        return email_log
    
    @staticmethod
    def get_email_logs(db: Session, skip: int = 0, limit: int = 100):
        """Get all email logs with pagination"""
        return db.query(EmailLog).order_by(EmailLog.sent_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_email_log_by_id(db: Session, email_log_id: int):
        """Get a specific email log by ID"""
        return db.query(EmailLog).filter(EmailLog.id == email_log_id).first()