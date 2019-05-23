# -*- coding: utf-8 -*-
# @Time    : 10/2/2017 2:09 PM
# @Author  : Abbott
# @Site    : 
# @File    : logsutils.py
# @Software: PyCharm

import logging
import logging.handlers

class CommonLogging():
    """
    记录log Class
    """

    def __init__(self, logfile):
        # self.logfmt = "%(asctime)s[level-%(levelname)s][%(name)s]:%(message)s"
        self.logfmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)s]"
        # logging.basicConfig()

        # logfile = commonconf.logfile
        self.fileshandle = logging.handlers.RotatingFileHandler(logfile, maxBytes=500 * 1024 * 1024, backupCount=10)
        # self.fileshandle = logging.handlers.TimedRotatingFileHandler(logfile,  when='M', interval=5, backupCount=3)
        # self.fileshandle.suffix = "%Y%m%d-%H.log"
        # self.fileshandle.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter(self.logfmt)
        self.fileshandle.setFormatter(self.formatter)
        self.logger = logging.getLogger('')
        self.logger.addHandler(self.fileshandle)
        self.logger.propagate = False
        self.logger.setLevel(logging.DEBUG)

    # def inputLogFile(self, logfile):
    #     """
    #     log方法基本一些参数配置，暂时没什么要修改的，唯一要修改的是日志文件目录，通过commonconf里的logfile配置
    #     :return:
    #     """


    def logging_debug(self, log):
        """
        日志级别为debug
        :param log: 要写入的日志内容
        :return:
        """
        self.logger.debug(log)

    def logging_info(self, log):
        """
        日志级别为info
        :param log: 要写入的日志内容
        :return:
        """
        self.logger.info(log)

    def logging_warning(self, log):
        """
        日志级别为dwarning
        :param log: 要写入的日志内容
        :return:
        """
        self.logger.warning(log)

    def logging_error(self, log):
        """
        日志级别为error
        :param log: 要写入的日志内容
        :return:
        """
        self.logger.error(log)
