#!/usr/bin/python 
import boto.ec2
import uuid 
import argparse

dev=False 

if dev:
  awspath = '/Users/nigeldaniels/'
else:
  awspath ='/Users/nigeldaniels/.aws/'

desc = 'simplified aws cli'

class Const:
  name  = 'NAME:'
  rules = 'RULES:'
  inst  = 'INSTANCE:'
  coma  = ','
def read_configs():
  
  f = open(awspath+'credentials','r')
  for line in f:
    if "aws_access_key_id" in line:
      line = line.split('=')
      awskeyid = line[1].strip(' \t\n') 
    
    if "aws_secret_access_key" in line: 
      line = line.split('=') 
      asak = line[1].strip(' \t\n') 

  aws_creds = [awskeyid, asak]
  return aws_creds

aws_creds = read_configs()
awskeyid = aws_creds[0]
asak = aws_creds[1]

def store_region(region):
  f = open(awspath+'regionstore','w+')
  f.write(region)
  f.close()

def get_region():
  f = open(awspath+'regionstore','r')
  region = f.readline() 
  region = region.strip('\ \t\n') 
  f.close()
  return region 

def get_regions():
  regions =  boto.ec2.regions()
  return regions 


def conn(region=get_region()):
  con = boto.ec2.connect_to_region(region,aws_access_key_id=awskeyid,aws_secret_access_key=asak)
  print "REGIONIS:" + region
  return con 


def get_secgroups(con):
  security_groups = con.get_all_security_groups()
  return security_groups


def get_secgroup(sg,name):
  for group in sg:
    if (group.name == name):
      return group 


def describe_sg(group):
  name = group.name 
  #description = group.description
  rules = group.rules 
  instances = group.instances
  item = group.item
  name = group.name
  

def list_groups(p):
  sg = get_secgroups(conn()) 
  for group in sg:
    if p == 'true':
        print group.name
  return sg
  
def list_instances(con):
   reservations = con.get_all_reservations()
   return reservations  


def is_ip(ip):
    if str(ip).startswith('s'):
        return False
    else:
        return True

def get_secgroup_name(id,con):

    list = [str(id)[:11]]
    group = con.get_all_security_groups(group_ids=list)
    return str(group)


def full_report():
    x=0 
    regions = get_regions()
 
    for region in regions:
        store_region(region.name)
    	print region.name
        secgroups_list = report()     
        f = open(region.name,'w') 
        for line in secgroups_list: 
            f.write(line+'\n') 
           
def report():
 # print get_region()
  report =[]  
  
  sg = list_groups('true')
  for secgroup in sg:
     for rule in secgroup.rules:
         for ip in rule.grants:
            if is_ip(ip):
                output1 = str(secgroup.name) + Const.coma + str(rule.ip_protocol) + Const.coma + str(rule.from_port) + Const.coma + str(ip)
#                print output1 
                report.append(output1) 
            else:
                ip = get_secgroup_name(ip, conn())
                ip = ip.split(':')[1].strip(']')
                output2 = str(secgroup.name) + Const.coma + str(rule.ip_protocol) + Const.coma + str(rule.from_port) + Const.coma + ip
                report.append(output2)
  return report

def main():
  parser = argparse.ArgumentParser(description='dude')
  parser.add_argument('-l', '--listing',      help = 'lists security groups in us-west-2', action='store_true')
  parser.add_argument('-d', '--describe',     help = 'decribe given security group',) 
  parser.add_argument('-dir', '--Dir',        help = 'does a python dir() on the securitygroups object', action='store_true')
  parser.add_argument('-lr', '--listregion',  help = 'list all regions', action='store_true')
  parser.add_argument('-cr', '--changeregion',help = 'changes the default region')
  parser.add_argument('-C',  '--config',      help = 'prints key elements of config', action='store_true')
  parser.add_argument('-li', '--instances',   help = 'lists instances in the current region', action='store_true')
  parser.add_argument('-r',  '--report',    help = 'lists instances in the current region', action='store_true')
  parser.add_argument('-g',   '--group2name', help =  'converts a security group id to a name ')
  parsed = parser.parse_args()

  #@g = get_secgroups(conn())

  if parsed.group2name:
      ass = get_secgroup_name(parsed.group2name, conn())
      print ass

  if(parsed.report):
      full_report()    
 
  if(parsed.listing):
    list_groups('true')
 
  if (parsed.describe):
     group = get_secgroup(sg,parsed.describe)
     print Const.name + group.name
     print Const.rules + str(group.rules)
     print Const.rules + str(group.egress_rules[0].ip_protocol)
     print Const.inst + str(group.instances)
     print group.description
     print group.rules_egress
     print str(group)
 
  if (parsed.Dir):
    print str(dir(sg[1])) + "\n\n"
    print dir(sg[1].rules)  
  
  if (parsed.listregion):
     regions =  get_regions()
     for region in regions:
       print region.name

  if (parsed.config):
    aws_creds =  read_configs()

  if (parsed.changeregion):
    store_region(parsed.changeregion) 

  if (parsed.instances):
    instances = list_instances(conn())
    for instance[1] in instances:
      print str(instance.dir())   
 
if __name__ == '__main__': 
  main()	
