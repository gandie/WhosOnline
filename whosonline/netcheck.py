#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# netcheck.py - simple module to check local network for pingable devices
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
# import os

import whosonline.logfacility as logfacility
LOGGER = logfacility.build_logger()


def notifiy(hostname, status):
    '''using notify-send shell command to visualize online status nicely'''
    cmd = ['notify-send', hostname, 'Online' if status is True else 'Offline']
    child = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    # just fire command, no response check for now
    child.communicate()


def ping(hostname):
    '''use ping shell command to determine if device behind hostname is online
    '''
    command = "ping -c 1 " + hostname
    child = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    result_text = child.communicate()[0]
    result = child.returncode
    if result == 0:
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
    network_adress = network_obj.network_address
    broadcast_address = network_obj.broadcast_address
    for address_obj in network_obj:
        if address_obj == network_adress:
            continue
        if address_obj == broadcast_address:
            continue
        yield address_obj


def netcheck_main(network):
    '''Build network object from network string and shovel ips to check
    functions
    '''
    results = {}
    # main loop
    while True:
        network_obj = ipaddress.ip_network(network, strict=True)
        for address_obj in get_ips(network_obj):
            ip_str = str(address_obj)
            hostname = get_hostname(ip_str)
            if hostname:
                last_result = results.get(hostname)
                ping_result = ping(hostname)
                # notify if status changes
                if (last_result is not None) and (last_result != ping_result):
                    notifiy(hostname, ping_result)
                results[hostname] = ping_result
                LOGGER.info('Host %s online: %s' % (hostname, ping_result))
