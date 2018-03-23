#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# netcheck.py - simple module to check local network for (ar)pingable devices
#
# Copyright (c) 2017 Lars Bergmann
#
# GNU GENERAL PUBLIC LICENSE
#    Version 3, 29 June 2007
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import ipaddress
import socket
import subprocess
import asyncio

# import os

# some hosts may not have to be checked, e.g. routers
OMIT_HOSTS = ['fritz', 'Teleball', ]


def safe_syscall(cmds, raisemode=False):
    '''Send a command and return both the return code and the output.  If
    used as a compatibility replacement for os.system(), pass
    "raisemode=True", which will mean that you don't get the return
    code, but instead an error.
    '''
    # Split command into list for safer parsing.
    if isinstance(cmds, str):
        cmds = cmds.split()

    import subprocess
    try:
        output = subprocess.check_output(cmds, stderr=subprocess.STDOUT)
        retcode = 0
    except subprocess.CalledProcessError as e:
        retcode = e.returncode
        output = e.output

    if raisemode and retcode:
        raise AssertionError("safe_syscall returned %s on %s" % (retcode, cmds))

    return retcode, output


def get_routes():
    '''
    returns list of dictionaries containing routes on system
    '''

    # route -n parsed by hand
    returncode, output = safe_syscall(['route', '-n'])
    routes_raw = output.decode('utf-8').split('\n')[2:]
    for line_raw in routes_raw:
        line = line_raw.split()
        line = [word for word in line if word]
        if not line:
            continue
        route = {
            'Destination': line[0],
            'Gateway': line[1],
            'Genmask': line[2],
            'Interface': line[-1]
        }
        yield route


def get_netdevice(network_address):
    '''get network device which is associated to the given network'''
    for route in get_routes():
        if route['Destination'] == network_address:
            return route['Interface']


def notify(head, message):
    '''using notify-send shell command to visualize online status nicely. Other
    methods of notification (e.g. mail) may be implemented here.'''
    cmd = ['notify-send', head, message]
    returncode, output = safe_syscall(cmd)


def ping(hostname):
    '''use ping shell command to determine if device behind hostname is online
    '''
    # send 5 packets and wait for a maximum of 5 seconds for the response
    command = "ping -c 5 -w 5 " + hostname
    returncode, output = safe_syscall(command.split())
    if returncode == 0:
        return True
    else:
        return False


def arping(ip_address, interface):
    '''use arping shell command to determine if device behind ip-address is
    online. sends ethernet frames which should not be dropped by firewalls.'''
    # send 5 packets and wait for a maximum of 5 seconds for the response
    command = "arping -c 5 -w 5 -I " + interface + "  " + ip_address
    returncode, output = safe_syscall(command.split())
    if returncode == 0:
        return True
    else:
        return False


def get_hostname(ip_address):
    try:
        host = socket.gethostbyaddr(ip_address)
        return host[0].split('.')[0]  # split of domain
    except socket.herror:
        return None
    except Exception:
        raise


def get_ips(network_obj):
    '''Get ip objects from network. Filter useless adresses'''
    if isinstance(network_obj, str):
        network_obj = ipaddress.ip_network(network_obj, strict=True)
    network_adress = network_obj.network_address
    broadcast_address = network_obj.broadcast_address
    for address_obj in network_obj:
        if address_obj == network_adress:
            continue
        if address_obj == broadcast_address:
            continue
        yield str(address_obj)


def get_hostnames(network_obj):
    myhost = socket.gethostname()
    for ip in get_ips(network_obj):
        host = get_hostname(ip)
        if host and host != myhost:
            yield ip, host


def netcheck_main(network):
    '''Main function of netcheck module called from executable
    '''

    # import logfacility
    # LOGGER = logfacility.build_logger()

    # save results to show notifications if something changes
    results = {}

    # set up network object and build ip strings from it using get_ips filter
    network_obj = ipaddress.ip_network(network, strict=True)
    ip_addresses = [str(address_obj) for address_obj in get_ips(network_obj)]

    # get the network device responsible for given network
    netdevice = get_netdevice(network.split('/')[0])  # cut off cidr netmask

    # get local hostname to add to OMIT_HOSTS list
    local_hostname = socket.gethostname()
    OMIT_HOSTS.append(local_hostname)

    # abort if not device can be found
    assert netdevice, "Unable to find network device belonging to network %s" % network
    print('Device associated to network %s : %s' % (network, netdevice))

    # main loop
    while True:
        for ip_str in ip_addresses:
            hostname = get_hostname(ip_str)
            if hostname and hostname not in OMIT_HOSTS:
                last_result = results.get(hostname)
                ping_result = arping(ip_str, netdevice)  # or ping(hostname)
                # notify if status changes --> DEACTIVATED!
                if (last_result is not None) and (last_result != ping_result):
                    notify(hostname, 'Online' if ping_result else 'Offline')
                # save new result
                if hostname not in results:
                    notify('New host found!', hostname)
                results[hostname] = ping_result
                # LOGGER.info('Host %s online: %s' % (hostname, ping_result))
                print('Host %s online: %s' % (hostname, ping_result))


async def netcheck_loop(network):
    '''
    ASYNC VERSION of netcheck main
    Main function of netcheck module called from executable
    '''

    # import logfacility
    # LOGGER = logfacility.build_logger()

    # save results to show notifications if something changes
    results = {}

    # set up network object and build ip strings from it using get_ips filter
    network_obj = ipaddress.ip_network(network, strict=True)
    ip_addresses = [str(address_obj) for address_obj in get_ips(network_obj)]

    # get the network device responsible for given network
    netdevice = get_netdevice(network.split('/')[0])  # cut off cidr netmask

    # get local hostname to add to OMIT_HOSTS list
    local_hostname = socket.gethostname()
    OMIT_HOSTS.append(local_hostname)

    # abort if not device can be found
    assert netdevice, "Unable to find network device belonging to network %s" % network
    print('Device associated to network %s : %s' % (network, netdevice))

    # main loop
    while True:
        for ip_str in ip_addresses:
            hostname = get_hostname(ip_str)
            if hostname and hostname not in OMIT_HOSTS:
                last_result = results.get(hostname)
                ping_result = arping(ip_str, netdevice)  # or ping(hostname)
                results[hostname] = ping_result
                print('Host %s online: %s' % (hostname, ping_result))
                await asyncio.sleep(2)
