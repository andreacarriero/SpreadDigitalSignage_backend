import logging, sys

##Log to file
#logging.basicConfig(filename='data/app.log', filemode='a', level=logging.DEBUG)

#Log to stdout
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

