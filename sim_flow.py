#! /usr/bin/env python
#-*- coding:UTF-8 -*-

import threading
import time 

traffic_file = 'traffic.txt'
trace_file = 'trace.txt'
class FlowThread(threading.Thread):
    def __init__(self, parent, host, server_ip, size, id):
        self.parent = parent
        self.host = host
        self.server_ip = server_ip
        self.size = size
        self.id = id
        threading.Thread.__init__(self)

    def run(self):
        cmd = './client.o %s %s %s' %(self.server_ip, 8080, self.size)
        stdout, stderr = self.host.popen(cmd).communicate()
        result = stdout.split()
        if len(result) >= 2:
            #Get FCT for this flow and 
            print '[%s] %s %s' %(self.id, self.host.name, stdout)
            fct = int(result[-2])
            self.parent.fcts[self.id] = fct
    

class TrafficSimThread(threading.Thread):
    def __init__(self, mn, traffic_file=traffic_file, trace_file=trace_file):
        self.mn = mn
        self.traffic_file = traffic_file
        self.trace_file = trace_file
        self.threads = []
        self.fcts = []
        threading.Thread.__init__(self)

    def get_node(self, name):
        return self.mn.getNodeByName(name)

    def run(self):
        print '====sim start===='
        f = open(self.traffic_file, 'r')
        i = 0
        begin = time.time()
        for line in f:
            if line.strip().startswith('#'):
                continue
            tmp = line.split()
            if len(tmp) >= 4:
                self.fcts.append(0)
                next_time = float(tmp[0])/1000 - (time.time() - begin)
                if next_time < 0:
                    next_time = 0
                flow_size = int(tmp[1])
                req_h = self.get_node(tmp[2])
                resp_h = self.get_node(tmp[3])
                #Wait for the next time
                time.sleep(next_time)
                #Make flow
                thread = FlowThread(self, req_h, resp_h.IP(), flow_size, i)
                thread.start()
                self.threads.append(thread)
                i += 1
                begin = time.time()
        
        f.seek(0) #seek to start

        for thr in self.threads:
            thr.join()

        print 'save trace to %s' %self.trace_file
        i = 0
        o = open(self.trace_file, 'w')
        for line in f:
            if line.strip().startswith('#'):
                continue
            next_time, flow_size, req_h, resp_h = line.split()
            r = '%s\t%s\t%s\t%s\n' %(flow_size, req_h,\
                                     resp_h, self.fcts[i]) 
            i += 1
            o.write(r)
        o.close()

        f.close()

        print '====sim done!===='
