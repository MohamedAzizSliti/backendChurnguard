import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_username)
        
    async def send_email(self, to_email: str, to_name: str, issue: str) -> tuple[bool, Optional[str]]:
        """
        Send an email notification
        Returns: (success: bool, error_message: Optional[str])
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = f"Issue Notification: {issue}"
            
            # Email body
            body = f"""
            Dear {to_name},

            We wanted to inform you about the following issue:

            Issue: {issue}

            Please take the necessary action to resolve this matter.

            Best regards,
            Customer Support Team
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            if not self.smtp_username or not self.smtp_password:
                # For development/testing - just log the email
                logging.info(f"EMAIL SIMULATION - To: {to_email}, Subject: {msg['Subject']}")
                logging.info(f"EMAIL BODY: {body}")
                return True, None
            
            # Real email sending
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            
            text = msg.as_string()
            server.sendmail(self.from_email, to_email, text)
            server.quit()
            
            return True, None
            
        except Exception as e:
            error_msg = f"Failed to send email to {to_email}: {str(e)}"
            logging.error(error_msg)
            return False, error_msg
    
    def is_configured(self) -> bool:
        """Check if email service is properly configured"""
        return bool(self.smtp_username and self.smtp_password) 