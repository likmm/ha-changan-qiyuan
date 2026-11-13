from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import logging
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryAuthFailed
from .api import ApiError, AuthError
from .geo import to_wgs84

def timestamp(value):
    try:
        parsed = datetime.fromisoformat(value)
        return parsed.replace(tzinfo=ZoneInfo("Asia/Shanghai")) if parsed.tzinfo is None else parsed
    except (TypeError, ValueError):
        return None

def fresh(value):
    parsed = timestamp(value)
    return parsed is not None and -300 <= (datetime.now(parsed.tzinfo)-parsed).total_seconds() <= 1800

def location_coordinates(data):
    """Return the last valid WGS84 fix, regardless of its age."""
    if data.get("validGps") is not True:
        return None
    try:
        lat, lon = float(data["lat"]), float(data["lng"])
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            return None
        return to_wgs84(lat, lon)
    except (KeyError, TypeError, ValueError):
        return None

class Coordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry, api):
        super().__init__(hass, logging.getLogger(__name__), name="Changan Qiyuan",
            config_entry=entry, update_interval=timedelta(minutes=max(5, entry.options.get("interval", 10))))
        self.api, self.entry = api, entry

    async def _async_update_data(self):
        try:
            condition = await self.api.get()
            location = {}
            location_status = "disabled"
            if self.entry.options.get("gps", self.entry.data.get("gps", False)):
                try:
                    location = await self.api.get(True)
                    location_status = "received"
                except AuthError:
                    raise
                except ApiError:
                    location_status = "request_failed"
            if location_status != "disabled" and location_coordinates(location) is None:
                previous = (self.data or {}).get("location", {})
                if location_coordinates(previous) is not None:
                    location = previous
                    location_status = "last_valid_fix"
            return {"condition": condition, "location": location, "location_status": location_status}
        except AuthError:
            raise ConfigEntryAuthFailed("Update credentials") from None
        except ApiError:
            raise UpdateFailed("Vehicle request failed") from None
