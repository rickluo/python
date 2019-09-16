from django.http import HttpResponse
import json, os
import sys
import re
import getopt
import subprocess
import time
import threading
import redis
import random

class RequestRedis():
    def get_ipport(self,redis_bns='bnsname'):
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

def check(request):
    return HttpResponse("gundam")

def state_afs(request):
    timestamp=time.strftime("%Y%m%d",time.localtime())
    redis_req=RequestRedis()
    redis_ipport=redis_req.get_ipport()
    redis_ip=redis_ipport[0]
    redis_port=int(redis_ipport[1])
    redis_client=redis.StrictRedis(host=redis_ip,port=redis_port)
    afs_capacity=1500
    afs_capacity_available=redis_client.hget("afs_bdrp",timestamp)
    if not afs_capacity_available:
	afs_capacity_available=28000
    afs_capacity_available=float(afs_capacity_available)
    afs_capacity_available=afs_capacity_available - afs_capacity
    afs_capacity_available="%0.2f"%(afs_capacity_available/1000)
    info_return=[{'tag':'P'},{'afs_pool':'yes','capacity':1.5},{'afs_pool':'no','capacity':afs_capacity_available}]
    info_return=json.dumps(info_return)
    return HttpResponse(info_return)

