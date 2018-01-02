from twisted.internet.protocol import Protocol
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ClientEndpoint, TCP4ServerEndpoint, connectProtocol
from twisted.internet import reactor
from twisted.internet import defer
from twisted.internet.protocol import Protocol, ClientFactory
from sys import stdout
import misc
import server
import socket
import client


def get_package(network, index):

    defers = []
    from random import shuffle
    shuffle(network)
    for address in network:
        host, port = address.split(':')
        #if port != options.server_port: #TODO replace port with host when running in cloud

        if host != socket.gethostname():
            d = defer.Deferred()
            factory = client.MyClientFactory(d, packages, index) # todo add index
            reactor.connectTCP(host, int(port), factory)
            defers.append(d)
    return defers


def peer_main():
    global options
    global packages

    options = misc.parse_args()
    packages = open(options.data_file, 'r').read().split(',')
    packages = [s.rstrip() for s in packages]
    packages = map(lambda x: None if x == '' else x, packages)

    print packages
    defers = []
    NETWORK = [  "10.142.0.2:5002"
                ,"10.142.0.3:5003"
                ,"10.142.0.4:5004"]

    def package_failed(err):
        print >>sys.stderr, 'Poem failed:', err

    def got_package(message):
        if (message['data'] is not None):
            packages[message['index']] = message['data']
        if None not in packages:
            print "i`m done~~~~~~~~"
        print packages
        #    serverFactory.broadcastDone()
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
