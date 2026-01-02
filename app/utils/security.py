import hashlib
import hmac
from app.config.settings import settings


def verify_signature(payload: str, signature: str) -> bool:
    """
    Verify webhook signature using HMAC
    This is a generic function - you might need to adapt it for specific services
    """
    try:
        expected_signature = hmac.new(
            settings.SECRET_KEY.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures
        return hmac.compare_digest(f"sha256={expected_signature}", signature)
    except Exception:
        return False


def verify_api_key(api_key: str) -> bool:
    """Verify API key"""
    return api_key == settings.API_KEY