#!/usr/bin/python 
import boto.ec2
import uuid 
import argparse

dev=False 

if dev:
  awspath = '/home/nigel/.aws/'
 
  

desc = 'simplified aws cli'

class Const:
  name  = 'NAME:'
  rules = 'RULES:'
  inst  = 'INSTANCE:'


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


def get_region():
  f = open(awspath+'regionstore','r')
  region = f.readline() 
  region = region.strip('\ \t\n') 
  return region 


def get_regions():
  regions =  boto.ec2.regions()
  return regions 


def conn(region=get_region()):
  con = boto.ec2.connect_to_region(region,aws_access_key_id=awskeyid,aws_secret_access_key=asak)
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
  

def list_groups():
  sg = get_secgroups(conn()) 
  for group in sg:
    print group.name


def main():
  parser = argparse.ArgumentParser(description='dude')
  parser.add_argument('-l', '--listing',      help = 'lists security groups in us-west-2', action='store_true')
  parser.add_argument('-d', '--describe',     help = 'decribe given security group',) 
  parser.add_argument('-dir','--Dir',         help = 'does a python dir() on the securitygroups object', action='store_true')
  parser.add_argument('-lr','--listregion',   help = 'list all regions', action='store_true') 
  parser.add_argument('-cr','--changeregion', help = 'changes the default region')     
  parser.add_argument('-C', '--config',       help = 'prints key elements of config', action='store_true') 

  parsed = parser.parse_args() 

  sg = get_secgroups(conn())
   
  if(parsed.listing):
    list_groups()
 
  if (parsed.describe):
     group = get_secgroup(sg,parsed.describe)
     print Const.name  + group.name   
     print Const.rules +  str(group.rules)
     print Const.inst  +  str(group.instances) 
     print group.description
     print group.rules_egress
 
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


if __name__ == '__main__': 
  main()	