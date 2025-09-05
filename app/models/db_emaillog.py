# from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
# from sqlalchemy.sql import func
# from app.database.database import Base

# class EmailLog(Base):
#     """Model for storing email sending logs in the database"""
#     __tablename__ = "email_logs"
    
#     id = Column(Integer, primary_key=True, index=True)
#     sender_email = Column(String(255), nullable=False)
#     recipient_email = Column(String(255), nullable=False)
#     subject = Column(String(500), nullable=False)
#     sent_at = Column(DateTime, default=func.now(), nullable=False)
#     error_message = Column(Text, nullable=True)
#     is_success = Column(Boolean, default=True, nullable=False)

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from app.database.database import Base

class EmailLog(Base):
    """Model for storing email sending logs in the database"""
    __tablename__ = "email_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_email = Column(String(255), nullable=False)
    sender_name = Column(String(255), nullable=True)
    recipients = Column(Text, nullable=False)  # Store as JSON string
    cc = Column(Text, nullable=True)  # Store as JSON string
    bcc = Column(Text, nullable=True)  # Store as JSON string
    subject = Column(String(500), nullable=False)
    message_id = Column(String(100), nullable=True)
    status = Column(String(50), nullable=False)
    sent_at = Column(DateTime, default=func.now(), nullable=False)
    error_message = Column(Text, nullable=True)
    is_success = Column(Boolean, default=True, nullable=False)
    
    opens = Column(Integer, default=0, nullable=False)       # Number of times email was opened
    clicks = Column(Integer, default=0, nullable=False)      # Number of clicks
    bounces = Column(Integer, default=0, nullable=False)     # Bounce count
    complaints = Column(Integer, default=0, nullable=False)  # Complaint count
