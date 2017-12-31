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


def get_package(network, index):

    defers = []
    from random import shuffle
    shuffle(network)
    for address in network:
        host, port = address.split(':')
        if port != options.server_port: #TODO replace port with host when running in cloud
            d = defer.Deferred()
            factory = client.MyClientFactory(d, packages, index) # todo add index
            reactor.connectTCP(host, int(port), factory)
            defers.append(d)
    return defers


def peer_main():
    global options
    options = misc.parse_args()
    global packages
    packages = open(options.data_file, 'r').read().split(',')
    packages.remove('\n')
    [None if v is '' else v for v in packages]
    packages.append(None)
    print packages
    defers = []
    NETWORK = [ "localhost:5999"
                ,"localhost:5998"
                ,"localhost:5997" ]
    #
    # point = TCP4ClientEndpoint(reactor, "localhost",  options.client_port)
    # d = connectProtocol(point, Echo())
    # d.addCallbacks(gotProtocol, handleClientError)

    def package_failed(err):
        print >>sys.stderr, 'Poem failed:', err

    def got_package(message):
        packages[message['index']] = message['data']
        if None not in packages:
            print "i`m done"
            serverFactory.broadcastDone()
        print 'got packages'

    serverFactory = server.ServerFactory(packages);
    for i in range(len(packages)):
        if packages[i] is None:
            defers.extend(get_package(NETWORK, i))

    for d in defers:
        d.addCallbacks(got_package, package_failed)


    endpoint = TCP4ServerEndpoint(reactor, options.server_port)
    endpoint.listen(serverFactory)

    from time import sleep
    sleep(5)

    reactor.run()

if __name__ == '__main__':
    peer_main()
