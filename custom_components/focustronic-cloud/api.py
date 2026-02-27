import aiohttp

from .binary_sensor import *
from .sensor import *
from .switch import *

_LOGGER = logging.getLogger(__name__)

cloudUrl = "https://alkatronic.focustronic.com/api/v2"


class BaseApi:

    def __init__(self, token):
        self.token = token

    async def get(self, url, data=None):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f'{cloudUrl}{url}',
                    data=data,
                    headers={
                        "Content-Type": "application/json",
                        "x-session-token": self.token
                    }
            ) as response:
                response.raise_for_status()
                data = await response.json()
                if not data["result"]:
                    raise Exception(f'Got false result on url {url}: {data["message"]}')
                return data

    async def put(self, url, data):
        async with aiohttp.ClientSession() as session:
            async with session.put(
                    f'{cloudUrl}{url}',
                    json=data,
                    headers={
                        "Content-Type": "application/json",
                        "x-session-token": self.token
                    }
            ) as response:
                response.raise_for_status()
                data = await response.json()
                if not data["result"]:
                    raise Exception(f'Got false result on url {url}: {data["message"]}')
                return data

    async def post(self, url, data):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f'{cloudUrl}{url}',
                    json=data,
                    headers={
                        "Content-Type": "application/json",
                        "x-session-token": self.token
                    }
            ) as response:
                response.raise_for_status()
                data = await response.json()
                if not data["result"]:
                    raise Exception(f'Got false result on url {url}: {data["message"]}')
                return data


async def login(email, password):
    async with aiohttp.ClientSession() as session:
        async with session.post(
                f'{cloudUrl}/auth/login',
                headers={
                    "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
                },
                data={
                    "email": email,
                    "password": password,
                    "platform": "focustronic-ios",
                },
        ) as response:
            response.raise_for_status()
            data = await response.json()
            if not isinstance(data.get("data"), dict):
                _LOGGER.error(f"Unexpected response: {data}")
                raise Exception(f"Unexpected response: {data}")
            if not data["result"]:
                raise Exception(f'Got false result on url /auth/login')
            return data["data"]["session_token"], data["data"]["user_hash"]


class FocustronicApi(BaseApi):

    def __init__(self, token):
        super().__init__(token)
        self.factories = {}
        self.entities = []

    def get_factories(self, platform):
        return self.factories.get(platform, [])

    def add_entities(self, entities):
        return self.entities.extend(entities)

    def update(self, data):
        for entity in self.entities:
            entity.handle_api_data(data)

    async def getTank(self):
        return await self.get("/aquarium-tanks/0")


def Generate(iterable, func):
    """
    Generates a list of instances based on the iterable and the function provided.
    """
    return [func(i) for i in iterable]

class MastertronicApi:
    def __init__(self, api: FocustronicApi, device, id):
        self.id = id
        self.api = api
        self.device = device

        self.factories = {
            "binary_sensor": [
                MastertronicActiveSensor(self.device),
            ],
            "sensor": [
                MastertronicStatusSensor(self.device),
                MastertronicStatusTextSensor(self.device),
                MastertronicTestCountSensor(self.device),
                MastertronicHoseCountSensor(self.device),
                MastertronicNeedleCountSensor(self.device),
                MastertronicHoseCountLimitSensor(self.device),
                MastertronicNeedleCountLimitSensor(self.device),

                MastertroniParamValueSensor(self.device, "ca", "mg/L"),
                MastertroniParamValueSensor(self.device, "mg", "mg/L"),
                MastertroniParamValueSensor(self.device, "po", "mg/L"),
                MastertroniParamValueSensor(self.device, "ni", "mg/L"),
                MastertroniParamValueSensor(self.device, "nit", "mg/L"),
                MastertroniParamValueSensor(self.device, "oli", "u"),
                MastertroniParamValueSensor(self.device, "kh", "dKH"),
                MastertroniParamValueSensor(self.device, "i", "mg/L"),
                MastertroniParamValueSensor(self.device, "amm", "mg/L"),

                *Generate(range(1, 13), lambda i: MastertroniVialReagentSensor(self.device, i)),
                *Generate(range(1, 13), lambda i: MastertroniVialVolumeSensor(self.device, i)),
            ],
            "switch": [
            ],
            "number": [
            ]
        }

    async def update(self):
        data = await self.api.get(f'/devices/mastertronic/{self.id}')
        param_data = await self.api.get(f'/devices/mastertronic/{self.id}/parameter-information')
        data["data"]["parameter-information"] = param_data["data"]
        self.api.update(data["data"])

class AlkatronicApi:
    def __init__(self, api: FocustronicApi, device, id):
        self.id = id
        self.api = api
        self.device = device

        self.factories = {
            "binary_sensor": [
                MastertronicActiveSensor(self.device),
            ],
            "sensor": [
                MastertronicStatusSensor(self.device),
                MastertronicStatusTextSensor(self.device),
                MastertronicTestCountSensor(self.device),

                MastertroniParamValueSensor(self.device, "kh", "dKH"),
                MastertroniParamValueSensor(self.device, "ph", ""),
                MastertroniParamValueSensor(self.device, "th", "°C"),
            ],
            "switch": [
            ],
            "number": [
            ]
        }

    async def update(self):
        data = await self.api.get(f'/devices/alkatronic/{self.id}')
        param_data = await self.api.get(f'/devices/alkatronic/{self.id}/parameter-information')
        data["data"]["parameter-information"] = param_data["data"]
        self.api.update(data["data"])
