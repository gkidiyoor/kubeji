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
	else:
		printit("** No pre setup")	

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
		printit("** No main")

def post(config):
	printit("** Exc post setup")
	if config != None:
		pass
	else:
		pass

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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create kubernetes cluster')
    parser.add_argument('layoutFile', type=str, help=': Path to the layout file')
    args = parser.parse_args()
    layout = get_layout(args.layoutFile)
    
    #TODO
    # validation of layout file should be done

    if 'pre' in layout[0].keys():
    	pre(layout[0]['pre'])	
    else:
    	sys.exit(0)

    if 'main' in layout[1].keys():
    	main(layout[1]['main'])	
    else:
    	sys.exit(0)

    if 'post' in layout[2].keys():
    	post(layout[2]['post'])	
    else:
    	sys.exit(0)
