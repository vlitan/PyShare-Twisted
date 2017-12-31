from twisted.internet.protocol import Protocol
from twisted.internet.protocol import Factory
import logging
import misc
import json

class ServerProtocol(Protocol):
    def __init__(self, factory):
        misc.commonInit(self, factory)

    def connectionMade(self):
        misc.commonConnectionMade(self)

    def connectionLost(self, reason):
        misc.commonConnectionLost(self, reason)

    def dataReceived(self, data):
        # log state and data
        self.factory.logger.info('[protocol {}] received data: {}'.format(self.index, data))
        # handle request and respond
        message = json.loads(data)
        handlers = {
            'ping': lambda x: self.handlePing(x),
            'get' : lambda x: self.handleGet(x)
        }
        result = handlers.get(message['type'], lambda x:self.handleUnknown(x))(message)
        self.transport.write(json.dumps(result))
    #TODO all server handlers should return JSONs
    def handleUnknown(self, message):
        self.factory.logger.info('[protocol {}] got unknown message type'.format(self.index))
        result = {}
        result['type'] = "error"
        result['error'] = "unknown type"
        return result

    def handlePing(self, message):
        self.factory.logger.info('[protocol {}] got pinged, return pong'.format(self.index))
        result = {}
        result['type'] = "pong"
        return result

    def handleGet(self, message):
        self.factory.logger.info('[protocol {}] got get-request package index is {}'.format(self.index, message['index']))
        result = {}
        result['type'] = "got"
        result['index'] = message['index']
        result['data'] =  self.factory.packages[result['index']]
        return result

class ServerFactory(Factory):

    def __init__(self, packages = None):
        self.numProtocols = 0
        self.protocolIndex = 0
        self.packages = packages
        misc.setupLogger(self, __name__)

    def buildProtocol(self, addr):
        return ServerProtocol(self)
