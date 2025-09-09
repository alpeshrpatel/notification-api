import boto3
import logging
from botocore.exceptions import ClientError
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.email_models import EmailRequest
from app.repositories.email_repositories import EmailRepository
from app.config import settings

logger = logging.getLogger(__name__)

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
    def get_sns_client():
        """Create and return an Amazon SNS client"""
        return boto3.client(
            'sns',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
    
    @staticmethod
    def setup_real_time_tracking():
        """
        One-time setup to enable real-time email tracking
        Creates configuration set and SNS topic for webhook notifications
        """
        ses_client = SESService.get_ses_client()
        sns_client = SESService.get_sns_client()
        
        configuration_set_name = 'my-first-configuration-set'
        sns_topic_name = 'ses-events'
        webhook_url = "https://api.communication.gotestli.com/api/email/events"  # Your domain + webhook endpoint
        
        try:
            # Step 1: Create SES Configuration Set
            try:
                ses_client.create_configuration_set(
                    ConfigurationSet={'Name': configuration_set_name}
                )
                logger.info(f"Created SES configuration set: {configuration_set_name}")
            except ses_client.exceptions.ConfigurationSetAlreadyExistsException:
                logger.info(f"Configuration set {configuration_set_name} already exists")
            
            # Step 2: Create SNS Topic
            topic_response = sns_client.create_topic(Name=sns_topic_name)
            topic_arn = topic_response['TopicArn']
            logger.info(f"SNS Topic ARN: {topic_arn}")
            
            # Step 3: Subscribe webhook endpoint to SNS topic
            subscription_response = sns_client.subscribe(
                TopicArn=topic_arn,
                Protocol='https',
                Endpoint=webhook_url
            )
            logger.info(f"Subscribed webhook {webhook_url} to SNS topic")
            
            # Step 4: Configure SES to publish events to SNS
            ses_client.create_configuration_set_event_destination(
                ConfigurationSetName=configuration_set_name,
                EventDestination={
                    'Name': 'webhook-destination',
                    'Enabled': True,
                    'MatchingEventTypes': [
                        'send',        # Email sent
                        'bounce',      # Email bounced
                        'complaint',   # Spam complaint
                        'delivery',    # Email delivered
                        'open',        # Email opened
                        'click'        # Link clicked
                    ],
                    'SNSDestination': {
                        'TopicARN': topic_arn
                    }
                }
            )
            
            logger.info("SES real-time tracking configured successfully!")
            
            return {
                'status': 'success',
                'configuration_set': configuration_set_name,
                'sns_topic_arn': topic_arn,
                'webhook_url': webhook_url,
                'next_step': f'Confirm SNS subscription by visiting AWS Console or wait for confirmation email'
            }
            
        except Exception as e:
            logger.error(f"Error setting up real-time tracking: {e}")
            raise HTTPException(status_code=500, detail=f"Setup failed: {str(e)}")
        
    @staticmethod
    async def send_email(email_request: EmailRequest, db: Session):
        """Send email using AWS SES service and log the operation"""
        print("Setting up real-time tracking...")
        # SESService.setup_real_time_tracking()
        try:
            # Log the email sending attempt
            email_log = await EmailRepository.create_email_log(
                db=db, 
                email_request=email_request,
                message_id=0,
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
                },
                'ConfigurationSetName': "my-first-configuration-set"
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
                    message_id=0,
                    status="Failed",
                    is_success=False,
                    error_message=error_message
                )
            
            raise Exception(f"Failed to send email: {error_message}")