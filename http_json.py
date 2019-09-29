#!/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import json, os
import urllib, httplib
import sys
import re
import getopt
import subprocess
import time
import thread


# Usage args
options,args=getopt.getopt(sys.argv[1:],'hl:c:b:')

def usage():
    script_name=sys.argv[0]

    print '''
    Usage:
        %s -c cmd
    ''' %(script_name)
    sys.exit()

try:
    sys_argv=sys.argv[1]

except Exception:
    usage()


for name,value in options:
    if name == '-h':
        usage()
    if name == '-l':
        list_host=value
    if name == '-c':
        keyname=value
    if name == '-b':
        bnsname=value

# Class
class HttpReqHost():

    def http_get(self):
        #http://$url
        http_address = "google.com"
        request_data = "/api/xxxxx"
        headers = {'Content-type': 'application/x-www-form-urlencoded', 'Accept': 'text/plain'}
        httpClient = httplib.HTTPConnection(http_address, 80, timeout=10)
        httpClient.request('GET', request_data, None, headers)
        response = httpClient.getresponse()
        return response.read()

    def http_json_proc(self,json_info):
        json_info=json.loads(json_info)        
        array_req=json_info['name']
        return array_req


# Main
a=HttpReqHost()
b=a.http_get()

jsoninfo=json.loads(b)

for x in jsoninfo:
    print x['name']
