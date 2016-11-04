#!/usr/bin/python

import random
import sys
import math
from getopt import getopt

host_file = 'conf_host.txt'
flow_distrb_file = 'conf_flows_dist.txt'
req_host = {}
resp_host = {}
flow_distribution = []
htypes = {}
distrb = {}

def usage():
    usage_str =\
    '''
generate flow(size, send time, req_host, resp_host)
Options:
    --load=<load> : 0~1, load of network
    --flow_num=<num> : flow number to generate
    --cap=<num> : Mb, the capicity of link
    -o<dst_file> : file to write
    '''
    print usage_str

def load_hosts():
    f = open(host_file, 'r')
    for line in f:
        tmp = line.split()
        if len(tmp) >= 3:
            req_ht = tmp[1]
            resp_ht = tmp[2]
            hname = tmp[0]
            req_host[hname] = req_ht
            resp_host[hname] = resp_ht
            htypes.setdefault(req_ht, [])
            htypes[req_ht].append(hname)
            htypes.setdefault(resp_ht, [])
            htypes[resp_ht].append(hname)

    f.close()
    print 'load %s' %host_file 

def load_flow_distribution():
    f = open(flow_distrb_file, 'r')
    var = 0
    for line in f:
        tmp = line.split()
        if len(tmp) >= 3:
            var += float(tmp[2])
            d_ht = (tmp[0], tmp[1])
            flow_distribution.append((var, d_ht))
            #print str(d_ht)
    f.close()
    print 'load %s' %flow_distrb_file

def choice_req_resp():
    rand = random.random()
    d_ht = None
    for var in flow_distribution:
        if var[0] >= rand:
            d_ht = var[1]
            break

    if d_ht:
        req_h = random.choice(htypes[d_ht[0]])
        resps = htypes[d_ht[1]]
        i = random.randint(0, len(resps) - 1)
        resp_h = resps[i]
        if req_h == resp_h:
            resp_h = resps[(i+1)%len(resps)]
        return (req_h, resp_h)
    else:
        return None

def traffic_fname(req_h, resp_h):
    if req_h not in req_host or \
            resp_h not in resp_host:
        return None
    type1 = req_host[req_h]
    type2 = resp_host[resp_h]
    return 'conf_%s_%s.txt' %(type1, type2)

def get_distribution(req_h, resp_h):
    fname = traffic_fname(req_h, resp_h)
    #print fname
    if fname in distrb:
        return distrb[fname]
    else:
        f = open(fname, 'r')
        d = []
        for line in f:
            tmp = line.split()
            tmp = (float(tmp[1]), int(tmp[0]))
            d.append(tmp)
        distrb[fname] = d
        f.close()
        return d


#http://pershing.com/20111007/how-to-generate-random-timings-for-a-poisson-process/
#Return next time interval (ms)
def nextTime(rateParameter):
    return round(-math.log(1.0 - random.random()) / rateParameter)

#Given a flow distribution and a random number in (0,1), return a flow size (KB)
def flowsize(distribution, random):
    i = 0
    for var in distribution:
        if var[0] > random:
            x1 = distribution[i-1][0]
            x2 = distribution[i][0]
            y1 = distribution[i-1][1]
            y2 = distribution[i][1]
            value = int((y2-y1)/(x2-x1)*random+(x2*y1-x1*y2)/(x2-x1))
            return value
        elif var[0] == random:
            return int(var[1])
        else:
            i+=1
    return 0
    

if __name__ == '__main__':
    load = 0.5
    capacity = 10 #Mb
    flow_num = 1000
    output = 'traffic.txt'
    options, args = getopt(sys.argv[1:], 'o:h', ['load=', 'cap=', 'flow_num=', 'help'])
    for k, v in options:
        if k in ('--load', ):
            load = float(v)
        elif k in ('--cap', ):
            capacity = int(v)
        elif k in ('--flow_num', ):
            flow_num = int(v)
        elif k in ('-o', ):
            output = v
        elif k in ('-h', '--help'):
            usage()
            exit()
        else:
            print 'unsupported option %s' %k
            usage()
            exit()

    load_hosts()
    load_flow_distribution()

    flows = []
    size_sum = 0
    for i in range(flow_num):
        req_h, resp_h = choice_req_resp()
        dis = get_distribution(req_h, resp_h)
        flow_size = flowsize(dis, random.random())
        flows.append((req_h, resp_h, flow_size))
        size_sum += flow_size
    
    throughput = load * capacity
    avg = size_sum / len(flows)
    #Get average number of requests per second
    num = throughput*1024*1024 / (avg*1024*8)
    #Get average request rate (number of requests every 1 ms)
    rate = num/1000

    times = []
    for i in range(flow_num):
        times.append(nextTime(rate))

    output_file = open(output, 'w')
    output_file.write('#flow_num:%s, load:%s, capacity:%s\n' %(\
                            flow_num, load, capacity))

    for i in range(flow_num):
        output_file.write('%s %s %s %s\n' %(times[i], \
                flows[i][2], flows[i][0], flows[i][1]))

    output_file.write('#average flow size: %s KB\n' %avg)
    output_file.write('#request speed: %s requests/second\n' %num)
    output_file.write('#last for about %s seconds\n' %(len(flows)/num))
    output_file.close()
    
    print 'Auto generate %s flows' %len(flows)
    print 'The average flow size: %s KB' %avg
    print 'The average request speed: %s requests/second' %num
    print 'Dynamic flow emulation will last for about %s seconds' %(len(flows)/num)
    print 'save to %s' %output
    print 'Done'
    


            
            
    


