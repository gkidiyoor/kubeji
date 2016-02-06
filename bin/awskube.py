import yaml
import argparse
import sys
import subprocess
import json
import termcolor

#require dpath , pip install dpath
import dpath
#require dpath , pip install jinja2
import jinja2

#TODO use environment variables for path 

extracted = {}

def printit(s):
	print(termcolor.colored(s,'red',attrs=['bold']))

def get_layout(f):
	f = open(f,'r')
	data = yaml.load(f)
	return data

def pre(config):
	printit("** Exc pre setup")
	if config != None:
		if 'create_key_pair' in config.keys():
			create_key_pairs(config['create_key_pair'])
		if 'create_security_group' in config.keys():
			create_security_groups(config['create_security_group'])
		if 'create_load_balancer' in config.keys():
			create_load_balancer(config['create_load_balancer'])
	else:
		printit("** No pre tasks")	

def main(config):
	if config != None:
		printit("** Exc main")
		for dobj in config:
			if type(dobj['user_data']) is dict	:
				user_d = open(dobj['user_data']['file'],'r')
				template = jinja2.Template(user_d.read())
				user_data =template.render(extracted)
				user_d.close()
				#TODO create this fine oi cloud config
				new_t = open("temp.yaml","w")
				new_t.write(user_data)
				new_t.close()

				dobj['user_data'] = "file://temp.yaml"
			
			#aws ec2 run-instances --image-id ami-0006dd68 --key-name kubernetes-key --region us-east-1 --security-groups kubernetes --instance-type t2.micro --user-data master.yaml > master-created.json
			inst_data_string = subprocess.check_output(["aws","ec2","run-instances","--image-id",dobj['image_id'],"--key-name",dobj['key_name'],"--region",dobj['region'],"--security-groups",dobj['security_group'],"--instance-type",dobj['instance_type'],"--user-data",dobj['user_data']])
			print(inst_data_string)
			inst_data = json.loads(inst_data_string)
			if 'extract' in dobj.keys():
				for e in dobj['extract']:
					extracted[e.keys()[0]]=dpath.util.get(inst_data, e[e.keys()[0]])
				printit("Extracted data : " + str(extracted))


	else:
		printit("** No main tasks")

def post(config):
	printit("** Exc post setup")
	if config != None:
		if 'register_instance_with_load_balancer' in config.keys():
			register_instance_with_load_balancer(config['register_instance_with_load_balancer'])
		if 'tag_resources' in config.keys():
			tag_resources(config['tag_resources'])
	else:
		printit("** No post tasks")


def create_key_pairs(config):
	printit("\t** Creating key-pair")
	for dobj in config:
		key_val = subprocess.check_output(["aws","ec2","create-key-pair","--key-name",dobj['name'],"--region",dobj['region'],"--query","KeyMaterial", "--output","text"])
		f = open(dobj['name']+".pem",'w')
		f.write(key_val)
		f.close()
		subprocess.call(["sudo","chmod","400",dobj['name']+".pem"])
		

def create_security_groups(config):
	printit("\t** Creating security groups")
	for dobj in config:
		#aws ec2 create-security-group --group-name kubernetes --description "Kubernetes Security Group"
		print(subprocess.check_output(["aws","ec2","create-security-group","--group-name",dobj['name'],"--description",dobj['description'],"--region",dobj['region']]))
		for port in dobj['ingress']:
			#aws ec2 authorize-security-group-ingress --group-name kubernetes --protocol tcp --port 22 --cidr 0.0.0.0/0
			print(subprocess.check_output(["aws","ec2","authorize-security-group-ingress","--group-name", dobj['name'],"--protocol","tcp","--port",str(port),"--cidr","0.0.0.0/0","--region",dobj['region']]))
		#aws ec2 authorize-security-group-ingress --group-name kubernetes --source-security-group-name kubernetes
		print(subprocess.check_output(["aws","ec2","authorize-security-group-ingress","--group-name", dobj['name'],"--source-security-group-name",dobj['name'],"--region",dobj['region']]))

def create_load_balancer(config):
	printit("\t** Creating load balancer")
	for dobj in config:
		l = ["aws","elb","create-load-balancer","--load-balancer-name",dobj['name'],"--listeners",dobj['listeners'],"--region", dobj['region'],"--availability-zones"]
		for i in dobj['availability_zones']:
			l.append(i)
		#aws elb create-load-balancer --load-balancer-name my-load-balancer --listeners "Protocol=HTTP,LoadBalancerPort=80,InstanceProtocol=HTTP,InstancePort=80" --subnets subnet-15aaab61 --security-groups sg-a61988c3
		output = subprocess.check_output(l)
		print(output)
		extracted['lb_url'] = dpath.util.get(json.loads(output), '/DNSName')

		
def register_instance_with_load_balancer(config):
	printit("\t** Attaching instances with load balancer")
 	for dobj in config:
	 	for i in dobj['instances']:
 		 	#aws elb register-instances-with-load-balancer --load-balancer-name my-load-balancer --instances i-d6f6fae3
 		 	print(subprocess.check_output(["aws","elb","register-instances-with-load-balancer","--load-balancer-name",dobj['name'],"--instances",extracted[i]]))


def tag_resources(config):
	printit("\t** Tagging resources")
	for dobj in config:
		#aws ec2 create-tags --resources ami-78a54011 --tags Key=Stack,Value=production  
		for i in dobj['tags']:
			print(subprocess.check_output(["aws","ec2","create-tags","--resources",extracted[dobj['id']],'--tags',i]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create kubernetes cluster')
    parser.add_argument('layoutFile', type=str, help=': Path to the layout file')
    args = parser.parse_args()
    layout = get_layout(args.layoutFile)
    
    #TODO
    # validation of layout file should be done


    if 'vars' in layout[0].keys():
    	for i in layout[0]['vars']:
    		extracted[i.keys()[0]]=i[i.keys()[0]]
    else:
    	print("var section not found, clue: have a empty var section")
    	sys.exit(0)

    if 'pre' in layout[1].keys():
    	pre(layout[1]['pre'])	
    	pass
    else:
    	print("pre section not found, clue: have a empty var section")
    	sys.exit(0)

    if 'main' in layout[2].keys():
    	main(layout[2]['main'])	
    	pass
    else:
    	print("main section not found, clue: have a empty var section")
    	sys.exit(0)

    if 'post' in layout[3].keys():
    	post(layout[3]['post'])
    else:
    	print("main section not found, clue: have a empty var section")
    	sys.exit(0)
    
    #For dangling else
    if(True):
    	pass

	print(termcolor.colored("** Completed **",'green',attrs=['bold']))


