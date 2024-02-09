"""SMSto platform for notify component."""
from http import HTTPStatus
import json
import logging

from aiohttp.hdrs import CONTENT_TYPE
import requests
import voluptuous as vol

from homeassistant.components.notify import PLATFORM_SCHEMA, BaseNotificationService
from homeassistant.const import (
    CONF_API_KEY,
    CONF_RECIPIENT,
    CONF_SENDER,
    CONTENT_TYPE_JSON,
)
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

BASE_API_URL = "https://api.sms.to"
DEFAULT_SENDER = "hass"
TIMEOUT = 5

PLATFORM_SCHEMA = vol.Schema(
    vol.All(
        PLATFORM_SCHEMA.extend(
            {
                vol.Required(CONF_API_KEY): cv.string,  # This will now hold the Bearer token
                vol.Required(CONF_RECIPIENT, default=[]): vol.All(
                    cv.ensure_list, [cv.string]
                ),
                vol.Optional(CONF_SENDER, default=DEFAULT_SENDER): cv.string,
            }
        )
    )
)


def get_service(hass, config, discovery_info=None):
    """Get the SMSto notification service."""
    return SMStoNotificationService(config)


class SMStoNotificationService(BaseNotificationService):
    """Implementation of a notification service for the sms.to service."""

    def __init__(self, config):
        """Initialize the service."""
        self.bearer_token = config[CONF_API_KEY]  # Store the Bearer token
        self.recipients = config[CONF_RECIPIENT]
        self.sender = config[CONF_SENDER]

    def send_message(self, message="", **kwargs):
        """Send a message to a user."""
        ploads = {
            "message": message,
            "to": ",".join(self.recipients),
            "bypass_optout": True,  # Assuming this is always desired
            "sender_id": self.sender,
            "callback_url": kwargs.get("callback_url", ""),  # Optional callback
        }

        api_url = f"{BASE_API_URL}/sms/send"
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",  # Add Bearer token to headers
            "Content-Type": "application/json",
        }

        resp = requests.post(
            api_url,
            timeout=TIMEOUT,
            headers=headers,
            data=json.dumps(ploads),
        )
        if resp.status_code == HTTPStatus.OK:
            return

        obj = json.loads(resp.text)
        response_msg = obj.get("message")
        response_code = obj.get("errorCode")
        _LOGGER.error(
            "Error %s : %s (Code %s)", resp.status_code, response_msg, response_code
        )
