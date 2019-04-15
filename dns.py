#!/usr/bin/python2
"""
Usage:
    dns.py [options]
    dns.py --create <hostname> <ip>
    dns.py --interface <hostname> <ifname>
    dns.py --gce

Options:
    --create        create a record with fqdn and ip
    --interface     gets the IP from the specified interface
    --gce           publish external ip from gce instance
"""

"""
dns.py simply creates a records given a fully qualified domain name and an ip
a hosted zone for the specified domain must already exist in route53.
duplicate names are not currently created.

dns.py can  be run from a remote host using the --create option
alternatively dns.py can be used on a new host at host creation time with no options
in this case dns.py will publish the hosts public interface based on the value of PUBLIC_INTERFACE
if public interface is not specified the IP of eth0 will be used.

dns.py now assumes that every server will be a member of an etc cluster and builds the required
DNS SRV records for this to be the case.

"""

import boto.route53
import socket
import fcntl
import struct
import re
import os
import subprocess
from docopt import docopt

ETCD_SERVER = '_etcd-server._tcp.'
REDACTED_DOMAIN = 'redacted.net'
ETCD_CLIENT = '_etcd-client._tcp.'
ifname = os.environ.get('PUBLIC_INTERFACE', 'eth1')
domain = os.environ['DOMAIN']
hostname = os.environ['HOSTNAME']
FQDN = '{}.{}'.format(hostname, domain)
ex_ip = os.environ['EXT_IP']

def is_valid_fqdn(fqdn):
    print fqdn
    if len(fqdn) > 255:
        return False
    if fqdn[-1] == ".":
        fqdn = fqdn[:-1]  # strip exactly one dot from the right, if present
    allowed = re.compile("(?=^.{4,253}$)(^((?!-)[a-zA-Z0-9-]{1,63}(?<!-)\.)+[a-zA-Z]{2,63}$)", re.IGNORECASE)
    return allowed.search(fqdn)


def run_local():
    fqdn = subprocess.check_output("hostname --fqdn", shell=True)
    if simple_create(fqdn, get_ip_address(ifname)):
        print "record created successfully"
    else:
        print "Dns record not created for this host"


def simple_create(fqdn, ip):
    if is_valid_fqdn(fqdn):
        domain_zone = is_domain_zone(fqdn)
        zone = domain_zone[0]
        conn = domain_zone[1]
        if zone is None:
            print "hosted zone does not exist"
            return False
        else:
            arecord = zone.get_a(fqdn, all=False)
            if arecord:
                zone.update_a(arecord.name, ip)
                print "a DNS record was updated"
            else:
                print zone.get_a(fqdn, all=False)
                zone.add_a(fqdn, ip, ttl=60)

                return True
    else:
        print "this is not a valid fqdn"
        return False


def is_domain_zone(fqdn):
    conn = boto.route53.connect_to_region('us-west-2')
    zone=None
    fqdnl = fqdn.split(".")
    domain = fqdnl[len(fqdnl)-2] + '.' + fqdnl[len(fqdnl)-1]
    zone = conn.get_zone(domain)
    return zone, conn


def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15])
        )[20:24])
    except IOError:
        print "no dns name was created"

def main():
    args = docopt(__doc__, version="dns.py 1.0")

    if args['--create']:
        fqdn = args['<hostname>']
        ip = args['<ip>']
        simple_create(fqdn, ip)

    if args['--gce']:
        simple_create(FQDN, ex_ip)

    if args['--interface']:
        fqdn = args['<hostname>']
        ip = get_ip_address(args['<ifname>'])
        simple_create(fqdn, ip)

    else:
        run_local()

if __name__ == '__main__':
    main()
