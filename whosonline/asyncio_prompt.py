#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
(Python >= 3.5)
This is an example of how to prompt inside an application that uses the asyncio
eventloop. The ``prompt_toolkit`` library will make sure that when other
coroutines are writing to stdout, they write above the prompt, not destroying
the input line.
This example does several things:
    1. It starts a simple coroutine, printing a counter to stdout every second.
    2. It starts a simple input/echo app loop which reads from stdin.
Very important is the following patch. If you are passing stdin by reference to
other parts of the code, make sure that this patch is applied as early as
possible. ::
    sys.stdout = app.stdout_proxy()
"""

from prompt_toolkit.shortcuts import Prompt
from prompt_toolkit.eventloop.defaults import use_asyncio_event_loop
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit import print_formatted_text
from prompt_toolkit.contrib.completers import WordCompleter

import asyncio
import pprint
import random
import time
import requests
import webcolors

import whosonline.netcheck as netcheck

whosonline_completer = WordCompleter(
    words=[
        'exit', 'hosts', 'nmap', 'stop', 'annoy_calendar', 'os',
        'services', 'all', 'fast_nmap_loop', 'spawn_kevin',
        'netcheck', 'probe'
    ],
    ignore_case=True
)

NETWORK = '192.168.88.0/24'


welcome = '''
                   :                                 :
                 :                                   :
                 :  RRVIttIti+==iiii++iii++=;:,       :
                 : IBMMMMWWWWMMMMMBXXVVYYIi=;:,        :
                 : tBBMMMWWWMMMMMMBXXXVYIti;;;:,,      :
                 t YXIXBMMWMMBMBBRXVIi+==;::;::::       ,
                ;t IVYt+=+iIIVMBYi=:,,,=i+=;:::::,      ;;
                YX=YVIt+=,,:=VWBt;::::=,,:::;;;:;:     ;;;
                VMiXRttItIVRBBWRi:.tXXVVYItiIi==;:   ;;;;
                =XIBWMMMBBBMRMBXi;,tXXRRXXXVYYt+;;: ;;;;;
                 =iBWWMMBBMBBWBY;;;,YXRRRRXXVIi;;;:;,;;;=
                  iXMMMMMWWBMWMY+;=+IXRRXXVYIi;:;;:,,;;=
                  iBRBBMMMMYYXV+:,:;+XRXXVIt+;;:;++::;;;
                  =MRRRBMMBBYtt;::::;+VXVIi=;;;:;=+;;;;=
                   XBRBBBBBMMBRRVItttYYYYt=;;;;;;==:;=
                    VRRRRRBRRRRXRVYYIttiti=::;:::=;=
                     YRRRRXXVIIYIiitt+++ii=:;:::;==
                     +XRRXIIIIYVVI;i+=;=tt=;::::;:;
                      tRRXXVYti++==;;;=iYt;:::::,;;
                       IXRRXVVVVYYItiitIIi=:::;,::;
                        tVXRRRBBRXVYYYIti;::::,::::
                         YVYVYYYYYItti+=:,,,,,:::::;
                         YRVI+==;;;;;:,,,,,,,:::::::

         "From great power comes great responsibility."  -- Mr. Spock


WhosOnline -- interactive wrapper arround nmap and other fun stuff
'''


async def syscall(command, debug=False):

    if isinstance(command, str):
        command = command.split()

    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE
    )

    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()

    if debug and process.returncode != 0:
        print('Failed: (pid = ' + str(process.pid) + ')')

    result = stdout.decode().strip()

    return process.returncode, result


async def nmap_scan(ip, mode='-F'):

    result_d = {'ports': []}
    cmd = ['nmap', ip, mode]
    retcode, result = await syscall(cmd)
    result = result.split('\n')

    # parse nmap result
    for line in result:
        if 'Host is up' in line:
            result_d['online'] = True
            continue
        elif 'Host seems down' in line:
            result_d['online'] = False
            break
        if line and line[0].isdigit() and mode != '-sV':
            port, state, service = line.split()
            port_d = {
                'port': port,
                'state': state,
                'service': service
            }
            result_d['ports'].append(port_d)
        if line and line[0].isdigit() and mode == '-sV':
            port, state, service, *version = line.split()
            port_d = {
                'port': port,
                'state': state,
                'service': service,
                'version': ' '.join(version)
            }
            result_d['ports'].append(port_d)
        if line.startswith('Running:'):
            result_d['OS'] = line.split(': ')[1]
        if line.startswith('MAC Address:'):
            result_d['MAC'] = line.split(': ')[1]

    return result_d


async def scan_host_os(hostname):
    scan_result = await nmap_scan(ip=hostname, mode='-O')
    print()
    print('OS SCAN')
    print('HOST %s SCANNED, RESULT FOLLOWS:' % hostname)
    print(pprint.pformat(scan_result))
    print()


async def scan_host_services(hostname):
    scan_result = await nmap_scan(ip=hostname, mode='-sV')
    print()
    print('SERVICES SCAN')
    print('HOST %s SCANNED, RESULT FOLLOWS:' % hostname)
    print(pprint.pformat(scan_result))
    print()


async def probe_host(hostname):
    scan_result = await nmap_scan(ip=hostname, mode='-PN')
    print()
    print('PROBING HOST SCAN')
    print('HOST %s SCANNED, RESULT FOLLOWS:' % hostname)
    print(pprint.pformat(scan_result))
    print()


async def nmap_scan_loop(network):
    """
    Coroutine calling fast nmap scan for all known hosts
    """
    while True:
        ip_hosts = await get_hosts(network)
        print('%s hosts in network %s' % (len(ip_hosts), network))
        for ip, host_d in ip_hosts.items():
            scan_result = await nmap_scan(ip)
            print()
            print('HOST %s SCANNED, RESULT FOLLOWS:' % host_d['hostname'])
            print(pprint.pformat(scan_result))
            print()
            online = scan_result['online']
            # print('%s online: %s' % (host_d['hostname'], online))
            ports = scan_result['ports']
            # for port_d in ports:
            # print(port_d)
            await asyncio.sleep(1)

        await asyncio.sleep(3)


async def arping(ip, interface, timeout=3, frame_count=3):

    command = 'arping -f -c {frame_count} -w {timeout} -I {interface} {ip}'.format(
        frame_count=frame_count,
        timeout=timeout,
        interface=interface,
        ip=ip
    )

    retcode, output = await syscall(command.split())

    if retcode == 0:
        return True
    else:
        return False


async def netcheck_loop(hosts_d, interface):
    while True:
        for ip in hosts_d:
            hostname = hosts_d[ip]
            ping_result = await arping(ip, interface)  # or ping(hostname)
            print()
            print('Host %s online: %s' % (hostname, ping_result))
            print()
            await asyncio.sleep(1)


async def get_hosts(network):
    hosts = dict(
        (ip, {'hostname': hostname}) for ip, hostname in netcheck.get_hostnames(network)
    )
    return hosts


async def interactive_shell(loop, network, hosts_d, interface):
    """
    """
    # Create Prompt.
    prompt = Prompt(
        [('ansicyan', '(WhosOnline)>>> ')],
        completer=whosonline_completer
    )

    done = False
    # Patch stdout in something that will always print *above* the prompt when
    # something is written to stdout.
    # (This is optional, when `patch_stdout=True` has been given before.)

    # sys.stdout = prompt.app.stdout_proxy()
    ip_hosts = {}
    tasks = {}

    fancy_print(welcome, color='ansigreen')

    while not done:
        try:
            result = await prompt.prompt(async_=True)
            if result == 'exit':
                fancy_print('Exiting shell, aborting tasks...')
                done = True
            elif result == 'spawn_kevin':
                fancy_print('Spawning kevin...')
                tasks['spawn_kevin'] = asyncio.gather(
                    spawn_kevin(),
                    return_exceptions=True
                )
            elif result == 'netcheck':
                fancy_print('Starting netcheck loop...')
                tasks['netcheck'] = asyncio.gather(
                    netcheck_loop(hosts_d, interface)
                )
            elif result.startswith('stop'):
                command = result.split()
                if len(command) != 2:
                    fancy_print('Type "stop <TASK_NAME>|all"', color='ansired')
                    continue
                if command[1] != 'all' and command[1] not in tasks:
                    fancy_print('Task not found', color='ansired')
                    continue
                if command[1] == 'all':
                    for task in tasks:
                        fancy_print('Canceling task %s...' % task)
                        tasks[task].cancel()
                    tasks = {}
                else:
                    fancy_print('Canceling task %s...' % command[1])
                    tasks[command[1]].cancel()
                    tasks.pop(command[1])
            elif result == 'fast_nmap_loop':
                if result in tasks:
                    fancy_print('Task allready running', color='ansired')
                    continue
                fancy_print('Sheduling fast_nmap_loop to check for hosts online/offline')
                tasks['fast_nmap_loop'] = asyncio.gather(
                    nmap_scan_loop(network)
                    # return_exceptions=True
                )
            elif result == 'annoy_calendar':
                if result in tasks:
                    fancy_print('Task allready running', color='ansired')
                    continue
                fancy_print('Starting to annoy calendar...')
                tasks['annoy_calendar'] = asyncio.gather(annoy_calendar())
            elif result.startswith('nmap os'):
                command = result.split()
                if len(command) != 3:
                    fancy_print('Type "nmap os <HOSTNAME>"', color='ansired')
                    continue
                host = command[-1]
                os_scan_task = asyncio.gather(scan_host_os(host))
                fancy_print('OS scan on host %s sheduled, expect results...' % host)
            elif result.startswith('nmap services'):
                command = result.split()
                if len(command) != 3:
                    fancy_print('Type "nmap services <HOSTNAME>"', color='ansired')
                    continue
                host = command[-1]
                os_scan_task = asyncio.gather(scan_host_services(host))
                fancy_print('Services scan on host %s sheduled, expect results...' % host)
            elif result.startswith('nmap probe'):
                command = result.split()
                if len(command) != 3:
                    fancy_print('Type "nmap probe <HOSTNAME>"', color='ansired')
                    continue
                host = command[-1]
                os_scan_task = asyncio.gather(probe_host(host))
                fancy_print('Probing scan on host %s sheduled, expect results...' % host)


        except (EOFError, KeyboardInterrupt):
            for task in tasks.values():
                task.cancel()
            return

    for task in tasks.values():
        task.cancel()

    loop.stop()


def fancy_print(text, color='ansiyellow'):
    print_formatted_text(FormattedText([(color, '\n' + text)]))


def main(network):
    # Tell prompt_toolkit to use the asyncio event loop.
    try:
        with patch_stdout():

            loop = asyncio.get_event_loop()
            use_asyncio_event_loop()

            interface = netcheck.get_netdevice(network.split('/')[0])  # cut off cidr netmask

            # SETUP SHELL
            # add hostnames add completer
            hosts_d = {
                ip: hostname for ip, hostname in netcheck.get_hostnames(network)
            }
            whosonline_completer.words += list(hosts_d.values())

            # start shell
            shell_task = asyncio.ensure_future(
                interactive_shell(loop, network, hosts_d, interface)
            )
            loop.run_until_complete(shell_task)
    except Exception as e:
        print(e)
        # pass  # stfu


if __name__ == '__main__':
    main(NETWORK)
