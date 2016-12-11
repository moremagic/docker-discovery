#!/usr/bin/python3

import os
import sys
import time
import json
import socket
import redis
import urllib.request

DOCKER_HOST = os.getenv('DOCKER_HOST')
REDIS_ADDR = '127.0.0.1'
REDIS_PORT = 6379


def redisDump():
    conn = redis.Redis(host=REDIS_ADDR, port=REDIS_PORT)
    for key in conn.keys():
        print(key + ' ==  ' + conn.get(key))
    return conn.keys()


def addData(datas):
    conn = redis.Redis(host=REDIS_ADDR, port=REDIS_PORT)
    for key in set(list(datas.keys()) + list(conn.keys())):
        if isinstance(key, bytes):
            key = key.decode('utf-8')
        if key in datas:
            conn.set(key, datas[key])
        else:
            conn.delete(key)


def getContainers():
    response = urllib.request.urlopen(
        'http://' + DOCKER_HOST + '/containers/json?all=1')
    jsonData = json.loads(response.read().decode('utf-8'))
    datas = {}

    for con in jsonData:
        name = con['Names'][-1][1:]
        name = name[name.find('/')+1:]
        for port in con['Ports']:
            key = name.replace('_','-') + '-' + str(port['PrivatePort']) # RFC952
            if 'IP' in port:
                value = str(port['IP']).replace('0.0.0.0', DOCKER_HOST[:DOCKER_HOST.find(':')]) + ':' + str(port['PublicPort'])
                datas[key] = value
                print( key + '(' +  value + ')' )

    return datas


def getIpAddress(name):
    try:
        return socket.gethostbyname(name)
    except:
        return 'unknown'

while True:
    try:
        addData(getContainers())
        print(redisDump())
        sys.stdout.flush()
    except Exception as e:
        print(e)
    time.sleep(3)

