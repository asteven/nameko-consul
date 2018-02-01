from nameko.extensions import Entrypoint

import consul

from . import constants
from . import client


class ConsulWatchEntrypoint(Entrypoint):
    """See
    https://www.consul.io/docs/agent/watches.html
    https://www.consul.io/docs/commands/watch.html
    """

    def setup(self):
        self.consul = client.get_client(self.container.config.get(constants.CONFIG_KEY, None))

    def start(self):
        self.container.spawn_managed_thread(
            self.run, identifier='ConsulWatch{0}EntryPoint.run'.format(self.__class__.__name__)
        )

    def run(self):
        # get initial index
        index, data = self.poll()
        while True:
            index, data = self.poll(index)
            self.handle_watch(data)

    def handle_watch(self, *args, **kwargs):
        context_data = {}
        self.container.spawn_worker(
            self, args, kwargs, context_data=context_data
        )


class Key(ConsulWatchEntrypoint):
    _type = 'key'

    def __init__(self, key, **kwargs):
        self.key = key
        self.kwargs = kwargs
        super().__init__(**kwargs)

    def poll(self, index=None):
        # get(key, index=None, recurse=False, wait=None, token=None, consistency=None, keys=False, separator=None, dc=None
        return self.consul.kv.get(self.key, index=index, **self.kwargs)


class KeyPrefix(ConsulWatchEntrypoint):
    _type = 'keyprefix'

    def __init__(self, prefix, **kwargs):
        self.prefix = prefix
        self.kwargs = kwargs
        super().__init__(**kwargs)

    def poll(self, index=None):
        # get(key, index=None, recurse=False, wait=None, token=None, consistency=None, keys=False, separator=None, dc=None)
        return self.consul.kv.get(self.prefix, index=index, recurse=True, **self.kwargs)


class Services(ConsulWatchEntrypoint):
    _type = 'services'

    def poll(self, index=None):
        #  services(index=None, wait=None, consistency=None, dc=None, token=None)¶
        return self.consul.services(index=index, **self.kwargs)


class Nodes(ConsulWatchEntrypoint):
    _type = 'nodes'

    def poll(self, index=None):
        # nodes(index=None, wait=None, consistency=None, dc=None, near=None, token=None)
        return self.consul.nodes(index=index, **self.kwargs)


class Service(ConsulWatchEntrypoint):
    _type = 'service'

    def __init__(self, service, **kwargs):
        self.service = service
        self.kwargs = kwargs
        super().__init__(**kwargs)

    def poll(self, index=None):
        # service(service, index=None, wait=None, passing=None, tag=None, dc=None, near=None, token=None)
        return self.consul.health.service(self.service, index=index, **self.kwargs)


class Checks(ConsulWatchEntrypoint):
    _type = 'checks'

    def __init__(self, service=None, state=None, **kwargs):
        self.service = service
        self.state = state
        self.kwargs = kwargs
        super().__init__(**kwargs)

    def poll(self, index=None):
        #  checks(service, index=None, wait=None, dc=None, near=None, token=None)
        return self.consul.health.checks(self.service, index=index)
        # or
        # state(name, index=None, wait=None, dc=None, near=None, token=None)
        #return self.consul.health.state(self.state, index=index)


class Node(ConsulWatchEntrypoint):
    _type = 'node'

    def __init__(self, node, **kwargs):
        self.node = node
        self.kwargs = kwargs
        super().__init__(**kwargs)

    def poll(self, index=None):
        # node(node, index=None, wait=None, dc=None, token=None)
        return self.consul.health.node(self.node, index=index)


class Event(ConsulWatchEntrypoint):
    # TODO: may need to implement something like sifter to filter duplicate events.
    #   https://github.com/darron/sifter/
    _type = 'event'

    def __init__(self, event, **kwargs):
        self.event = event
        self.kwargs = kwargs
        super().__init__(**kwargs)

    def poll(self, index=None):
        #  list(name=None, index=None, wait=None)
        return self.consul.event.list(self.event, index=index)


class ConsulWatchEntrypointFactory():
    def __getattribute__(self, _type):
        for watch in ConsulWatchEntrypoint.__subclasses__():
            if watch._type == _type:
                return watch.decorator
        raise AttributeError('Unknown watch type: %s' % _type)


watch = ConsulWatchEntrypointFactory()

