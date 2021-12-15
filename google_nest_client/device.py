class Device:
    def __init__(self, api_client, device_dict):
        self.api_client = api_client
        self.device_dict = device_dict
        self.device_id = get_device_id(device_dict)

    def label(self):
        return get_device_label(self.device_dict)

    def get_trait(self, trait):
        return self.device_dict['traits']['sdm.devices.traits.' + trait]

    def get_event(self, trait):
        return self.device_dict['traits']['sdm.devices.events.' + trait]


def get_device_id(device_dict):
    return device_dict['name'].split('/')[-1]


def get_device_label(device_dict):
    label = device_dict.get('traits', {}).get('sdm.devices.traits.Info', {}).get('customName')
    if label:
        return label

    return device_dict.get('parentRelations', {})[0].get('displayName')
