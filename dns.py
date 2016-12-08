#!/usr/bin/python2
"""
Usage:
    dns.py [options]
    dns.py --create <hostname> <ip>

Options:
    --create    create a record with fqdn and ip
"""

"""
dns.py simply creates a records given a fully qualified domain name and an ip
a hosted zone for the specified domain must already exist in route53.
duplicate names are not currently created.

dns.py can  be run from a remote host using the --create option
alternatively dns.py can be used on a new host at host creation time with no options
in this case dns.py will publish the hosts public interface based on the value of PUBLIC_INTERFACE
if public interface is not specified the IP of eth0 will be used.
"""

import boto.route53
import socket
import fcntl
import struct
import re
import os
import subprocess
from docopt import docopt


def is_valid_fqdn(fqdn):
    if len(fqdn) > 255:
        return False
    if fqdn[-1] == ".":
        fqdn = fqdn[:-1]  # strip exactly one dot from the right, if presentasdf
    allowed = re.compile("(?=^.{4,253}$)(^((?!-)[a-zA-Z0-9-]{1,63}(?<!-)\.)+[a-zA-Z]{2,63}$)", re.IGNORECASE)
    if allowed.search(fqdn):
        return True
    else:
        return False


def run_local():
    fqdn = subprocess.check_output("hostname --fqdn", shell=True)
    if is_valid_fqdn(fqdn):
        if simple_create(fqdn, get_ip_address()):
            print "record created successfully"
        else:
            print "Dns record not created for this host"
    else:
        print "this host does not have a valid fqdn DNS records will not be created"


def simple_create(fqdn, ip):
    if is_valid_fqdn(fqdn):
        zone = is_domain_zone(fqdn)
        if zone is None:
            print "hosted zone does not exist"
        else:
            arecord = zone.get_a(fqdn, all=False)
            if arecord:
                print "record already exists"
                return False
            else:
                print zone.get_a(fqdn, all=False)
                zone.add_a(fqdn, ip, ttl=60)
                return True
    else:
        print "this is not a valid fqdn"


def is_domain_zone(fqdn):
    conn = boto.route53.connect_to_region('us-west-2')
    zone=None
    fqdnl = fqdn.split(".")
    domain = fqdnl[len(fqdnl)-2] + '.' + fqdnl[len(fqdnl)-1]
    zone = conn.get_zone(domain)
    return zone


def get_ip_address():
    try:
        ifname = os.environ['PUBLIC_INTERFACE']
    except KeyError:
        ifname = 'eth0'

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])


def main():
    args = docopt(__doc__, version="dns.py 1.0")

    if args['--create']:
        fqdn = args['<hostname>']
        ip = args['<ip>']
        simple_create(fqdn, ip)

    else:
        run_local()

if __name__ == '__main__':
    main()
