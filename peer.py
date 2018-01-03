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


def peer_main():
    # TODO replace global with better and local use of variables ;)
    global options
    global packages
    global NETWORK
    global doneCount
    doneCount = 0

    def get_package(network, index):
        # done callback, called when a client receives a "done"
        def gotDone():
            global doneCount
            global packages
            doneCount += 1
            print doneCount
            if None not in packages and doneCount == len(NETWORK) - 1:
               print "all peers are done"
               from twisted.internet import reactor
               reator.stop()
               print packages
        defers = []
        # shuffle bootstrap
        from random import shuffle
        shuffle(network)
        for address in network:
            host, port = address.split(':')
        #    if port != options.server_port: #TODO replace port with host when running in cloud
            if host != socket.gethostname(): # if not connectig with self
                d = defer.Deferred()
                factory = client.MyClientFactory(d, packages, index, gotDone)
                reactor.connectTCP(host, int(port), factory)
                defers.append(d)
        return defers

    # parse cl options
    options = misc.parse_args()
    packages = open(options.data_file, 'r').read().split(',')  # open file and read contents
    packages = [s.rstrip() for s in packages]                  # remove trailing \n
    packages = map(lambda x: None if x == '' else x, packages) # replace empty with nones

    print packages  #print packages
    defers = []
    # read bootstraped network
    NETWORK = [  "10.142.0.2:5002"
                ,"10.142.0.3:5003"
                ,"10.142.0.4:5004"]

    # NETWORK = [  "localhost:5999"
    #             ,"localhost:5998"]

    # failure callback
    def package_failed(err):
        print >>sys.stderr, 'Poem failed:', err

    # succes callback
    def got_package(message):
        if (message['data'] is not None):
            packages[message['index']] = message['data']
        if None not in packages:
            print "i`m done~~~~~~~~"
            print packages
            serverFactory.broadcastDone()
        print 'got package'

    # create server factory
    serverFactory = server.ServerFactory(packages);
    # create client factories for each package
    for i in range(len(packages)):
        if packages[i] is None:
            defers.extend(get_package(NETWORK, i))

    # add callbacks to deffers
    for d in defers:
        d.addCallbacks(got_package, package_failed)

    # setup server endpoint
    endpoint = TCP4ServerEndpoint(reactor, options.server_port)
    endpoint.listen(serverFactory)

    # wait for myself to start all instances
    from time import sleep
    sleep(5)

    #run reactor
    reactor.run()

if __name__ == '__main__':
    peer_main()
