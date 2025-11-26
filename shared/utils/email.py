"""
Email utility functions for sending notifications via SMTP.
"""
import logging
from typing import Optional, List
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


def get_active_smtp_server():
    """
    Get the active SMTP server configuration.
    Returns the first enabled SMTP server, or None if none exists.
    """
    from shared.models import SMTPServer
    
    try:
        return SMTPServer.objects.filter(is_enabled=1).first()
    except Exception as e:
        logger.error(f"Error getting active SMTP server: {e}")
        return None


def send_email_notification(
    subject: str,
    message: str,
    recipient_email: str,
    recipient_name: Optional[str] = None,
    html_message: Optional[str] = None,
) -> bool:
    """
    Send an email notification using the active SMTP server.
    
    Args:
        subject: Email subject
        message: Plain text message body
        recipient_email: Recipient email address
        recipient_name: Optional recipient name
        html_message: Optional HTML message body
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    smtp_server = get_active_smtp_server()
    
    if not smtp_server:
        logger.warning("No active SMTP server configured. Email not sent.")
        return False
    
    if not recipient_email:
        logger.warning(f"No recipient email provided. Email not sent.")
        return False
    
    try:
        # Configure Django email backend with SMTP settings
        from_email = smtp_server.from_email
        if smtp_server.from_name:
            from_email = f"{smtp_server.from_name} <{smtp_server.from_email}>"
        
        # Create email message
        email = EmailMessage(
            subject=subject,
            body=html_message if html_message else message,
            from_email=from_email,
            to=[recipient_email],
        )
        
        if html_message:
            email.content_subtype = 'html'
        
        # Configure SMTP backend dynamically
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        # Use Django's email backend but configure it with our SMTP settings
        # We'll use a custom approach since Django's email backend doesn't support
        # dynamic SMTP configuration easily
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = recipient_email
        
        # Add plain text and HTML parts
        text_part = MIMEText(message, 'plain', 'utf-8')
        msg.attach(text_part)
        
        if html_message:
            html_part = MIMEText(html_message, 'html', 'utf-8')
            msg.attach(html_part)
        
        # Connect to SMTP server
        if smtp_server.use_ssl:
            server = smtplib.SMTP_SSL(
                smtp_server.host,
                smtp_server.port,
                timeout=smtp_server.timeout
            )
        else:
            server = smtplib.SMTP(
                smtp_server.host,
                smtp_server.port,
                timeout=smtp_server.timeout
            )
        
        # Enable TLS if needed
        if smtp_server.use_tls and not smtp_server.use_ssl:
            server.starttls()
        
        # Authenticate
        if smtp_server.username and smtp_server.password:
            server.login(smtp_server.username, smtp_server.password)
        
        # Send email
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Email sent successfully to {recipient_email}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending email to {recipient_email}: {e}", exc_info=True)
        return False


def send_notification_email(
    notification_type: str,
    notification_message: str,
    recipient_user,
    notification_url: Optional[str] = None,
    company_name: Optional[str] = None,
) -> bool:
    """
    Send a formatted email notification based on notification type.
    
    Args:
        notification_type: Type of notification (e.g., 'approval_pending', 'approved')
        notification_message: The notification message text
        recipient_user: Django User object (must have email)
        notification_url: Optional URL to include in email
        company_name: Optional company name for context
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    if not recipient_user or not recipient_user.email:
        logger.warning(f"User {recipient_user} has no email address. Email not sent.")
        return False
    
    # Determine subject based on notification type
    if notification_type == 'approval_pending':
        subject = _("Pending Approval Request")
    elif notification_type == 'approved':
        subject = _("Request Approved")
    else:
        subject = _("Notification")
    
    if company_name:
        subject = f"[{company_name}] {subject}"
    
    # Create HTML email body
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #3b82f6; color: white; padding: 20px; text-align: center; }}
            .content {{ background-color: #f9fafb; padding: 20px; }}
            .message {{ background-color: white; padding: 15px; border-left: 4px solid #3b82f6; margin: 15px 0; }}
            .button {{ display: inline-block; padding: 10px 20px; background-color: #3b82f6; color: white; text-decoration: none; border-radius: 5px; margin-top: 15px; }}
            .footer {{ text-align: center; color: #6b7280; font-size: 12px; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>{subject}</h2>
            </div>
            <div class="content">
                <div class="message">
                    <p>{notification_message}</p>
                </div>
    """
    
    if notification_url:
        html_message += f"""
                <a href="{notification_url}" class="button">{_("View Details")}</a>
        """
    
    html_message += """
            </div>
            <div class="footer">
                <p>""" + _("This is an automated notification from invproj system.") + """</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version
    plain_message = f"{notification_message}\n\n"
    if notification_url:
        plain_message += f"{_('View Details')}: {notification_url}\n"
    plain_message += f"\n{_('This is an automated notification from invproj system.')}"
    
    return send_email_notification(
        subject=str(subject),
        message=plain_message,
        recipient_email=recipient_user.email,
        recipient_name=recipient_user.get_full_name() or recipient_user.username,
        html_message=html_message,
    )

