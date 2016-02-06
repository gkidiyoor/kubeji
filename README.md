# kubernetes-aws-launch-cluster
Learn to set up kubernetes cluster on aws.

Dependencies:
- AWS CLI
- Python2.7
- Python jinja2, dpath,pyyaml,termcolor module

This is a wrapper around AWS CLI that allow you to write a configuration YAML file for set up a kubernetes cluster from local command line.
It has features to 
- create key-pair
- create security groups
- extract variable from AWS-CLI output and use them in next instance launch(uses jinja2 syntax, very useful for static configuration)

Sample config file :
```
---
- pre:
    create_key_pair:
      - name: kubernetes_test_3
        region: "us-east-1"
    create_security_group:
      - name: kubernetes_test_2
        description: "For test"
        region: "us-east-1"
        ingress:
          - 22
          - 80
          - 4500
    
- main:
  - name: "master"
    image_id: "ami-0006dd68"
    key_name: "kubernetes_test_3" 
    region: "us-east-1"
    security_group: "kubernetes_test_2"
    instance_type: "t2.micro"
    user_data: "file://../cloud_config/sample.yaml" #file:// imp
    extract:
      - master_ip: "Instances/0/PrivateIpAddress" # JSON path to extract IP from AWS CLI output

  - name: slave
    user_data: 
      file: "../cloud_config/sample.yaml" # use the extracted variable using jinja2 syntax # do not use file://
      type: "yaml"
    image_id: "ami-0006dd68"
    key_name: "kubernetes_test_3" 
    region: "us-east-1"
    security_group: "kubernetes_test_2"
    instance_type: "t2.micro"


- post:

```
How to run ?
Set ENV for access key and AWS secret
```
 cd bin
 python awskube.py "../layout/kube_t.yaml"
```
 


