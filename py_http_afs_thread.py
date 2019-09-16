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
import threading
import redis
import random


# Usage args
options,args=getopt.getopt(sys.argv[1:],'hl:k:b:p:')

def usage():
    script_name=sys.argv[0]

    print '''
    Usage:
        %s -l list_host
        %s -b bns_name
        %s -p bns_path

    ''' %(script_name,script_name,script_name)
    sys.exit()

try:
    sys_argv=sys.argv[1]

except Exception:
    usage()

# Pre Define
bns_name='no'
bns_path='no'

for name,value in options:
    if name == '-h':
        usage()
    if name == '-l':
        list_host=value
    if name == '-k':
        keyname=value
    if name == '-b':
        bns_name=value
    if name == '-p':
        bns_path=value

# Class
# http://$url:8529/agents.jsp?priority=STABLE&tag=bdrp-feed
class HttpReqHost():
    def __init__(self,idc_region,ip):
        self.idc_region=idc_region  
        self.ip=ip  

    def http_get(self):
        http_address = "%s.m.b.com"%(self.idc_region)
        request_data = "/agentdetail.jsp?hostId=%s"%(self.ip)
        headers = {'Content-type': 'application/x-www-form-urlencoded', 'Accept': 'text/plain'}
        httpClient = httplib.HTTPConnection(http_address, 8529, timeout=10)
        httpClient.request('GET', request_data, None, headers)
        response = httpClient.getresponse()
        return response.read()

class HostnameToip():
    def __init__(self,hostname):
        self.hostname=hostname

    def analyze_ip_region(self):
        host_info = self.hostname
        host_info = host_info.split('.')
        host_region = host_info[1]
        cmd = ['host',self.hostname]
        cmd_re = subprocess.check_output(cmd)
        cmd_re = re.split('\s',cmd_re)
        host_ip = cmd_re[3]
        if host_region == 'szwg01':
            host_region = 'szwg'
        data_return = [host_region,host_ip]
        return data_return
        
class FileToList():
    def __init__(self,file_name):
        self.file_name=file_name

    def cont_to_array(self):
        data_return = []
        fp=open(self.file_name,'r')
        for line in fp.readlines():
            line=line.strip()
            data_return.append(line)
        fp.close()
        return data_return

    def clear_to_file(self):
        fp=open(self.file_name,'w')
        fp.close()
 
    def write_to_file(self,line):
        fp=open(self.file_name,'a')
        fp.write("%s\n"%(line))


class VerifyIdc():
    def __init__(self,idc):
        self.idc=idc

    def verify_idc(self):
        idc_bj=['bjyz', 'cp01', 'cq01','cq02', 'm1', 'tc', 'st01','bjhw','dbl']
        idc_gz=['gzhl', 'gzhxy', 'gzns','gzbh']
        idc_hz=['hz01']
        idc_nj=['nj01','nj02', 'nj03', 'njjs']
        idc_nmg=['nmg01','nmg02','nmg012']
        idc_sh=['sh01']
        idc_sz=['szth', 'szwg','szwg01','szwg3']
        idc_yq=['yq01','yq011','yq014']
        idc=self.idc

        if idc in idc_bj:
            return "bj"
        if idc in idc_gz:
            return "gz"
        if idc in idc_hz:
            return "hz"
        if idc in idc_nj:
            return "nj"
        if idc in idc_nmg:
            return "nmg"
        if idc in idc_sh:
            return "sh"
        if idc in idc_sz:
            return "sz"
        if idc in idc_yq:
            return "yq"

class MyThread(threading.Thread):

    def __init__(self,func,args=()):
        super(MyThread,self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result 
        except Exception:
            return None

class RequestRedis():
    def get_ipport(self,redis_bns='g.redisop-recovery-p.M.all'):
        redis_bns=redis_bns
        shell_cmd_args=['get_instance_by_service','-ab',redis_bns]
        p=subprocess.Popen(shell_cmd_args,stdout=subprocess.PIPE)
        tmp_array=[]
        for line in p.stdout.readlines():
            line=re.sub('(\s+)',',',line)
            line=line.split(',')
            if line[4] == "0":
                tmp_array.append("%s:%s"%(line[1],line[3]))

        p.wait()
        max_num = len(tmp_array)-1
        random_num = random.randint(0,max_num)
        value_return = tmp_array[random_num]
        value_return = value_return.split(':')
        return value_return

# Function
def http_get_disk_size(idc,ip):
    httpinfo=HttpReqHost(idc,ip)
    try:
        json_httpinfo=httpinfo.http_get()
    except Exception:
        return "fail %s %s"%(idc,ip)

    json_httpinfo=httpinfo.http_get()
    idcinfo=VerifyIdc(idc)
    region=idcinfo.verify_idc()
    array=[]
    size=0
    count=0
    for x in json_httpinfo.splitlines():
        if re.search('disk.*hdd',x):
            x=re.sub('\<[a-z]*\>|\<\/[a-z]*\>|\<a.*\"\>',' ',x)
            x=re.sub('\s+',',',x)
            x=re.sub('^,|,$','',x)
            x=x.split(',')
            x=x[2]
            x=x.split('/')
            x=x[3]
            x=int(x)
            x= x / 1000
            array.append(x)
            count += 1            

    if len(array) == 0:
        return_info="%s %s %s %s"%(idc,ip,0,0)
        return return_info
    for x in array[1:]:
            size += x

    return_info="%s %s %s %s"%(region,ip,size,count)
    return return_info

def calculate_capacity_from_afs(array_re_afs):
    array_re_afs=array_re_afs
    capa=0
    float(capa)

    for element in array_re_afs:
        element=element.split(' ')
        if re.search('[0-9]+\.[0-9]+\.[0-9]+\.',element[1]):
            a=float(element[2])
            capa=capa + a
            
    print "capacity of afs is %0.2f P"%(capa/1000)
    return capa

# Main
file_open=FileToList(list_host)
file_write=FileToList('/tmp/result.py.afs')
file_write.clear_to_file()
ip_list=file_open.cont_to_array()
ip_list_len=len(ip_list)
num_thread_max=20
array_thread=[]
base_count=0
proc_count=0
array_proc_results=[]

for host in ip_list:
    hostname_op = HostnameToip(host)
    ip_r = hostname_op.analyze_ip_region()
    idc = ip_r[0]
    ip = ip_r[1]
    t=MyThread(http_get_disk_size,(idc,ip))
    #array_thread.append(threading.Thread(target=http_get_disk_size,args=(idc,ip)))
    array_thread.append(t)
    base_count+=1
    proc_count+=1
    if proc_count == ip_list_len:
        for thread_proc in array_thread:
            thread_proc.setDaemon(True)
            thread_proc.start()
        for thread_proc in array_thread:
            thread_proc.join()
            return_proc=thread_proc.get_result()
            array_proc_results.append(return_proc)
            file_write.write_to_file(return_proc)
        base_count=0
    if base_count == num_thread_max:
        for thread_proc in array_thread:
            thread_proc.setDaemon(True)
            thread_proc.start()
        for thread_proc in array_thread:
            thread_proc.join()
            return_proc=thread_proc.get_result()
            array_proc_results.append(return_proc)
            file_write.write_to_file(return_proc)
        base_count=0
        array_thread=[]

# Results save to redis
timestamp=time.strftime("%Y%m%d",time.localtime())
afs_capa=calculate_capacity_from_afs(array_proc_results)
redis_req=RequestRedis()
redis_ipport=redis_req.get_ipport()
redis_ip=redis_ipport[0]
redis_port=redis_ipport[1]
redis_client=redis.StrictRedis(host=redis_ip,port=redis_port)
redis_client.hset("afs_bdrp",timestamp,afs_capa)

print "key:%s,value:%s"%(timestamp,afs_capa)
for x in array_proc_results:
    if re.search('fail',x):
        print x
