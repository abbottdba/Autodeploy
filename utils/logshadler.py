import logging
import logging.handlers

class CommonLogging():
    def __init__(self, logfile):
        self.logfmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)s]"

        self.fileshandle = logging.handlers.RotatingFileHandler(logfile, maxBytes=500 * 1024 * 1024, backupCount=10, encoding='utf-8')
        self.formatter = logging.Formatter(self.logfmt)
        self.fileshandle.setFormatter(self.formatter)
        self.logger = logging.getLogger('')
        self.logger.addHandler(self.fileshandle)
        self.logger.propagate = False
        self.logger.setLevel(logging.INFO)


    def logging_debug(self, log):
        self.logger.debug(log)

    def logging_info(self, log):
        self.logger.info(log)

    def logging_warning(self, log):
        self.logger.warning(log)

    def logging_error(self, log):
        self.logger.error(log)

if __name__ == "__main__":
    log_control = CommonLogging('./log.txt')
    log_control.logging_info('This is tet')