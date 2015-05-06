#!/usr/bin/python
#for a simple comparison of security groups rules
import argparse 

def create_list(path_to_file): 
    rule_list = []
    f = open(path_to_file) 
    for line in f:
        rule_list.append(line)    

    return rule_list  

def compare(good_rule_list,test_rule_list,list_name): 
    for rule in good_rule_list:
        for test_rule in test_rule_list:
            if rule == test_rule:
                break
        else:
            print rule.rstrip('\n') + "," + list_name

def main():
    parser = argparse.ArgumentParser(description='basic compare') 
    parser.add_argument('filename', nargs=2)
    parsed = parser.parse_args() 
    
    if parsed.filename:
        first_file = parsed.filename[0] 
        second_file = parsed.filename[1]
        
         
        good_rule_list = create_list(first_file)
        test_rule_list = create_list(second_file)	
     
        compare(good_rule_list, test_rule_list, parsed.filename[1])
        compare(test_rule_list, good_rule_list, parsed.filename[0])
                     

if __name__ == '__main__':
    main()



