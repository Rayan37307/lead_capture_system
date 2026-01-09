import smtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
from app.config.settings import settings
from typing import List, Dict, Any


import logging


logger = logging.getLogger(__name__)





class NotificationService:
    def __init__(self):
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            self.twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        else:
            self.twilio_client = None


    # ... (other methods)





    async def send_email_notification(self, subject: str, body: str, recipients: List[str]):
        """Send email notification"""
        logger.info("--- send_email_notification started ---")
        if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
            logger.warning("Email settings not configured")
            return

        def send_email():
            try:
                msg = MIMEMultipart()
                msg['From'] = settings.SMTP_USERNAME
                msg['To'] = ", ".join(recipients)
                msg['Subject'] = subject

                msg.attach(MIMEText(body, 'html'))

                server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
                server.starttls()
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                text = msg.as_string()
                server.sendmail(settings.SMTP_USERNAME, recipients, text)
                server.quit()
            except Exception as e:
                logger.error(f"Error sending email: {e}", exc_info=True)
        
        await asyncio.to_thread(send_email)
        logger.info("--- send_email_notification finished ---")

    async def send_whatsapp_notification(self, message: str, to_number: str):
        """Send WhatsApp notification to admin"""
        logger.info("--- send_whatsapp_notification started ---")
        if not self.twilio_client or not settings.ADMIN_WHATSAPP_NUMBER:
            logger.warning("WhatsApp settings not configured")
            return

        def send_whatsapp():
            try:
                self.twilio_client.messages.create(
                    from_=f"whatsapp:{settings.WHATSAPP_PHONE_NUMBER_ID}",
                    body=message,
                    to=f"whatsapp:{settings.ADMIN_WHATSAPP_NUMBER}"
                )
            except Exception as e:
                logger.error(f"Error sending WhatsApp notification: {e}", exc_info=True)
        
        await asyncio.to_thread(send_whatsapp)
        logger.info("--- send_whatsapp_notification finished ---")


    async def notify_new_lead(self, lead_data: Dict[str, Any], tenant_id: str):
        """Send notification for new lead"""
        logger.info(f"--- notify_new_lead started for tenant_id: {tenant_id} ---")
        subject = "New Lead Captured"
        body = f"""
        <h2>New Lead Captured!</h2>
        <p><strong>Name:</strong> {lead_data.get('name', 'N/A')}</p>
        <p><strong>Email:</strong> {lead_data.get('email', 'N/A')}</p>
        <p><strong>Phone:</strong> {lead_data.get('phone', 'N/A')}</p>
        <p><strong>Source:</strong> {lead_data.get('source', 'N/A')}</p>
        <p><strong>Intent:</strong> {lead_data.get('intent', 'N/A')}</p>
        <p><strong>Created At:</strong> {lead_data.get('created_at', 'N/A')}</p>
        <p><strong>Tenant ID:</strong> {tenant_id}</p>
        """

        # Send email notifications
        if settings.NOTIFICATION_EMAILS:
            await self.send_email_notification(subject, body, settings.NOTIFICATION_EMAILS)

        # Send WhatsApp notification
        whatsapp_msg = f"New lead: {lead_data.get('name', 'N/A')} from {lead_data.get('source', 'N/A')} - Intent: {lead_data.get('intent', 'N/A')}. Tenant ID: {tenant_id}"
        await self.send_whatsapp_notification(whatsapp_msg, settings.ADMIN_WHATSAPP_NUMBER)
        logger.info("--- notify_new_lead finished ---")


    async def notify_hot_lead(self, lead_data: Dict[str, Any], tenant_id: str):
        """Send urgent notification for hot lead"""
        logger.info(f"--- notify_hot_lead started for tenant_id: {tenant_id} ---")
        subject = "🚨 HOT LEAD ALERT! 🚨"
        body = f"""
        <h2>🚨 URGENT: HOT LEAD ALERT! 🚨</h2>
        <p><strong>Name:</strong> {lead_data.get('name', 'N/A')}</p>
        <p><strong>Email:</strong> {lead_data.get('email', 'N/A')}</p>
        <p><strong>Phone:</strong> {lead_data.get('phone', 'N/A')}</p>
        <p><strong>Source:</strong> {lead_data.get('source', 'N/A')}</p>
        <p><strong>Intent:</strong> {lead_data.get('intent', 'N/A')}</p>
        <p><strong>Created At:</strong> {lead_data.get('created_at', 'N/A')}</p>
        <p><strong>Messages:</strong></p>
        <ul>
        {" ".join([f"<li>{msg.get('content', '')}</li>" for msg in lead_data.get('messages', [])])}
        </ul>
        <p><strong>Tenant ID:</strong> {tenant_id}</p>
        """

        # Send email notifications
        if settings.NOTIFICATION_EMAILS:
            await self.send_email_notification(subject, body, settings.NOTIFICATION_EMAILS)

        # Send WhatsApp notification
        whatsapp_msg = f"🚨 HOT LEAD ALERT! 🚨 {lead_data.get('name', 'N/A')} from {lead_data.get('source', 'N/A')} - Ready to buy! Tenant ID: {tenant_id}"
        await self.send_whatsapp_notification(whatsapp_msg, settings.ADMIN_WHATSAPP_NUMBER)
        logger.info("--- notify_hot_lead finished ---")



