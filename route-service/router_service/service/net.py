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
    h3 = net.addHost('h3', ip='30.0.0.1/24')
    h4 = net.addHost('h4', ip='40.0.0.1/24')
    h5 = net.addHost('h5', ip='50.0.0.1/24')
    print "*** Creating router node"
    r1 = net.addHost('r1', ip='10.0.0.2/24')
    r2 = net.addHost('r2', ip='20.0.0.2/24')

    print "*** Creating links"
    net.addLink(h1, r1, intfName1='h1-r1', intfName2='r1-h1')
    net.addLink(h2, r1, intfName1='h2-r1', intfName2='r1-h2')
    net.addLink(h3, r1, intfName1='h3-r1', intfName2='r1-h3')
    net.addLink(h4, r2, intfName1='h4-r2', intfName2='r2-h4')
    net.addLink(h5, r2, intfName1='h5-r2', intfName2='r2-h5')
    net.addLink(r2, r1, intfName1='r2-r1', intfName2='r1-r2')

    print " *** Fix ip for  router"
    r1.cmd('ifconfig r1-h1 10.0.0.2 netmask 255.255.255.0')
    r1.cmd('ifconfig r1-h2 20.0.0.2 netmask 255.255.255.0')
    r1.cmd('ifconfig r1-h3 30.0.0.2 netmask 255.255.255.0')
    r2.cmd('ifconfig r2-h4 40.0.0.2 netmask 255.255.255.0')
    r2.cmd('ifconfig r2-h5 50.0.0.2 netmask 255.255.255.0')

    r2.cmd('ifconfig r2-r1 60.0.0.1 netmask 255.255.255.0')
    r1.cmd('ifconfig r1-r2 60.0.0.2 netmask 255.255.255.0')
    print "*** Starting network"

    net.build()

    print "*** Running CLI"

    CLI(net)

    print "*** Stopping network"

    net.stop()
