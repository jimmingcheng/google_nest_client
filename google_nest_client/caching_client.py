from google_nest_client.client import GoogleNestClient


class GoogleNestCachingClient(GoogleNestClient):
    def __init__(
        self,
        project_id,
        client_id,
        client_secret,
        refresh_token,
        device_cache,
        cache_writes_enabled=True,
    ):
        super().__init__(project_id, client_id, client_secret, refresh_token)
        self.device_cache = device_cache
        self.cache_writes_enabled = cache_writes_enabled

        if self.cache_writes_enabled:
            self.device_cache.clear()
            self.load_cache()

    def load_cache(self):
        for device in super().get_devices():
            self.device_cache.upsert_device(device)

    def update_from_event(self, event):
        if 'resourceUpdate' in event:
            self.device_cache.upsert_device(event['resourceUpdate'])

    def get_devices(self):
        return self.device_cache.get_devices()

    def get_device(self, device_id):
        return self.device_cache.get_device(device_id)
