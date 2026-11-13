import importlib.util
from pathlib import Path
import aiohttp
import pytest
from aioresponses import aioresponses

ROOT = Path(__file__).resolve().parents[1] / "custom_components/changan_qiyuan"
def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
api = load("api")
geo = load("geo")

def test_coordinates():
    assert geo.to_wgs84(0, 0) == (0, 0)
    lat, lon = 31.0, 121.0  # Synthetic test point, not a vehicle location.
    dx, dy = geo._offset(lon, lat)
    result = geo.to_wgs84(lat + dy, lon + dx)
    assert result == pytest.approx((lat, lon), abs=1e-7)
    assert geo.to_wgs84(39.9102265, 116.4037136) == pytest.approx((39.908823, 116.39747), abs=2e-5)

@pytest.mark.asyncio
async def test_api():
    import re
    async with aiohttp.ClientSession() as session:
        client = api.API(session, "synthetic-car", "synthetic-token")
        with aioresponses() as mock:
            mock.get(re.compile(".*get-car-condition-map.*"), payload={"code":0,"success":True,"data":{"soc":78}})
            assert await client.get() == {"soc":78}
        with aioresponses() as mock:
            mock.get(re.compile(".*get-car-condition-map.*"), status=401)
            with pytest.raises(api.AuthError):
                await client.get()
        with pytest.raises(api.AuthError):
            await client.get()

@pytest.mark.asyncio
@pytest.mark.parametrize("payload", [{}, [], {"code":0,"success":True,"data":None}, {"code":9,"success":False}])
async def test_bad_payload(payload):
    import re
    with aioresponses() as mock:
      async with aiohttp.ClientSession() as session:
        mock.get(re.compile(".*get-car-condition-map.*"), payload=payload)
        with pytest.raises(api.ApiError):
            await api.API(session,"fake","fake").get()

