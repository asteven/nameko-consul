import logging

from six.moves import urllib

from nameko.extensions import DependencyProvider

import consul

from . import constants
from . import client


class ConsulConnectionError(Exception):
    pass


class Consul(DependencyProvider):

    def setup(self):
        self.consul = client.get_client(self.container.config.get(constants.CONFIG_KEY, None))

    def stop(self):
        del self.consul

    def get_dependency(self, worker_ctx):
        # trigger an exception if we can't interact with consul
        try:
            self.consul.agent.self()
        except OSError as e:
            error_message = 'Failed to connect to consul.'
            logging.error(error_message)
            raise ConsulConnectionError(error_message) from e
        return self.consul

