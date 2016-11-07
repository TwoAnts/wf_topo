#!/usr/bin/python

"""
Simple example of setting network and CPU parameters

NOTE: link params limit BW, add latency, and loss.
There is a high chance that pings WILL fail and that
iperf will hang indefinitely if the TCP handshake fails
to complete.
"""

import getopt
import sys, os
trace_file = 'trace.txt'
traffic_file = 'traffic.txt'
sim = False
pias = False
depth=2
fanout=2
host_rate=10
host_num_per_switch=4

pingall=False

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.node import RemoteController
from mininet.link import OVSLink
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.cli import CLI

from sim_flow import TrafficSimThread

class TreeTopo(Topo):
    def build(self, depth=2, fanout=2, host_num_per_switch=4):
        self.ovsmode = 'kernel'
        self.hostNum = 1
        self.switchNum = 1
        self.host_num_per_switch = host_num_per_switch
        
        root = self.addSwitch('s0', protocols='OpenFlow13', datapath=self.ovsmode)
        #print 'add %s' %root
        self.addTree(depth, fanout, [root])
    
    def addTree(self, depth, fanout, parents):
        isSwitch = depth > 0
        new_parents = []
        for parent in parents:
            if isSwitch:
                for _ in range(fanout):
                    node = self.addSwitch('s%s' %self.switchNum, protocols='OpenFlow13', datapath=self.ovsmode)
                    self.addLink(node, parent)
                    #print 'add %s to %s' %(node, parent)
                    new_parents.append(node)
                    self.switchNum += 1
            else:
                for _ in range(self.host_num_per_switch):
                    node = self.addHost('h%s' %self.hostNum)
                    self.addLink(node, parent)
                    #print 'add %s to %s' %(node, parent)
                    self.hostNum += 1

        if isSwitch:
            self.addTree(depth-1, fanout, new_parents)

def run_mn():
    "Create network and run simple performance test"
    #topo = WFTopo()
    topo = TreeTopo(depth=depth, fanout=fanout, 
                         host_num_per_switch=host_num_per_switch)
    host_num = topo.hostNum - 1
    net = Mininet( topo=topo,
                   host=CPULimitedHost, link=OVSLink,
                   controller=lambda name:RemoteController(name,
                            ip='127.0.0.1', port=6666),
                   autoStaticArp=False)


    print '===restart ovs'
    p = os.popen('./ovs_daemons_stop.sh && ./ovs_startup.sh')
    for line in p:
        print line   
    p.close()
    

    net.start()
    switch = net.getNodeByName('s0')

    for i in xrange(host_num):
        host = net.getNodeByName('h%s' %(i+1))
        #r = host.cmd('python -m SimpleHTTPServer 8080 &')
        host.cmd('./server.o 8080 &')
    
    print '===clear qos'
    r = switch.cmd('./clear_qos.sh')
    print "result:\n%s\n" %r
    print 'qos queue after clear:\n%s\n%s\n' \
            %(switch.cmd('ovs-vsctl list qos'),
                switch.cmd('ovs-vsctl list queue')) 
    
    
    print '===set queue'
    cmd = './set_queue_wf_args.sh %s %s %s %s' %(\
                depth, fanout, int(host_rate*1e6), host_num_per_switch)
    print cmd
    r = switch.cmd(cmd)
    print 'result:\n%s\n' %r

    if pias:
        devs = ','.join(['h%s-eth0' %(i+1) for i in xrange(host_num)])
        cmd = 'insmod pias.ko param_dev=%s' %devs
        r = switch.cmd('%s && dmesg | tail' %cmd)
        print r


    h1 = net.getNodeByName('h1') 
    if pingall:
       for i in range(1, host_num):
            h = net.getNodeByName('h%s' %(i+1))
            net.ping(hosts=[h1, h])

    if sim:
        sim_thr = TrafficSimThread(net, traffic_file=traffic_file,\
                                 trace_file=trace_file)
        sim_thr.start()

    CLI(net)

    if pias:
        print '===rmmod pias'
        switch.cmd('sudo rmmod pias')
        r = switch.cmd('dmesg | tail')
        print r

    net.stop()

if __name__ == '__main__':
    options, args = getopt.getopt(sys.argv[1:], 'd:f:r:n:p', \
                                   ['sim', 'traffic_file=', 'trace_file=', 'depth=', 'fanout=', \
                                    'rate=', 'host_num_per_switch=', 'pingall', 'pias'])
    for k, v in options:
        if k in ('--sim', ):
            sim = True
        elif k in ('--traffic_file', ):
            traffic_file = v
            print 'set traffic_file:%s' %traffic_file
        elif k in ('--trace_file', ):
            trace_file = v
            print 'set trace_file:%s' %trace_file
        elif k in ('-d', '--depth'):
            depth = int(v)
        elif k in ('-f', '--fanout'):
            fanout = int(v)
        elif k in ('-r', '--rate'):
            host_rate=int(v)
        elif k in ('-n', '--host_num_per_switch'):
            host_num_per_switch=int(v)
        elif k in ('-p', '--pingall'):
            pingall=True
        elif k in ('--pias'):
            pias=True

    setLogLevel('info')
    run_mn()
