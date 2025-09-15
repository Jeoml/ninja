"""
Email service for sending OTP codes.
"""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .config import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, FROM_EMAIL, APP_NAME

class EmailService:
    """Email service for sending OTP codes."""
    
    def __init__(self):
        self.smtp_server = SMTP_SERVER
        self.smtp_port = SMTP_PORT
        self.username = SMTP_USERNAME
        self.password = SMTP_PASSWORD
        self.from_email = FROM_EMAIL
    
    def send_otp_email(self, to_email: str, otp_code: str) -> bool:
        """Send OTP code via email."""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = f"Your {APP_NAME} Verification Code"
            message["From"] = self.from_email
            message["To"] = to_email
            
            # Create HTML content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .otp-code {{ background: #fff; border: 2px dashed #667eea; padding: 20px; text-align: center; margin: 20px 0; border-radius: 8px; }}
                    .otp-number {{ font-size: 32px; font-weight: bold; color: #667eea; letter-spacing: 5px; }}
                    .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 14px; }}
                    .warning {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🔐 {APP_NAME}</h1>
                        <p>Your verification code is ready!</p>
                    </div>
                    <div class="content">
                        <h2>Hello!</h2>
                        <p>You requested a verification code for your email address. Here's your One-Time Password (OTP):</p>
                        
                        <div class="otp-code">
                            <div class="otp-number">{otp_code}</div>
                        </div>
                        
                        <div class="warning">
                            <strong>⚠️ Important:</strong>
                            <ul>
                                <li>This code will expire in <strong>5 minutes</strong></li>
                                <li>Don't share this code with anyone</li>
                                <li>If you didn't request this code, please ignore this email</li>
                            </ul>
                        </div>
                        
                        <p>Enter this code in the verification form to complete your authentication.</p>
                        
                        <div class="footer">
                            <p>This is an automated message from {APP_NAME}.</p>
                            <p>If you have any questions, please contact our support team.</p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create plain text version
            text_content = f"""
            {APP_NAME} - Email Verification
            
            Hello!
            
            You requested a verification code for your email address.
            
            Your One-Time Password (OTP) is: {otp_code}
            
            Important:
            - This code will expire in 5 minutes
            - Don't share this code with anyone
            - If you didn't request this code, please ignore this email
            
            Enter this code in the verification form to complete your authentication.
            
            ---
            This is an automated message from {APP_NAME}.
            """
            
            # Convert to MIMEText objects
            part1 = MIMEText(text_content, "plain")
            part2 = MIMEText(html_content, "html")
            
            # Add parts to message
            message.attach(part1)
            message.attach(part2)
            
            # Create secure connection and send email
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.username, self.password)
                server.send_message(message)
            
            print(f"✅ OTP email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email to {to_email}: {str(e)}")
            return False
    
    def test_connection(self) -> bool:
        """Test email service connection."""
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.username, self.password)
            print("✅ Email service connection successful")
            return True
        except Exception as e:
            print(f"❌ Email service connection failed: {str(e)}")
            return False

# Global email service instance
email_service = EmailService()
