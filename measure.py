#!/usr/bin/env python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import output, setLogLevel
from mininet.node import Controller, DefaultController, RemoteController
from mininet.node import CPULimitedHost, OVSSwitch, OVSKernelSwitch
from mininet.link import TCLink
from mininet.util import custom, dumpNetConnections, irange, quietRun, waitListening
from mininet.cli import CLI

from time import sleep, time
from multiprocessing import Process
from subprocess import Popen
import argparse

import sys
import os
from util.monitor import monitor_devs_ng

parser = argparse.ArgumentParser(description="Topology bandwith and TCP/UDP tests")

parser.add_argument('--dir', '-d',
                    help="Directory to store outputs",
                    default="results")

parser.add_argument('--cli', '-c',
                    action='store_true',
                    help='Run CLI for topology debugging purposes')

parser.add_argument('--time', '-t',
                    dest="time",
                    type=int,
                    help="Duration of the experiment.",
                    default=60)

parser.add_argument('--size', '-s',
                    dest="size",
                    type=int,
                    help="Size of file for transfer in MB.",
                    default=10)

parser.add_argument('--bw', '-b',
                    dest="bw",
                    type=int,
                    help="Size of bandwidth in Mbps.",
                    default=100)

# Expt parameters
args = parser.parse_args()

if not os.path.exists(args.dir):
    os.makedirs(args.dir)

def waitListening(client, server, port):
    "Wait until server is listening on port"
    if not 'telnet' in client.cmd('which telnet'):
        raise Exception('Could not find telnet')
    cmd = ('sh -c "echo A | telnet -e A %s %s"' % (server.IP(), port))
    while 'Connected' not in client.cmd(cmd):
        output('waiting for', server, 'to listen on port', port, '\n')
        sleep(.5)

def progress(t):
    while t > 0:
        print '  %3d seconds left  \r' % (t)
        t -= 1
        sys.stdout.flush()
        sleep(1)

def start_tcpprobe(protocol=None):
    os.system("rmmod tcp_probe 1>/dev/null 2>&1; modprobe tcp_probe")
    if protocol:
        Popen("cat /proc/net/tcpprobe > %s/tcp_probe-%s.txt" % (args.dir, protocol), shell=True)
    else:
        Popen("cat /proc/net/tcpprobe > %s/tcp_probe.txt" % args.dir, shell=True)

def stop_tcpprobe():
    os.system("killall -9 cat; rmmod tcp_probe")

def get_txbytes(iface):
    f = open('/proc/net/dev', 'r')
    lines = f.readlines()
    for line in lines:
        if iface in line:
            break
    f.close()
    if not line:
        raise Exception("could not find iface %s in /proc/net/dev:%s" % (iface, lines))
    return float(line.split()[9])

def get_rates(iface, nsamples=1, period=30, wait=10):
    """Returns rate in Mbps"""
    # Returning nsamples requires one extra to start the timer.

    nsamples += 1
    last_time = 0
    last_txbytes1 = 0
    last_txbytes2 = 0
    ret = []
    sleep(wait)
    iface1 = 's1-eth1'
    iface2 = 's2-eth1'
    while nsamples:
        nsamples -= 1

        txbytes1 = get_txbytes(iface1)
        txbytes2 = get_txbytes(iface2)
    
        now = time()
        elapsed = now - last_time
 
        last_time = now

        rate1 = (txbytes1 - last_txbytes1) * 8.0 / 1e6 / elapsed
        rate2 = (txbytes2 - last_txbytes2) * 8.0 / 1e6 / elapsed
        if last_txbytes1 != 0:
            ret.append(rate1)
            ret.append(rate2)
            ret.append(rate1+rate2)
        last_txbytes1 = txbytes1
        last_txbytes2 = txbytes2
        sys.stdout.flush()
        sleep(period)
    return ret

def iperf_experiment(net):
    print "*** Running iperf experiment"
    
    # Get receiver and clients
    sender = net.getNodeByName('sender')
    receiver = net.getNodeByName('receiver')
    
    s1 = net.getNodeByName('s1')
    s2 = net.getNodeByName('s2')
    
    port = 5001
    
    # Start the bandwidth and cwnd monitors in the background
    monitor = Process(target=monitor_devs_ng, args=('%s/bwm-iperf-udp.txt' % args.dir, 1.0))
    monitor.start()
    start_tcpprobe("udp")
    
    # Start the receiver
    receiver.cmd('iperf -s -w 256K -l 16K -u -p', port, '> %s/iperf_server-udp.txt' % args.dir, '&')
    
    print "*** Starting iperf udp"
    sender.sendCmd('iperf -c %s -p %s -t %d -i 1 -r -w 256K -l 16K -u -b %dM -yc > %s/iperf_client-udp.txt' %
	           (receiver.IP(), port, args.time, args.bw, args.dir))
    sender.waitOutput(verbose=True)
    print "*** Killing iperf proc"

    receiver.cmd('kill %iperf')

    # Shut down monitors
    stop_tcpprobe()
    monitor.terminate()
    os.system("killall -9 bwm-ng")
    
    
    ### do tcp test
    monitor = Process(target=monitor_devs_ng, args=('%s/bwm-iperf-tcp.txt' % args.dir, 1.0))
    monitor.start()
    start_tcpprobe("tcp")
    
    # Start the receiver
    receiver.cmd('iperf -s -w 256K -l 16K -p', port, '> %s/iperf_server-tcp.txt' % args.dir, '&')
    waitListening(sender, receiver, port)

    print "*** Starting iperf tcp"
    sender.sendCmd('iperf -c %s -p %s -t %d -i 1 -r -w 256K -l 16K -yc > %s/iperf_client-tcp.txt' %
	           (receiver.IP(), port, args.time, args.dir))
    sender.waitOutput(verbose=True)
    print "*** Killing iperf proc"
    
    receiver.cmd('kill %iperf')
    
    # Shut down monitors
    stop_tcpprobe()
    monitor.terminate()
    os.system("killall -9 bwm-ng")
    
    print "*** End iperf experiment"

def transfer_experiment(net, program):
    print("*** Running file transfer experiment with %s" % program)

    # Start the bandwidth and cwnd monitors in the background                                                                               
    monitor = Process(target=monitor_devs_ng, args=('%s/bwm-tx.txt' % args.dir, 1.0))
    monitor.start()

    # Get receiver and clients                                                                                                             
    sender = net.getNodeByName('sender')
    receiver = net.getNodeByName('receiver')

    s1 = net.getNodeByName('s1')
    s2 = net.getNodeByName('s2')

    # Start sshd on all hosts
    sender.cmd('/usr/sbin/sshd -D &')
    receiver.cmd('/usr/sbin/sshd -D &')
    print "*** Started sshd on all hosts"

    print("*** Creating %s MB testfile for transfer" % args.size)
    sender.cmd('dd if=/dev/zero of=/home/vagrant/testfile-send bs=1 count=0 seek=%sM' % args.size)

    # Start the data transfer
    print("*** Sending file using %s" % program)
    sender.sendCmd('scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no /home/vagrant/testfile-send %s:/home/vagrant/testfile-receive' % receiver.IP())
    sender.waitOutput(verbose=True)
    print "*** File transfer complete"

    # Shut down monitors                                                                                                      
    monitor.terminate()
    os.system("killall -9 bwm-ng")
    
    print "*** End file transfer experiment"

def check_prereqs():
    "Check for necessary programs"
    prereqs = ['bwm-ng', 'iperf', 'ping', 'scp', 'telnet']
    for p in prereqs:
        if not quietRun('which ' + p):
            raise Exception((
                'Could not find %s - make sure that it is '
                'installed and in your $PATH') % p)

def main():
    host = custom(CPULimitedHost, cpu=.15) # 15% of system bandwidth
    link = custom(TCLink, max_queue_size=500)

    #net = Mininet(host=host, link=link, controller=RemoteController, switch=OVSKernelSwitch)
    net = Mininet(host=host, link=link, controller=DefaultController, switch=OVSKernelSwitch)
    
    print "*** Creating controllers"
    #c1 = RemoteController('c1', ip='127.0.0.1', port=6633)
    #c2 = RemoteController('c2', ip='127.0.0.1', port=6634)
    #c1 = net.addController('c1', controller=RemoteController, ip="127.0.0.1", port=6633)
    #c2 = net.addController('c2', controller=RemoteController, ip="127.0.0.1", port=6634)

    c1 = net.addController('c1')
    c2 = net.addController('c2')

    print "*** Creating switches"
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')

    # Create data transfer machines (DTMs)
    print "*** Creating hosts"
    hostConfig = {'cpu': .25}
    dtm1 = net.addHost('sender',   ip='10.0.0.1', **hostConfig)
    dtm2 = net.addHost('receiver', ip='10.0.0.2', **hostConfig)

    # Add network links
    print "*** Adding links"
    linkConfig = {'bw': args.bw, 'delay': '5ms', 'loss': 0, 'max_queue_size': None}
    net.addLink(dtm1, s1, **linkConfig)
    net.addLink(s1, s2, **linkConfig)
    net.addLink(s2, dtm2, **linkConfig)
    
    # Build the network and start experiment
    print "\n*** Building the network"
    net.build()
    
#    c1.start()
#    c2.start()
    s1.start([ c1 ])
    s2.start([ c2 ])

    net.start()
    start = time()
    
    print "*** Dumping network connections:"
    dumpNetConnections(net)

    print "*** Testing connectivity"
    net.pingAll()

    if args.cli:
        # Run CLI instead of experiment
        CLI(net)
    else:
        iperf_experiment(net)
        transfer_experiment(net, "scp")

    end = time()
    net.stop()

    print "Experiment took %.3f seconds" % (end - start)

if __name__ == '__main__':
    check_prereqs()
    
    setLogLevel('info')
    main()
