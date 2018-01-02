from twisted.internet.protocol import Protocol, ReconnectingClientFactory
import misc
import server
import json

class ClientProtocol(Protocol):

    data = ''
    def __init__(self, factory):
        misc.commonInit(self, factory)

    def connectionMade(self):
        # reset factory
        self.factory.resetDelay()
        # make request
        self.transport.write(json.dumps(self.get(self.factory.index)))
        #manage logs and stats
        misc.commonConnectionMade(self)

    def dataReceived(self, data):
        # log state and data
        self.factory.logger.info('[protocol {}] received data: {}'.format(self.index, data))
        # handle response
        message = json.loads(data)
        handlers = {
            'pong': lambda x: self.handlePong(x),
            'got' : lambda x: self.handleGot(x),
            'error': lambda x: self.handleError(x),
            'done': lambda x: self.handleDone(x)
        }
        result = handlers.get(message['type'], lambda x:self.handleUnknown(x))(message)

    def handleDone(self, message):
        self.factory.logger.info('[protocol {}] got done message'.format(self.index))
        self.factory.gotDone()

    def handleError(self, message):
        self.factory.logger.info('[protocol {}] got error message {}'.format(self.index, json.dumps(message)))

    def handleUnknown(self, message):
        self.factory.logger.info('[protocol {}] got unknown message {}'.format(self.index, json.dumps(message)))

    def handleGot(self, message):
        #add data to packages
        #self.factory.packages[message['index']] = message['data']
        self.factory.logger.info('[protocol {}] got done'.format(self.index))
        self.packageReceived(message)

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

    def packageReceived(self, message):
        self.factory.package_finished(message)
        # log received data and state
        self.factory.logger.info('[protocol {}] package received'.format(self.index))

class MyClientFactory(ReconnectingClientFactory):

    def __init__(self, deferred, packages, index, gotDoneCallback):
        self.numProtocols = 0
        self.protocolIndex = 0
        self.deferred = deferred
        self.packages = packages
        self.index = index
        self.gotDoneCallback = gotDoneCallback
        misc.setupLogger(self, __name__)

    def gotDone():
        gotDoneCallback()


    def buildProtocol(self, addr):
        return ClientProtocol(self)

    def package_finished(self, message):
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.callback(message)

    def clientConnectionFailed(self, connector, reason):
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.errback(reason)
