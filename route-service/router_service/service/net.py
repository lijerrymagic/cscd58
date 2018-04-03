#!/usr/bin/python
from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSKernelSwitch, UserSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import Link, TCLink


def Network():
    net = Mininet(controller=RemoteController, link=TCLink, switch=OVSKernelSwitch)

    print "*** Creating end system node"
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='20.0.0.1/24')

    print "*** Creating router node"
    r1 = net.addHost('r1', ip='10.0.0.2/24')
    r2 = net.addHost('r2', ip='20.0.0.2/24')
    r3 = net.addHost('r3', ip='40.0.0.2/24')

    print "*** Creating links"
    net.addLink(h1, r1, intfName1='h1-r1', intfName2='r1-h1')
    net.addLink(h2, r2, intfName1='h2-r2', intfName2='r2-h2')
    net.addLink(r1, r2, intfName1='r1-r2', intfName2='r2-r1')
    net.addLink(r1, r3, intfName1='r1-r3', intfName2='r3-r1')
    net.addLink(r2, r3, intfName1='r2-r3', intfName2='r3-r2')

    print " *** Fix ip for  router"
    r1.cmd('ifconfig r1-h1 10.0.0.2 netmask 255.255.255.0')
    r1.cmd('ifconfig r1-r2 30.0.0.1 netmask 255.255.255.0')
    r1.cmd('ifconfig r1-r3 40.0.0.1 netmask 255.255.255.0')

    r2.cmd('ifconfig r2-h2 20.0.0.2 netmask 255.255.255.0')
    r2.cmd('ifconfig r2-r1 30.0.0.2 netmask 255.255.255.0')
    r2.cmd('ifconfig r2-r3 50.0.0.1 netmask 255.255.255.0')

    r3.cmd('ifconfig r3-r1 40.0.0.2 netmask 255.255.255.0')
    r3.cmd('ifconfig r3-r2 50.0.0.2 netmask 255.255.255.0')

    print "*** Starting network"

    net.build()

    print "*** Running CLI"

    CLI(net)

    print "*** Stopping network"

    net.stop()