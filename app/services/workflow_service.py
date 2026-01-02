from typing import Dict, Any, Callable
from app.services.notification_service import NotificationService
from app.services.ai_service import AIService
import logging
logger = logging.getLogger(__name__)

class WorkflowService:
    def __init__(self):
        self.notification_service = NotificationService()
        self.ai_service = AIService()
        self.event_handlers = {
            "on_new_message": self._handle_new_message,
            "on_lead_created": self._handle_lead_created,
            "on_hot_lead": self._handle_hot_lead,
        }

    async def trigger_event(self, event_name: str, data: Dict[str, Any]):
        """Trigger a workflow event"""
        logger.info(f"--- trigger_event started for {event_name} ---")
        if event_name in self.event_handlers:
            await self.event_handlers[event_name](data)
        else:
            logger.warning(f"Unknown event: {event_name}")
        logger.info(f"--- trigger_event finished for {event_name} ---")

    async def _handle_lead_created(self, data: Dict[str, Any]):
        """Handle new lead created event"""
        logger.info("--- _handle_lead_created started ---")
        # Send notification about new lead
        await self.notification_service.notify_new_lead(data)
        logger.info("--- _handle_lead_created finished ---")

    async def _handle_hot_lead(self, data: Dict[str, Any]):
        """Handle hot lead event"""
        logger.info("--- _handle_hot_lead started ---")
        # Send urgent notification about hot lead
        await self.notification_service.notify_hot_lead(data)
        logger.info("--- _handle_hot_lead finished ---")
    async def _handle_new_message(self, data: Dict[str, Any]):
        """Handle new message event"""
        logger.info("--- _handle_new_message started ---")
        # Placeholder for handling new message
        logger.info("--- _handle_new_message finished ---")

    def register_handler(self, event_name: str, handler: Callable):
        """Register a custom event handler"""
        self.event_handlers[event_name] = handler