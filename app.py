# AWS SES Email Sender for FastAPI

import boto3
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from dotenv import load_dotenv
import os
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN

load_dotenv()  
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")  
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")  
AWS_REGION = os.getenv("AWS_Region")  

app = FastAPI(title="Email Sender API with AWS SES")



# api_key_header = APIKeyHeader(name="X-API-Key")

# def verify_api_key(api_key: str = Depends(api_key_header)):
#     if api_key != API_KEY:
#         raise HTTPException(
#             status_code=HTTP_403_FORBIDDEN,
#             detail="Invalid API key"
#         )
#     return api_key


class EmailRecipient(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class EmailContent(BaseModel):
    subject: str
    body_text: str
    body_html: Optional[str] = None

class EmailRequest(BaseModel):
    sender: EmailStr
    sender_name: Optional[str] = None
    recipients: List[EmailRecipient]
    # cc: Optional[List[EmailRecipient]] = None
    # bcc: Optional[List[EmailRecipient]] = None
    content: EmailContent
    # reply_to: Optional[List[EmailStr]] = None

class EmailResponse(BaseModel):
    message_id: str
    status: str


def get_ses_client():
    return boto3.client(
        'ses',
        aws_access_key_id= AWS_ACCESS_KEY_ID,
        aws_secret_access_key= AWS_SECRET_ACCESS_KEY,
        region_name= AWS_REGION
    )

@app.post("/send-email", response_model=EmailResponse)
async def send_email(email_request: EmailRequest):
    try:
       
        ses_client = get_ses_client()
        
       
        to_addresses = [
            {"Email": recipient.email, "Name": recipient.name if recipient.name else recipient.email}
            for recipient in email_request.recipients
        ]
        
        # Format CC if provided
        # cc_addresses = []
        # if email_request.cc:
        #     cc_addresses = [
        #         {"Email": recipient.email, "Name": recipient.name if recipient.name else recipient.email}
        #         for recipient in email_request.cc
        #     ]
        
        # Format BCC if provided
        # bcc_addresses = []
        # if email_request.bcc:
        #     bcc_addresses = [
        #         {"Email": recipient.email, "Name": recipient.name if recipient.name else recipient.email}
        #         for recipient in email_request.bcc
        #     ]
        
        
        sender = f"{email_request.sender_name} <{email_request.sender}>" if email_request.sender_name else email_request.sender
        
        
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
        
       
        if email_request.content.body_html:
            message['Message']['Body']['Html'] = {
                'Data': email_request.content.body_html,
                'Charset': 'UTF-8'
            }
        
        # Add CC if provided
        # if email_request.cc:
        #     message['Destination']['CcAddresses'] = [recipient.email for recipient in email_request.cc]
        
        # Add BCC if provided
        # if email_request.bcc:
        #     message['Destination']['BccAddresses'] = [recipient.email for recipient in email_request.bcc]
        
        # Add Reply-To if provided
        # if email_request.reply_to:
        #     message['ReplyToAddresses'] = email_request.reply_to
        
        
        response = ses_client.send_email(**message)
        
        return EmailResponse(
            message_id=response['MessageId'],
            status="Email sent successfully"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)