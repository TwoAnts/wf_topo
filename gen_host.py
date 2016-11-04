#!/usr/bin/python
import random

T_WEB = 'web_server'
T_FILE = 'file_server'
T_MDS = 'mds'
T_OSD = 'osd'
req_ts = [T_WEB, T_FILE]
resp_ts = [T_MDS, T_OSD]


host_dist_file = 'conf_host_dist.txt'
host_file = 'conf_host.txt'

req_host_dist = []
resp_host_dist = []

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

    f = open(host_file, 'w')
    
    for h in range(host_num):
        host = 'h%s' %(h+1) 
        t1, t2 = host_type(req_host_dist, resp_host_dist, random.random(), random.random())
        f.write('%s %s %s\n' %(host, t1, t2))
    
    f.close()
    print 'gen %s' %host_file
    print 'Done!'
        
        
        
       
            
