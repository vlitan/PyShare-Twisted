from twisted.internet.protocol import Protocol
from twisted.internet.protocol import Factory
import logging
import misc
import json

class ServerProtocol(Protocol):
    def __init__(self, factory):
        misc.commonInit(self, factory)

    def connectionMade(self):
        self.factory.servers.append(self)
        print self.factory.servers
        misc.commonConnectionMade(self)

    def connectionLost(self, reason):
        misc.commonConnectionLost(self, reason)
        self.factory.servers.remove(self)

    def dataReceived(self, data):
        # log state and data
        self.factory.logger.info('[protocol {}] received data: {}'.format(self.index, data))
        # handle request and respond
        message = json.loads(data)
        handlers = {
            'ping': lambda x: self.handlePing(x),
            'get' : lambda x: self.handleGet(x),
            'done': lambda x: self.handleDone(x)
        }
        result = handlers.get(message['type'], lambda x:self.handleUnknown(x))(message)
        self.transport.write(json.dumps(result))

    #TODO all server handlers should return JSONs
    def handleDone(self, message):
        self.factory.logger.info('[protocol {}] got done message'.format(self.index))
        result = {}
        result['type'] = "ok"
        return result

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

    def sendDone(self):
        self.factory.logger.info('[protocol {}] sending DONE'.format(self.index))
        result = {}
        result['type'] = "done"
        self.transport.write(json.dumps(result))

class ServerFactory(Factory):

    def __init__(self, packages = None):
        self.numProtocols = 0
        self.protocolIndex = 0
        self.packages = packages
        self.servers = []
        misc.setupLogger(self, __name__)

    def buildProtocol(self, addr):
        return ServerProtocol(self)

    def broadcastDone(self):
        print 'start to broadcast'
        print self.servers
        for protocol in self.servers:
            print 'broadcast o'
            protocol.sendDone()
