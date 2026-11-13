from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import logging
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryAuthFailed
from .api import ApiError, AuthError

def timestamp(value):
    try:
        parsed = datetime.fromisoformat(value)
        return parsed.replace(tzinfo=ZoneInfo("Asia/Shanghai")) if parsed.tzinfo is None else parsed
    except (TypeError, ValueError):
        return None

def fresh(value):
    parsed = timestamp(value)
    return parsed is not None and -300 <= (datetime.now(parsed.tzinfo)-parsed).total_seconds() <= 1800

class Coordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry, api):
        super().__init__(hass, logging.getLogger(__name__), name="Changan Qiyuan",
            config_entry=entry, update_interval=timedelta(minutes=max(5, entry.options.get("interval", 10))))
        self.api, self.entry = api, entry

    async def _async_update_data(self):
        try:
            condition = await self.api.get()
            location = {}
            if self.entry.options.get("gps", self.entry.data.get("gps", False)):
                try:
                    location = await self.api.get(True)
                except AuthError:
                    raise
                except ApiError:
                    pass
            return {"condition": condition, "location": location}
        except AuthError:
            raise ConfigEntryAuthFailed("Update credentials") from None
        except ApiError:
            raise UpdateFailed("Vehicle request failed") from None
