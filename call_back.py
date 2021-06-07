#-*- encoding:utf-8 -*-
from functools import partial
import inspect
import json
from logging import getLogger, StreamHandler, DEBUG, INFO, WARNING, ERROR, CRITICAL
import os
import re
import sys

#logger setting
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(os.getenv("LogLevel", DEBUG))
logger.addHandler(handler)
logger.propagate = False


class PyColor:
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    END = "\033[0m"

def handler(body=None):
    def call_back(match,body = body):
        logger.info(f"{PyColor.RED}{sys._getframe().f_code.co_name} function called{PyColor.END}")
        m = match.group()
        if m in body:
            return body[m]
        return m
    return call_back

def callback(match,body=None):
    logger.info(f"{PyColor.YELLOW}{sys._getframe().f_code.co_name} function called{PyColor.END}")
    m = match.group()
    if m in body:
        return body[m]
    return m

def main():
    #組み込みモジュールfunctools.partialを使う方法
    logger.debug(re.sub(r"key",partial(callback,body={"key" : "value"}),"key"))
    #handler関数を定義。デコレータ関数を使ったときと動きと同じ
    logger.debug(re.sub(r"key",handler(body={"key" : "value"}),"key"))
    #lambda関数を使う方法
    logger.debug(re.sub(r"key",lambda match,body={"key" : "value"}: body[match.group()] if match.group() in body else match.group(),"key"))

if __name__ == "__main__":
    main()
