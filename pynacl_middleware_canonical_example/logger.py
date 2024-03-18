from logging import getLogger, basicConfig, DEBUG

basicConfig(filename='debug.log',
            filemode='a',
            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
            datefmt='%H:%M:%S',
            level=DEBUG)

log = getLogger('log')