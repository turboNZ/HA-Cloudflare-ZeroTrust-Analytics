import logging

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_API_KEY, CONF_EMAIL
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
import asyncio
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)

CONF_API_KEY = "api_key"
CONF_EMAIL = "email"
CONF_ACCOUNT_ID = "account_id"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_API_KEY): cv.string,
    vol.Required(CONF_EMAIL): cv.string,
    vol.Required(CONF_ACCOUNT_ID): cv.string,
})

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    api_key = config[CONF_API_KEY]
    email = config[CONF_EMAIL]
    account_id = config[CONF_ACCOUNT_ID]
    cloudflare_api = CloudflareAPI(hass, api_key, email, account_id)
    sensors = [
        CloudflareApplicationsAccessedSensor(cloudflare_api),
        CloudflareFailedLoginsSensor(cloudflare_api)
    ]
    
    # Dictionary to keep track of existing user sensors
    existing_user_sensors = {}


    connected_users_data = await cloudflare_api.get_data()
    connected_users = [item for item in connected_users_data if item.get('allowed')]
    
    for user in connected_users:
        user_email = user['user_email']
        if user_email in existing_user_sensors:
            # Update existing sensor
            existing_user_sensors[user_email].update_user_data(user)
        else:
            # Create new sensor
            user_sensor = CloudflareConnectedUserSensor(user, cloudflare_api)
            sensors.append(user_sensor)
            existing_user_sensors[user_email] = user_sensor
    
    async_add_entities(sensors, True)

class CloudflareAPI:
    def __init__(self, hass, api_key, email, account_id):
        self.hass = hass
        self.api_key = api_key
        self.email = email
        self.account_id = account_id
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/access/logs/access_requests"
        self.session = async_get_clientsession(hass)

    async def get_data(self):
        headers = {
            "X-Auth-Email": self.email,
            "X-Auth-Key": self.api_key,
            "Content-Type": "application/json"
        }
        async with self.session.get(self.base_url, headers=headers) as response:
            response.raise_for_status()
            data = await response.json()
            _LOGGER.debug("Cloudflare API response: %s", data)
            return data.get("result", [])

class CloudflareApplicationsAccessedSensor(Entity):
    def __init__(self, cloudflare_api):
        self._state = None
        self._attributes = {}
        self._cloudflare_api = cloudflare_api

    @property
    def name(self):
        return "Cloudflare Applications Accessed"

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes

    async def async_update(self):
        try:
            data = await self._cloudflare_api.get_data()
            applications_accessed = len(set(item['app_domain'] for item in data if item.get('allowed')))
            self._state = applications_accessed
            self._attributes = {"applications_accessed": applications_accessed}
        except Exception as e:
            _LOGGER.error("Error fetching data from Cloudflare: %s", e)
            self._state = None
            self._attributes = {}

class CloudflareFailedLoginsSensor(Entity):
    def __init__(self, cloudflare_api):
        self._state = None
        self._attributes = {}
        self._cloudflare_api = cloudflare_api

    @property
    def name(self):
        return "Cloudflare Failed Logins"

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes

    async def async_update(self):
        try:
            data = await self._cloudflare_api.get_data()
            failed_logins = len([item for item in data if not item.get('allowed')])
            self._state = failed_logins
            self._attributes = {"failed_logins": failed_logins}
        except Exception as e:
            _LOGGER.error("Error fetching data from Cloudflare: %s", e)
            self._state = None
            self._attributes = {}

class CloudflareConnectedUserSensor(Entity):
    def __init__(self, user_data, cloudflare_api):
        self._state = None
        self._attributes = {}
        self._user_data = user_data
        self._cloudflare_api = cloudflare_api

    @property
    def name(self):
        return f"Cloudflare Connected User {self._user_data['user_email']}"

    @property
    def state(self):
        return self._user_data['user_email']

    @property
    def extra_state_attributes(self):
        return self._attributes

    async def async_update(self):
        try:
            data = await self._cloudflare_api.get_data()
            user_data = next((item for item in data if item['user_email'] == self._user_data['user_email'] and item.get('allowed')), None)
            if user_data:
                self.update_user_data(user_data)
        except Exception as e:
            _LOGGER.error("Error updating user sensor: %s", e)
            self._attributes = {}

    def update_user_data(self, new_data):
        self._user_data = new_data
        self._attributes = {
            "user_email": new_data.get("user_email"),
            "app_domain": new_data.get("app_domain"),
            "connection": new_data.get("connection"),
            "ip_address": new_data.get("ip_address"),
            "created_at": new_data.get("created_at"),
            "ray_id": new_data.get("ray_id"),
            "country": new_data.get("country"),
            "action": new_data.get("action"),
        }
