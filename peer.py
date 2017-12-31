from twisted.internet.protocol import Protocol
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ClientEndpoint, TCP4ServerEndpoint, connectProtocol
from twisted.internet import reactor
from twisted.internet import defer
from twisted.internet.protocol import Protocol, ClientFactory
from sys import stdout
import misc
import server
import client
# class Echo(Protocol):
#     def dataReceived(self, data):
#         stdout.write(data)
#
#     def sendMessage(self, msg):
#         self.transport.write("MESSAGE %s" % msg)


def get_package(host, port):
    """
    Download a poem from the given host and port. This function
    returns a Deferred which will be fired with the complete text of
    the poem or a Failure if the poem could not be downloaded.
    """
    d = defer.Deferred()
    from twisted.internet import reactor
    factory = server.ServerFactory(d)
    reactor.connectTCP(host, port, factory)
    return d

# def gotProtocol(p):
#     # p.sendMessage("Hello")
#     reactor.callLater(1, p.sendMessage, "This is sent in a second")
#     reactor.callLater(2, p.transport.loseConnection)


def peer_main():
    options = misc.parse_args()
    packages = ["a", "b", None, "d"]
    #
    # point = TCP4ClientEndpoint(reactor, "localhost",  options.client_port)
    # d = connectProtocol(point, Echo())
    # d.addCallbacks(gotProtocol, handleClientError)

    def package_failed(err):
        print >>sys.stderr, 'Poem failed:', err

    def got_package(package):
        packages.append(package)
        print 'got packages'

    d = defer.Deferred()
    from twisted.internet import reactor
    factory = client.MyClientFactory(d, packages)
    reactor.connectTCP('localhost', options.client_port, factory)

    d.addCallbacks(got_package, package_failed)

    endpoint = TCP4ServerEndpoint(reactor, options.server_port)
    endpoint.listen(server.ServerFactory(packages))
    from time import sleep
    #sleep(3)
    reactor.run()

if __name__ == '__main__':
    peer_main()
