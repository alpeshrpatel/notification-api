import boto3
from botocore.exceptions import ClientError
from sqlalchemy.orm import Session
from app.models.email_models import EmailRequest
from app.repositories.email_repositories import EmailRepository
from app.config import settings

class SESService:
    """AWS SES service for sending emails"""
    
    @staticmethod
    def get_ses_client():
        """Create and return an Amazon SES client"""
        return boto3.client(
            'ses',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
    
    @staticmethod
    async def send_email(email_request: EmailRequest, db: Session):
        """Send email using AWS SES service and log the operation"""
        try:
            # Log the email sending attempt
            email_log = await EmailRepository.create_email_log(
                db=db, 
                email_request=email_request,
                status="Sending"
            )
            
            ses_client = SESService.get_ses_client()
            
            # Format sender
            sender = f"{email_request.sender_name} <{email_request.sender}>" if email_request.sender_name else email_request.sender
            
            # Prepare the message
            message = {
                'Source': sender,
                'Destination': {
                    'ToAddresses': [recipient.email for recipient in email_request.recipients],
                },
                'Message': {
                    'Subject': {
                        'Data': email_request.content.subject,
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Text': {
                            'Data': email_request.content.body_text,
                            'Charset': 'UTF-8'
                        }
                    }
                }
            }
            
            # Add HTML body if provided
            if email_request.content.body_html:
                message['Message']['Body']['Html'] = {
                    'Data': email_request.content.body_html,
                    'Charset': 'UTF-8'
                }
            
            # Add CC if provided
            if email_request.cc:
                message['Destination']['CcAddresses'] = [recipient.email for recipient in email_request.cc]
            
            # Add BCC if provided
            if email_request.bcc:
                message['Destination']['BccAddresses'] = [recipient.email for recipient in email_request.bcc]
            
            # Add Reply-To if provided
            if email_request.reply_to:
                message['ReplyToAddresses'] = email_request.reply_to
            
            # Send the email
            response = ses_client.send_email(**message)
            message_id = response['MessageId']
            
            # Update the email log with success information
            await EmailRepository.create_email_log(
                db=db,
                email_request=email_request,
                message_id=message_id,
                status="Sent",
                is_success=True
            )
            
            return {
                "message_id": message_id,
                "status": "Email sent successfully"
            }
        
        except ClientError as e:
            error_message = str(e)
            
            # Log the failure
            if 'email_log' in locals():
                await EmailRepository.create_email_log(
                    db=db,
                    email_request=email_request,
                    status="Failed",
                    is_success=False,
                    error_message=error_message
                )
            
            raise Exception(f"Failed to send email: {error_message}")