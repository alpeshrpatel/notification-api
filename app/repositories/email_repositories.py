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
from sqlalchemy import func, case
from datetime import datetime, timedelta
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
        # db.add(email_log)
        # db.commit()
        # db.refresh(email_log)
        async with db.cursor() as cursor:
            await cursor.execute(
                """
                INSERT INTO email_logs (
                    sender_email, sender_name, recipients, cc, bcc,
                    subject, message_id, status, is_success, error_message,app_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
                """,
                (
                    email_request.sender,
                    email_request.sender_name,
                    recipients_json,
                    cc_json,
                    bcc_json,
                    email_request.content.subject,
                    message_id,
                    status,
                    is_success,
                    error_message, email_request.app_id 
                )
            )
            await db.commit()
        
        return email_log
    
    # @staticmethod
    # def get_email_logs(db: Session, skip: int = 0, limit: int = 100):
    #     """Get all email logs with pagination"""
    #     return db.query(EmailLog).order_by(EmailLog.sent_at.desc()).offset(skip).limit(limit).all()
    
    # @staticmethod
    # def get_email_log_by_id(db: Session, email_log_id: int):
    #     """Get a specific email log by ID"""
    #     return db.query(EmailLog).filter(EmailLog.id == email_log_id).first()
    
    # @staticmethod
    # async def update_status(db: Session, message_id: str, status: str, is_success: bool):
    #     log = db.query(EmailLog).filter(EmailLog.message_id == message_id).first()
    #     if log:
    #         log.status = status
    #         log.is_success = is_success
    #         db.commit()
    #         db.refresh(log)
    #     return log

    # @staticmethod
    # async def increment_open_count(db: Session, message_id: str):
    #     log = db.query(EmailLog).filter(EmailLog.message_id == message_id).first()
    #     if log:
    #         log.opens = (log.opens or 0) + 1
    #         db.commit()
    #         db.refresh(log)
    #     return log

    # @staticmethod
    # async def increment_click_count(db: Session, message_id: str):
    #     log = db.query(EmailLog).filter(EmailLog.message_id == message_id).first()
    #     if log:
    #         log.clicks = (log.clicks or 0) + 1
    #         db.commit()
    #         db.refresh(log)
    #     return log
    
    # @staticmethod
    # def get_email_metrics(db: Session, months: int = 3):
    #     start_date = datetime.utcnow() - timedelta(days=30 * months)

    #     results = (
    #         db.query(
    #             func.date_trunc('day', EmailLog.sent_at).label('day'),
    #             func.count().label('total'),
    #             func.sum(case((EmailLog.is_success == True, 1), else_=0)).label('success'),
    #             func.sum(case((EmailLog.status == "Bounced", 1), else_=0)).label('bounced'),
    #             func.sum(case((EmailLog.status == "Complaint", 1), else_=0)).label('complaints'),
    #             func.sum(EmailLog.opens).label('opens'),
    #             func.sum(EmailLog.clicks).label('clicks'),
    #         )
    #         .filter(EmailLog.sent_at >= start_date)
    #         .group_by(func.date_trunc('day', EmailLog.sent_at))
    #         .order_by(func.date_trunc('day', EmailLog.sent_at))
    #         .all()
    #     )

    #     return [
    #         {
    #             "date": row.day.strftime("%Y-%m-%d"),
    #             "total": row.total,
    #             "success": int(row.success or 0),
    #             "bounced": int(row.bounced or 0),
    #             "complaints": int(row.complaints or 0),
    #             "opens": int(row.opens or 0),
    #             "clicks": int(row.clicks or 0),
    #         }
    #         for row in results
    #     ]
    
    
    @staticmethod
    async def get_email_logs(db, skip: int = 0, limit: int = 100):
        """Get all email logs with pagination"""
        async with db.cursor() as cursor:
            await cursor.execute(
                """
                SELECT * FROM email_logs 
                ORDER BY sent_at DESC 
                OFFSET %s LIMIT %s
                """,
                (skip, limit)
            )
            return await cursor.fetchall()
    
    @staticmethod
    async def get_email_log_by_id(db, email_log_id: int):
        """Get a specific email log by ID"""
        async with db.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM email_logs WHERE id = %s",
                (email_log_id,)
            )
            return await cursor.fetchone()
    
    @staticmethod
    async def update_status(db, message_id: str, status: str, is_success: bool):
        """Update email status"""
        async with db.cursor() as cursor:
            await cursor.execute(
                """
                UPDATE email_logs 
                SET status = %s, is_success = %s 
                WHERE message_id = %s
                """,
                (status, is_success, message_id)
            )
            await db.commit()
            
            # Return updated record
            await cursor.execute(
                "SELECT * FROM email_logs WHERE message_id = %s",
                (message_id,)
            )
            return await cursor.fetchone()

    @staticmethod
    async def increment_open_count(db, message_id: str):
        """Increment email open count"""
        async with db.cursor() as cursor:
            await cursor.execute(
                """
                UPDATE email_logs 
                SET opens = COALESCE(opens, 0) + 1 
                WHERE message_id = %s
                """,
                (message_id,)
            )
            await db.commit()
            
            # Return updated record
            await cursor.execute(
                "SELECT * FROM email_logs WHERE message_id = %s",
                (message_id,)
            )
            return await cursor.fetchone()

    @staticmethod
    async def increment_click_count(db, message_id: str):
        """Increment email click count"""
        async with db.cursor() as cursor:
            await cursor.execute(
                """
                UPDATE email_logs 
                SET clicks = COALESCE(clicks, 0) + 1 
                WHERE message_id = %s
                """,
                (message_id,)
            )
            await db.commit()
            
            # Return updated record
            await cursor.execute(
                "SELECT * FROM email_logs WHERE message_id = %s",
                (message_id,)
            )
            return await cursor.fetchone()
    
    @staticmethod
    async def get_email_metrics(db, months: int = 3):
        """Get email metrics using raw SQL (MySQL compatible)"""
        start_date = datetime.utcnow() - timedelta(days=30 * months)
        print(f"Calculating metrics since: {start_date}")
        async with db.cursor() as cursor:
            
            await cursor.execute(
                """
                SELECT 
                    DATE(sent_at) as day,
                    COUNT(*) as total,
                    SUM(CASE WHEN is_success = 1 THEN 1 ELSE 0 END) as success,
                    SUM(CASE WHEN status = 'Bounced' THEN 1 ELSE 0 END) as bounced,
                    SUM(CASE WHEN status = 'Complaint' THEN 1 ELSE 0 END) as complaints,
                    SUM(COALESCE(opens, 0)) as opens,
                    SUM(COALESCE(clicks, 0)) as clicks
                FROM email_logs
                WHERE sent_at >= %s
                GROUP BY DATE(sent_at)
                ORDER BY DATE(sent_at)
                """,
                (start_date,)
            )
            
            results = await cursor.fetchall()
            
            print("Raw metrics results:",results)
            
            return [
                {
                    "date": row[0].strftime("%Y-%m-%d") if hasattr(row[0], 'strftime') else str(row[0]),
                    "total": row[1],
                    "success": int(row[2] or 0),
                    "bounced": int(row[3] or 0),
                    "complaints": int(row[4] or 0),
                    "opens": int(row[5] or 0),
                    "clicks": int(row[6] or 0),
                }
                for row in results
            ]