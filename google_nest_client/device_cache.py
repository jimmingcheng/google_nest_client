import time
from google_nest_client.device import get_device_id


class DeviceCache:
    def clear(self):
        raise NotImplementedError

    def upsert_device(device_update):
        raise NotImplementedError

    def get_devices(self):
        raise NotImplementedError

    def get_device(self):
        raise NotImplementedError


class InMemoryDeviceCache(DeviceCache):
    def __init__(self):
        self.id_to_device = {}

    def clear(self):
        self.id_to_device = {}

    def upsert_device(self, device_update):
        device_id = get_device_id(device_update)
        device = self.id_to_device.get(device_id)

        if not device:
            self.id_to_device[device_id] = device_update
            return

        if 'traits' in device_update:
            for k, v in device_update['traits']:
                device['traits'][k] = v

        if 'events' in device_update:
            for k, v in device_update['events']:
                device['events'][k] = v
                device['events'][k]['timestamp'] = int(time.time())

    def get_devices(self):
        return self.id_to_device.values()

    def get_device(self, device_id):
        return self.id_to_device[device_id]
