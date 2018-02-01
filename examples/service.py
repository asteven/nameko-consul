import time
import logging

from nameko.web.handlers import http
from nameko.timer import timer

from nameko_consul.dependencies import Consul
from nameko_consul.entrypoints import watch


class ExampleService(object):
    name = 'example'
    consul = Consul()


    #@timer(interval=2)
    #def get_count(self):
    #    print('timer: ' + str(self.consul.kv.get('count')))

    @http('GET', '/')
    def hello_world(self, request):
        return 'hello world\n'

    @http('GET', '/reset-count')
    def reset_count(self, request):
        self.consul.kv.put('count', '0')
        return 'reset count to: 0\n'

    @http('GET', '/increment-count')
    def increment_count(self, request):
        index, data = self.consul.kv.get('count')
        print('index: %s; data: %s' % (index, data))
        if data:
            count = int(data['Value'])
        else:
            index = 0
            count = 0
        new_count = str(count+1)
        self.consul.kv.put('count', new_count, cas=index)
        return 'count is now: %s\n' % new_count

    @watch.key('count')
    def handle_count(self, *args, **kwargs):
        print('handle_count: %s; %s' % (args, kwargs))

    @watch.event('fire')
    def handle_fire(self, *args, **kwargs):
        print('handle_fire: %s; %s' % (args, kwargs))
