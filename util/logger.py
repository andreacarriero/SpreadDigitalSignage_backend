import logging, sys

#file_handler = logging.FileHandler(filename='data/app.log')
stdout_handler = logging.StreamHandler(sys.stdout)
handlers = [stdout_handler]

logging.basicConfig(
    level=logging.DEBUG, 
    format='[%(asctime)s] %(name)s {%(funcName)s on %(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    handlers=handlers
)
