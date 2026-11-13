import math
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from .entity import VehicleEntity
from .coordinator import timestamp

FIELDS = [("soc", "电池电量", "%", "battery"), ("remainedPowerMile", "纯电续航", "km", "distance"),
    ("remainedOilMile", "燃油续航", "km", "distance"), ("totalOdometer", "总里程", "km", "distance"),
    ("lfTyrePressure", "左前胎压", None, None), ("rfTyrePressure", "右前胎压", None, None),
    ("lrTyrePressure", "左后胎压", None, None), ("rrTyrePressure", "右后胎压", None, None),
    ("environmentalTemp", "车外温度", "°C", "temperature"), ("driving", "行驶状态", None, None)]
GPS = [("city", "所在城市", None, None), ("address", "车辆地址", None, None), ("gpsTime", "定位时间", None, "timestamp")]

async def async_setup_entry(hass, entry, async_add_entities):
    c = entry.runtime_data
    fields = FIELDS + GPS if entry.options.get("gps", entry.data.get("gps", False)) else FIELDS
    async_add_entities(VehicleSensor(c, *field) for field in fields)

class VehicleSensor(VehicleEntity, SensorEntity):
    def __init__(self, c, key, name, unit, device_class):
        super().__init__(c, key)
        self.key = key
        self._attr_name = name
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        if "Tyre" in key:
            self._attr_native_unit_of_measurement = c.entry.options.get("pressure_unit", "raw")
            if self._attr_native_unit_of_measurement == "raw":
                self._attr_native_unit_of_measurement = None
            else:
                self._attr_device_class = SensorDeviceClass.PRESSURE
        if unit and key != "gpsTime":
            self._attr_state_class = SensorStateClass.TOTAL_INCREASING if key == "totalOdometer" else SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        if self.key == "driving":
            return "未知"
        source = "location" if self.key in ("city", "address", "gpsTime") else "condition"
        value = self.coordinator.data[source].get(self.key)
        if self.key == "gpsTime":
            return timestamp(value)
        if source == "location":
            return str(value)[:255] if value is not None else None
        try:
            number = float(value)
            if not math.isfinite(number):
                return None
            return number * self.coordinator.entry.options.get("pressure_scale", 1) if "Tyre" in self.key else number
        except (TypeError, ValueError):
            return None

    @property
    def available(self):
        return super().available and self.native_value is not None

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data["condition"]
        if self.key == "driving":
            return {k: data.get(k) for k in ("carStatus", "status", "vehicleSpeed", "lastUpdatedTime")}
        return {"vehicle_updated_at": data.get("lastUpdatedTime")}
