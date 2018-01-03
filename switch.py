LISTEN_PORT = 8000
import json
from twisted.internet import protocol, reactor


# Adapted from http://stackoverflow.com/a/15645169/221061
class ServerProtocol(protocol.Protocol):
    def __init__(self):
        self.buffer = None
        self.client = None

    def connectionMade(self):
        self.factory = protocol.ClientFactory()
        self.factory.protocol = ClientProtocol
        self.factory.server = self

    #    reactor.connectTCP(SERVER_ADDR, SERVER_PORT, factory)

    # Client => Proxy
    def dataReceived(self, data):
        print "Client => Proxy %s" % (data)
        message = json.loads('{' + data.rsplit('{', 1)[1])
        addr, port = message['address'].split(':')
        del message['address']
        reactor.connectTCP(addr, int(port), self.factory)
        if self.client:
            self.client.write(json.dumps(message))
        else:
            self.buffer = data

    # Proxy => Client
    def write(self, data):
        print "Proxy => Client %s" % (data)
        self.transport.write(data)


class ClientProtocol(protocol.Protocol):
    def connectionMade(self):
        self.factory.server.client = self
        self.write(self.factory.server.buffer)
        self.factory.server.buffer = ''

    # Server => Proxy
    def dataReceived(self, data):
        print "Server => Proxy %s" % (data)
        self.factory.server.write(data)

    # Proxy => Server
    def write(self, data):

        if data:
            print "Proxy => Server %s" % (data)
            self.transport.write(data)



def main():
    factory = protocol.ServerFactory()
    factory.protocol = ServerProtocol

    reactor.listenTCP(LISTEN_PORT, factory)
    reactor.run()


if __name__ == '__main__':
    main()
