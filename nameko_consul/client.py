import consul

from . import CONFIG_KEY


config_defaults = {
    'scheme': 'http',
    'host': '127.0.0.1',
    'port': 8500,
    'token': None,
    'consistency': 'default',
    'dc': None,
    'verify': True,
}


def get_client(extra_config=None):
    config = config_defaults.copy()
    if extra_config:
        config.update(extra_config)
    return consul.Consul(**config)


def from_config(container_config):
    return get_client(container_config.get(CONFIG_KEY, None))
