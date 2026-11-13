from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.components.device_tracker import SourceType
from .entity import VehicleEntity
from .coordinator import fresh
from .geo import to_wgs84

async def async_setup_entry(hass, entry, async_add_entities):
    if entry.options.get("gps", entry.data.get("gps", False)):
        async_add_entities([VehicleTracker(entry.runtime_data, "position")])

class VehicleTracker(VehicleEntity, TrackerEntity):
    _attr_name = "车辆位置"
    _attr_source_type = SourceType.GPS

    @property
    def coordinates(self):
        d = self.coordinator.data["location"]
        if d.get("validGps") is not True or not fresh(d.get("gpsTime")):
            return None
        try:
            lat, lon = float(d["lat"]), float(d["lng"])
            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                return None
            return to_wgs84(lat, lon)
        except (KeyError, TypeError, ValueError):
            return None

    @property
    def available(self):
        return super().available and self.coordinates is not None

    @property
    def latitude(self):
        return self.coordinates[0] if self.coordinates else None

    @property
    def longitude(self):
        return self.coordinates[1] if self.coordinates else None
