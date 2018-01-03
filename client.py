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
        self.write(json.dumps(self.get(self.factory.index)))
        #self.write(json.dumps(self.ping()))
        #manage logs and stats
        misc.commonConnectionMade(self)

    def dataReceived(self, data):
        # log state and data
        self.factory.logger.info('[protocol {}] received data: {}'.format(self.index, data))
        # handle response
        message = json.loads('{' + data.rsplit('{', 1)[1]) #overcome non-flushing "stream"
        handlers = {
            'pong':  lambda x: self.handlePong(x),
            'got' :  lambda x: self.handleGot(x),
            'error': lambda x: self.handleError(x),
            'done':  lambda x: self.handleDone(x)
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
        # log
        self.factory.logger.info('[protocol {}] got done'.format(self.index))
        # callback
        self.packageReceived(message)

    def handlePong(self, message):
        self.factory.logger.info('[protocol {}] got ponged'.format(self.index))

    def ping(self):
        request = {}
        request['type'] = "ping"
        return request

    def get(self, index):
        #TODO actuallt use this condition and treat case
    #   if (self.factory.packages[index] is None):
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

    def write(self, message):
        msg = json.loads(message)
        msg['address'] = self.factory.address
        self.transport.write(json.dumps(msg))

class MyClientFactory(ReconnectingClientFactory):

    maxDelay = 10
    continueTrying = True

    def __init__(self, deferred, packages, index, address, gotDoneCallback = None):
        self.numProtocols = 0       # active number of protocols
        self.protocolIndex = 0      # current index for protocol
        self.deferred = deferred    # deferred
        self.packages = packages    # list of packages TODO remove this
        self.index = index          # index of desired package
        self.address = address      # address of other peer
        self.gotDoneCallback = gotDoneCallback # callback for done
        misc.setupLogger(self, __name__)

    def gotDone(self):
        self.gotDoneCallback()


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
