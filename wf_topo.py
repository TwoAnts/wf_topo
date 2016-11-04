#!/usr/bin/python

"""
Simple example of setting network and CPU parameters

NOTE: link params limit BW, add latency, and loss.
There is a high chance that pings WILL fail and that
iperf will hang indefinitely if the TCP handshake fails
to complete.
"""

import getopt
import sys
trace_file = 'trace.txt'
sim = False

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.node import RemoteController
from mininet.link import OVSLink
from mininet.log import setLogLevel
from mininet.cli import CLI

from sim_flow import TrafficSimThread

class WFTopo(Topo):
    def build(self):
        s = []
        for i in range(3):
            s.append(self.addSwitch('s%s' %(i+1), protocols='OpenFlow13'))

        self.addLink(s[0], s[1])
        self.addLink(s[0], s[2])

        h = []
        for i in range(6):
            h.append(self.addHost('h%s' %(i + 1)))
            self.addLink(h[i], s[1+(i/3)])

def run_mn():
    "Create network and run simple performance test"
    topo = WFTopo()
    net = Mininet( topo=topo,
                   host=CPULimitedHost, link=OVSLink,
                   controller=lambda name:RemoteController(name,
                            ip='127.0.0.1', port=6666),
                   autoStaticArp=False)
    net.start()
    switch1 = net.getNodeByName('s1')

    for i in range(6):
        host = net.getNodeByName('h%s' %(i+1))
        #r = host.cmd('python -m SimpleHTTPServer 8080 &')
        host.cmd('./server.o 8080 &')
    
    print '===clear qos'
    r = switch1.cmd('./clear_qos.sh')
    print "result:\n%s\n" %r
    print 'qos queue after clear:\n%s\n%s\n' \
            %(switch1.cmd('ovs-vsctl list qos'),
                switch1.cmd('ovs-vsctl list queue')) 

    print '===set queue'
    r = switch1.cmd('./set_queue_wf.sh')
    print 'result:\n%s\n' %r

    net.pingAll()
    if sim:
        sim_thr = TrafficSimThread(net, trace_file=trace_file)
        sim_thr.start()

    CLI(net)
    net.stop()

if __name__ == '__main__':
    options, args = getopt.getopt(sys.argv[1:], '', ['sim=', 'trace_file='])
    for k, v in options:
        if k in ('--sim', ):
            sim = (v == 'True')
        elif k in ('--trace_file', ):
            trace_file = v
            print 'set trace_file:%s' %trace_file
            

    setLogLevel('info')
    run_mn()
