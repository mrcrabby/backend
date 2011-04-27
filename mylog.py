import logging

def logstart(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    formater = logging.Formatter("%(name)s %(levelname)s %(asctime)s %(funcName)s %(lineno)d %(message)s")
    handler.setFormatter(formater)
    logger.addHandler(handler)
    return logger


