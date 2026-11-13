import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import selector
from .api import API, ApiError, AuthError
from .const import DOMAIN

TOKEN = selector.TextSelector(selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD))

async def validate(hass, data):
    await API(async_get_clientsession(hass), data["car_id"], data["token"]).get()

class Flow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return Options()

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input:
            user_input = {**user_input, "car_id": user_input["car_id"].strip(), "token": user_input["token"].strip()}
            try:
                if not user_input["car_id"] or not user_input["token"]:
                    raise AuthError()
                await validate(self.hass, user_input)
                await self.async_set_unique_id(user_input["car_id"])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="长安启源 A05", data=user_input)
            except AuthError:
                errors["base"] = "invalid_auth"
            except ApiError:
                errors["base"] = "cannot_connect"
        return self.async_show_form(step_id="user", data_schema=vol.Schema({vol.Required("car_id"): str,
            vol.Required("token"): TOKEN, vol.Optional("gps", default=False): bool}), errors=errors)

    async def async_step_reauth(self, entry_data):
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        errors = {}
        if user_input:
            entry = self._get_reauth_entry()
            try:
                data = {**entry.data, "token": user_input["token"].strip()}
                await validate(self.hass, data)
                return self.async_update_reload_and_abort(entry, data_updates=data)
            except AuthError:
                errors["base"] = "invalid_auth"
            except ApiError:
                errors["base"] = "cannot_connect"
        return self.async_show_form(step_id="reauth_confirm", data_schema=vol.Schema({vol.Required("token"): TOKEN}), errors=errors)

class Options(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        errors = {}
        if user_input:
            token = user_input.pop("token", "").strip()
            if token:
                try:
                    data = {**self.config_entry.data, "token": token}
                    await validate(self.hass, data)
                    self.hass.config_entries.async_update_entry(self.config_entry, data=data)
                except AuthError:
                    errors["base"] = "invalid_auth"
                except ApiError:
                    errors["base"] = "cannot_connect"
            if not errors:
                return self.async_create_entry(title="", data=user_input)
        o = self.config_entry.options
        return self.async_show_form(step_id="init", data_schema=vol.Schema({
            vol.Optional("token"): TOKEN,
            vol.Required("interval", default=o.get("interval", 10)): vol.All(vol.Coerce(int), vol.Range(min=5, max=1440)),
            vol.Required("gps", default=o.get("gps", self.config_entry.data.get("gps", False))): bool,
            vol.Required("pressure_unit", default=o.get("pressure_unit", "raw")): vol.In(["raw", "bar", "kPa", "psi"]),
            vol.Required("pressure_scale", default=o.get("pressure_scale", 1.0)): vol.All(vol.Coerce(float), vol.Range(min=.0001, max=1000)),
        }), errors=errors)
