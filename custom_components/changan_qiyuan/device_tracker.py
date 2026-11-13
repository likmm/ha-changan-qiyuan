from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.components.device_tracker import SourceType
from .entity import VehicleEntity
from .coordinator import location_coordinates, fresh

async def async_setup_entry(hass, entry, async_add_entities):
    if entry.options.get("gps", entry.data.get("gps", False)):
        async_add_entities([VehicleTracker(entry.runtime_data, "position")])

class VehicleTracker(VehicleEntity, TrackerEntity):
    _attr_name = "车辆位置"
    _attr_source_type = SourceType.GPS

    @property
    def coordinates(self):
        return location_coordinates(self.coordinator.data["location"])

    @property
    def available(self):
        return super().available and self.coordinates is not None

    @property
    def latitude(self):
        return self.coordinates[0] if self.coordinates else None

    @property
    def longitude(self):
        return self.coordinates[1] if self.coordinates else None

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data["location"]
        return {"gps_time": data.get("gpsTime"), "stale": not fresh(data.get("gpsTime")),
                "location_status": self.coordinator.data.get("location_status", "unknown")}
