import optparse
import logging
from twisted.python import log
def parse_args():
        usage = """ TODO - usage
    """

        parser = optparse.OptionParser(usage)
        parser.add_option("-s", "--server_port", dest="server_port", type="int")
        parser.add_option("-c", "--client_port", dest="client_port", type="int")
        options, _ = parser.parse_args()
        return (options)

#common code for both sides

def setupLogger(self, name):
    # create logger
    logging.basicConfig(level=logging.INFO)
    self.logger = logging.getLogger(name)
    # create a file handler
    handler = logging.FileHandler('main.log')
    handler.setLevel(logging.INFO)
    # create a logging format
    formatter = logging.Formatter('%(asctime)s|%(name)s|%(levelname)s|>\t\t%(message)s')
    handler.setFormatter(formatter)
    # add the handlers to the logger
    self.logger.addHandler(handler)
    # add twisted loggs to this log ? not tested with multiple calls of this function
    # observer = log.PythonLoggingObserver(name)
    # observer.start()

def commonInit(self, factory):
    self.factory = factory
    # increase index
    self.index = self.factory.protocolIndex
    self.factory.protocolIndex += 1
    # log state and data
    self.factory.logger.info('protocol created with index {}'.format(self.index))

def commonConnectionMade(self):
    # increase num of active protocols
    self.factory.numProtocols = self.factory.numProtocols + 1
    # log state and data
    self.factory.logger.debug('{} active protocols'.format(self.factory.numProtocols))
    self.factory.logger.info('[protocol {}] connectionMade'.format(self.index))

def commonConnectionLost(self, reason):
    # decrease num of active protocols
    self.factory.numProtocols = self.factory.numProtocols - 1
    # log state and data
    self.factory.logger.info('[protocol {}] connectionLost: {}'.format(self.index, reason))
    self.factory.logger.debug('{} active protocols'.format(self.factory.numProtocols))
