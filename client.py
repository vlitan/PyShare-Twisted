from twisted.internet.protocol import Protocol, ClientFactory
import misc
import server
import json

class ClientProtocol(Protocol):

    data = ''
    def __init__(self, factory):
        misc.commonInit(self, factory)

    def connectionMade(self):
        # make request
        self.transport.write(json.dumps(self.get(1)))
        #manage logs and stats
        misc.commonConnectionMade(self)

    def dataReceived(self, data):
        # log state and data
        self.factory.logger.info('[protocol {}] received data: {}'.format(self.index, data))
        # handle response
        message = json.loads(data)
        handlers = {
            'pong': lambda x: self.handlePong(x),
            'got' : lambda x: self.handleGot(x)
        }
        result = handlers.get(message['type'], lambda x:self.handleUnknown(x))(message)

    def handleUnknown(self, message):
        self.factory.logger.info('[protocol {}] got unknown message {}'.format(self.index, json.dumps(message)))

    def handleGot(self, message):
        #add data to packages
        self.factory.packages[message['index']] = message['data']
        self.factory.logger.info('[protocol {}] got package {} -> {}'.format(self.index, message['index'], message['data']))

    def handlePong(self, message):
        self.factory.logger.info('[protocol {}] got ponged'.format(self.index))

    def ping(self):
        request = {}
        request['type'] = "ping"
        return request

    def get(self, index):
    #    if (self.factory.packages[index] is None):
        request = {}
        request['type'] = "get"
        request['index'] = index
        return request


    def connectionLost(self, reason):
        self.packageReceived(self.data)
        misc.commonConnectionLost(self, reason)

    def packageReceived(self, data):
        self.factory.package_finished(data)
        # log received data and state
        self.factory.logger.info('[protocol {}] package received {}'.format(self.index, data))

class MyClientFactory(ClientFactory):

    def __init__(self, deferred, packages):
        self.numProtocols = 0
        self.protocolIndex = 0
        self.deferred = deferred
        self.packages = packages
        misc.setupLogger(self, __name__)

    def buildProtocol(self, addr):
        return ClientProtocol(self)

    def package_finished(self, data):
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.callback(data)

    def clientConnectionFailed(self, connector, reason):
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.errback(reason)