#!/usr/bin/python
import random
import sys
from getopt import getopt

T_WEB = 'web_server'
T_FILE = 'file_server'
T_MDS = 'mds'
T_OSD = 'osd'
req_ts = [T_WEB, T_FILE]
resp_ts = [T_MDS, T_OSD]


host_dist_file = 'conf_host_dist.txt'
host_file = 'conf_host.txt'
host_file_single = 'conf_host_single.txt'

is_single = False

req_d = 5
resp_d = 5
req_host_dist = []
resp_host_dist = []

def usage():
    print 'generate host from conf_host_dist.txt'
    print 'Options:'
    print '    -s, --single : host only have one type'

def host_type_single(req_d, resp_d, host_index, host_sum):
    req_num = host_sum * req_d / (req_d + resp_d)
    if host_index < req_num:
        dist = req_host_dist
        dist_sum = req_num
    else:
        dist = resp_host_dist
        dist_sum = host_sum - req_num
        host_index -= req_num

    if host_index < int(dist[0][1] * dist_sum):
        return dist[0][0]
    else:
        return dist[1][0]
    
def host_type(req_host_dist, resp_host_dist, i, j):
    req = None
    resp = None
    for var in req_host_dist:
        if var[1] >= i:
            req = var[0]
            break
    
    for var in resp_host_dist:
        if var[1] >= j:
            resp = var[0]
            break

    return (req, resp)
        

if __name__ == '__main__':
    options, args = getopt(sys.argv[1:], 's:', ['single='])
    for k, v in options:
        if k in ('-s', '--single'):
            is_single = True
            tmp = v.split('_')
            req_d, resp_d = int(tmp[0]), int(tmp[1])
        else:
            usage()
            exit()

    
    f = open(host_dist_file, 'r')

    line = f.readline()
    tmp = line.split(':')
    if len(tmp) == 2 and tmp[0].strip() == 'host_num':
        host_num = int(tmp[1])
    else:
        f.seek(0)

    req_sum_d = 0.0
    resp_sum_d = 0.0
    for line in f:
        tmp = line.split()
        if len(tmp) >= 2:
            t, d = tmp[0:2]
            if t in req_ts:
                req_sum_d += float(d)
                if req_sum_d > 1:
                    req_host_dist.append((t, 1))
                    continue
                req_host_dist.append((t, req_sum_d))
            elif t in resp_ts:
                resp_sum_d += float(d)
                if resp_sum_d > 1:
                    resp_host_dist.append((t, 1))
                    continue
                resp_host_dist.append((t, resp_sum_d))
            else:
                print 'unexpect type:%s' %t

    f.close()

    print 'load %s' %host_dist_file
    print 'host_num:%s' %host_num
    print 'req %s' %req_host_dist
    print 'resp %s' %resp_host_dist
    if is_single:
        print 'req_d:resp_d %s:%s' %(req_d, resp_d)

    if is_single:
        f = open(host_file_single, 'w')
        f.write('#req:resp %s:%s\n' %(req_d, resp_d))
        for h in range(host_num):
            host = 'h%s' %(h+1)
            t = host_type_single(req_d, resp_d, h, host_num)
            f.write('%s %s\n' %(host, t))
        f.close()
        print 'gen %s' %host_file_single
    else:
        f = open(host_file, 'w')
    
        for h in range(host_num):
            host = 'h%s' %(h+1) 
            t1, t2 = host_type(req_host_dist, resp_host_dist, random.random(), random.random())
            f.write('%s %s %s\n' %(host, t1, t2))
    
        f.close()
        print 'gen %s' %host_file

    print 'Done!'
        
        
        
       
            
