import httpx
from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.logging import logger


class N8NClient:
    @staticmethod
    def trigger_webhook_sync(
        endpoint_path: str,
        payload: Dict[str, Any],
        timeout: float = 0.8
    ) -> Optional[Dict[str, Any]]:
        """
        Triggers an n8n webhook endpoint with timeout and exception containment.
        If n8n is not running or unreachable, gracefully logs and continues.
        """
        if not settings.N8N_ENABLED:
            return None

        url = f"{settings.N8N_WEBHOOK_URL_BASE.rstrip('/')}/{endpoint_path.lstrip('/')}"
        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Token": settings.N8N_WEBHOOK_AUTH_TOKEN
        }

        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.post(url, json=payload, headers=headers)
                if response.status_code in [200, 201, 204]:
                    logger.info(f"Successfully notified n8n webhook at {url}")
                    try:
                        return response.json()
                    except Exception:
                        return {"status": "ok"}
                else:
                    logger.warning(f"n8n webhook {url} returned HTTP {response.status_code}")
                    return None
        except Exception as e:
            logger.debug(f"n8n webhook notification skipped (service offline or unconfigured): {e}")
            return None
