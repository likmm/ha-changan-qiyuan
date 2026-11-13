"""Read-only API. Never log responses or credential-bearing URLs."""
import asyncio
import aiohttp

class ApiError(Exception):
    """Sanitized request failure."""

class AuthError(ApiError):
    """Credentials rejected."""

class API:
    def __init__(self, session, car_id, token):
        self.session, self.car_id, self.token = session, car_id, token
        self.invalid = False

    async def get(self, location=False):
        if self.invalid:
            raise AuthError("Authentication required")
        params = {"carId": self.car_id, "token": self.token}
        params.update({"mapType": "GCJ02"} if location else {"isNev": "0"})
        endpoint = "location" if location else "get-car-condition-map"
        try:
            async with self.session.get(
                "https://m.iov.changan.com.cn/app2/api/car/" + endpoint,
                params=params, headers={"vcs-app-id": "inCall", "Accept": "*/*" if location else "application/json",
                "User-Agent": "OuShangStyle/812 CFNetwork/3896.100.1.2.1 Darwin/27.0.0"},
                timeout=aiohttp.ClientTimeout(total=30), raise_for_status=False,
            ) as response:
                if response.status in (401, 403):
                    self.invalid = True
                    raise AuthError("Authentication required")
                if response.status != 200:
                    raise ApiError("Server request failed")
                result = await response.json(content_type=None)
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError):
            raise ApiError("Connection or response failure") from None
        if not isinstance(result, dict):
            raise ApiError("Invalid response")
        if result.get("code") != 0 or result.get("success") is not True:
            # Only known HTTP-style codes or explicit authentication messages.
            message = str(result.get("msg", "")).lower()
            if str(result.get("code")) in ("401", "403") or any(x in message for x in
                    ("token", "登录", "认证", "未授权")):
                self.invalid = True
                raise AuthError("Authentication required")
            raise ApiError("API rejected request")
        if not isinstance(result.get("data"), dict):
            raise ApiError("Missing vehicle data")
        return result["data"]
