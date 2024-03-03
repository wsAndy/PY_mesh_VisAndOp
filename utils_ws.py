import os
import json
import sys
import re
import time
from deepdiff import DeepDiff
from subprocess import run
from loguru import logger
from subprocess import Popen, run, PIPE

def initLog(_path = f"./utils-ws_{time.strftime('%Y-%m')}.log"):
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    logger.add(f"{_path}",
               format="{time:YYYY-MM-DD HH:mm:ss,SSS} {level} {message}", rotation="50MB", encoding="utf-8",
               enqueue=True)

def executeCommand(*args, display=False):
    if not display:
        p = Popen(' '.join(list(args)), shell=True, stdout=PIPE, stderr=PIPE)
    else:
        p = Popen(' '.join(list(args)), shell=True)
    retCode = p.wait()
    if not display:
        if re.match(r'failed', p.stdout.read().decode()):
            return 1
    return retCode

def getMemSize(path):
    return round(os.path.getsize(path) / (1024 * 1024), 2)


def findFiles(path, _startwith="", _endswith=""):
    '''
    指定目录下寻找指定格式文件
    '''
    _startwith = _startwith.lower()
    _endswith = _endswith.lower()
    if os.path.exists(path) and os.path.isdir(path):
        files = os.listdir(path)
        res = []
        if (_startwith != "" and _endswith != ""):

            res = [x for x in files if x.lower().endswith(_endswith) and x.lower().startswith(_startwith)]
        elif _startwith == "" and _endswith != "":
            res = [x for x in files if x.lower().endswith(_endswith)]
        elif _startwith != "" and _endswith == "":
            res = [x for x in files if x.lower().startswith(_startwith)]
        else:
            res = [x for x in files]
        return res
    else:
        return None


def checkfolderExist(_path):
    '''
    检查文件夹是否存在
    '''
    if (_path is not None) and os.path.exists(_path) and os.path.isdir(_path):
        return _path
    else:
        return None

def checkfileExist(_filepath):
    '''
    检查文件是否存在
    '''
    if (_filepath is not None) and os.path.exists(_filepath) and os.path.isfile(_filepath):
        return _filepath
    else:
        return None
